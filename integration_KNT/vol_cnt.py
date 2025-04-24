import open3d as o3d
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json
import os

class ObjBox:
    def __init__(self, length:float, width:float, height:float):
        self.length = length
        self.width  = width
        self.height = height
    def get_vol(self) -> float:
        return self.length * self.width * self.height
    
class ROIbg:
    def __init__(self, y:float, x_left:float, x_right:float, z_down:float, z_up:float):
        self.y       = y
        self.x_left  = x_left
        self.x_right = x_right
        self.z_down  = z_down
        self.z_up    = z_up
    
class VolCnt():
    def __init__(self, batch_num:int):
        self.cnt_list   = []
        self.cnt_signal = None
        self.batch_num  = batch_num
    
    def compute_integrated_volume(self, input_file:str, reference:float) -> float:
        # 读取点云文件
        pcd = o3d.io.read_point_cloud(input_file)
        # 提取点云的XYZ坐标
        points = np.asarray(pcd.points)
        # 使用k近邻算法计算每个点的邻近点，找到横向最小距离
        nbrs = NearestNeighbors(n_neighbors=10, algorithm='ball_tree').fit(points[:, [0, 2]])
        distances, _ = nbrs.kneighbors(points[:, [0, 2]])  # 计算XZ平面距离
        # 初始化体积变量
        total_volume = 0.0
        # 对每个点计算微小体积并累加
        for i in range(len(points)):
            L     = (distances[i, 3] + distances[i, 4])/2  # 选择除自身以外次小的横向距离 最小的疑似太小使得结果偏小
            depth = reference - points[i, 1] # 当前点到参考平面的距离
            # 微小体积计算：L^2 * z
            volume_i      = L**2 * depth
            total_volume += volume_i
        return total_volume

    def update_cntlist(self):
        if self.cnt_signal:
            self.cnt_signal.emit(self.cnt_list)

    def run(self):
        print('Hello from volume cnt')
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        ply_folder = config['ply_folder']
        roi = ROIbg(y       = config["roi"]["y"], 
                    x_left  = config["roi"]["x_left"],
                    x_right = config["roi"]["x_right"],
                    z_down  = config["roi"]["z_down"],
                    z_up    = config["roi"]["z_up"])
        objbox = ObjBox(length = config["boxsz"]["length"],
                        width  = config["boxsz"]["width"],
                        height = config["boxsz"]["height"])
        ftdfiles   = [file for file in os.listdir(ply_folder) if file.startswith('ftd')]
        input_file = os.path.join(ply_folder, ftdfiles[self.batch_num])
        real_vol   = objbox.get_vol()
        volume     = self.compute_integrated_volume(input_file, reference=roi.y)
        cnt        = volume/real_vol
        self.cnt_list.append(round(cnt))
        self.update_cntlist()
        print(f'{os.path.basename(input_file)} // real_cnt={cnt:.3f}')
        print('Count Done!')

if __name__ == "__main__":
    vc = VolCnt(batch_num=0)
    vc.run()
