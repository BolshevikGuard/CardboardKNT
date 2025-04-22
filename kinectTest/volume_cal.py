import open3d as o3d
import numpy as np
from sklearn.neighbors import NearestNeighbors

def compute_integrated_volume(input_file, reference):
    
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
        L = distances[i, 2]  # 选择除自身以外次小的横向距离 最小的疑似太小使得结果偏小
        depth = reference - points[i, 1] # 当前点到参考平面的距离
        
        # 微小体积计算：L^2 * z
        volume_i = L**2 * depth
        total_volume += volume_i
    
    return total_volume

class ObjBox:
    def __init__(self, length:float, width:float, height:float):
        self.length = length
        self.width = width
        self.height = height
    def get_vol(self):
        return self.length * self.width * self.height

# 示例调用
input_file = "modelsout/ftd_hello2.ply"  # 输入点云文件
reference = 2000
volume = compute_integrated_volume(input_file, reference=reference)
print(f"volume: {volume:.3e} mm3 aka {volume/1e9:.3f} m3")

objbox = ObjBox(length=700, width=380, height=520)
real_vol = objbox.get_vol()
print(f'{real_vol=:.3e} mm3')
print(f'boxs cnt: {(volume/real_vol):.3f} => {round(volume/real_vol)}')