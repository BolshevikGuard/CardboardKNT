import numpy as np

# 定义 ROI 参数
roi = {
        "y": 1960,
        "x_left": -400,
        "x_right": 400,
        "z_down": -700,
        "z_up": 2000
    }

# 提取 ROI 信息
y = roi["y"]
x_left = roi["x_left"]
x_right = roi["x_right"]
z_down = roi["z_down"]
z_up = roi["z_up"]

# 定义矩形的 4 个角顶点
vertices = [
    (x_left, y, z_down),  # 左下角
    (x_right, y, z_down),  # 右下角
    (x_right, y, z_up),    # 右上角
    (x_left, y, z_up),     # 左上角
]

# 定义一个函数来在矩形的每个边上生成点
def generate_edge_points(x1, z1, x2, z2, y, num_points=200):
    # 在边的两个端点之间均匀分布点
    x_vals = np.linspace(x1, x2, num_points)
    z_vals = np.linspace(z1, z2, num_points)
    points = [(x, y, z) for x, z in zip(x_vals, z_vals)]
    return points

# 生成矩形的四条边上的点
edge_points = []
edge_points.extend(generate_edge_points(x_left, z_down, x_right, z_down, y))  # 下边
edge_points.extend(generate_edge_points(x_right, z_down, x_right, z_up, y))    # 右边
edge_points.extend(generate_edge_points(x_right, z_up, x_left, z_up, y))       # 上边
edge_points.extend(generate_edge_points(x_left, z_up, x_left, z_down, y))      # 左边

# 合并角点和边上点
all_points = edge_points + vertices

# 定义每个点的颜色 (红色)
colors = [(255, 0, 0)] * len(all_points)

# 将数据转换为适合 PLY 格式的字符串
ply_header = """ply
format ascii 1.0
element vertex {0}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
""".format(len(all_points))

# 将顶点数据和颜色信息拼接成 PLY 点云数据
ply_data = ""
for i, (x, y, z) in enumerate(all_points):
    r, g, b = colors[i]
    ply_data += f"{x} {y} {z} {r} {g} {b}\n"

# 保存 PLY 文件
ply_filename = "ROI_border_0430.ply"
with open(ply_filename, 'w') as ply_file:
    ply_file.write(ply_header)
    ply_file.write(ply_data)

print(f"PLY 文件已保存为 {ply_filename}")
