import open3d as o3d
import numpy as np

class ROIbg:
    def __init__(self, y, x_left, x_right, z_down, z_up):
        self.y = y
        self.x_left = x_left
        self.x_right = x_right
        self.z_down = z_down
        self.z_up = z_up

def roi_filter(input_file, output_file, voxel_sz, roi:ROIbg, nb, std_r):
    pcd = o3d.io.read_point_cloud(input_file)
    print(f"读取点云 {input_file} 点数 {len(pcd.points)}")

    # 体素下采样
    pcd = pcd.voxel_down_sample(voxel_sz)
    print(f'体素下采样后点数 {len(pcd.points)}')

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

if __name__ == "__main__":
    filename = "hello2.ply"  # 输入的PLY文件
    input_file = "models/"+filename
    voxel_size = 0.01  # 体素大小，可以根据需求调整
    output_file = "modelsout/ftd_"+filename

    roi_paras = {
        "y" : 2000,
        "x_left" : -400,
        "x_right" : 400,
        "z_down" : -737,
        "z_up" : -210
    }

    neigbours = 5
    std_ratio = 2

    roi = ROIbg(y       = roi_paras["y"], 
                x_left  = roi_paras["x_left"],
                x_right = roi_paras["x_right"],
                z_down  = roi_paras["z_down"],
                z_up    = roi_paras["z_up"])
    
    roi_filter(input_file, output_file, voxel_size, roi, neigbours, std_ratio)
    
