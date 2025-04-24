import open3d as o3d
import numpy as np
import json
import os

class ROIbg:
    def __init__(self, y:float, x_left:float, x_right:float, z_down:float, z_up:float):
        self.y       = y
        self.x_left  = x_left
        self.x_right = x_right
        self.z_down  = z_down
        self.z_up    = z_up

def get_batch_num_max() -> int:
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    ply_folder = config['ply_folder']
    return sum(1 for file in os.listdir(ply_folder) if file.endswith('png'))

class FilterProc():
    def __init__(self):
        pass

    def roi_filter(self, input_file:str, output_file:str, voxel_sz:float, roi:ROIbg, nb:int, std_r:float):
        pcd = o3d.io.read_point_cloud(input_file)
        print(f"读取点云 {os.path.basename(input_file)} 点数 {len(pcd.points)}")

        # 体素下采样
        pcd = pcd.voxel_down_sample(voxel_sz)
        # print(f'体素下采样后点数 {len(pcd.points)}')

        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors)

        ft = (points[:, 1]<=roi.y) & (points[:, 0]>=roi.x_left) & (points[:, 0]<=roi.x_right) & (points[:, 2]>=roi.z_down) & (points[:, 2]<=roi.z_up)
        filtered_pts = points[ft]
        filtered_cls = colors[ft]
        filtered_pcd = o3d.geometry.PointCloud()
        filtered_pcd.points = o3d.utility.Vector3dVector(filtered_pts)
        filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_cls)
        print(f'ROI滤除后点数 {len(filtered_pcd.points)}')

        filtered_pcd, _ = filtered_pcd.remove_statistical_outlier(nb_neighbors=nb, std_ratio=std_r)
        print(f"杂点滤除点数 {len(filtered_pcd.points)}")

        o3d.io.write_point_cloud(output_file, filtered_pcd, write_ascii=True)
        
    def run(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        ply_folder = config['ply_folder']
        roi = ROIbg(y       = config["roi"]["y"], 
                    x_left  = config["roi"]["x_left"],
                    x_right = config["roi"]["x_right"],
                    z_down  = config["roi"]["z_down"],
                    z_up    = config["roi"]["z_up"])
        voxel_size = 0.01

        for filename in os.listdir(ply_folder):
            if str(filename).endswith('ply') and not str(filename).startswith('ftd'):
                input_file = os.path.join(ply_folder, filename)
                output_file = os.path.join(ply_folder, f'ftd_{filename}')
                self.roi_filter(input_file, output_file, voxel_size, roi, nb=5, std_r=2)

if __name__ == '__main__':
    fp = FilterProc()
    fp.run()