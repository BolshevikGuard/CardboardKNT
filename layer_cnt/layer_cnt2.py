from sklearn.cluster import DBSCAN
import numpy as np

# 读取YOLO推理结果文件
def read_yolo_results(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [list(map(float, line.split()[1:5])) for line in data]

# 读取YOLO识别结果
file_path = 'src/Image_20250108140359197.txt'
detections = read_yolo_results(file_path)
y_centers = [det[1] for det in detections]
y_centers.sort(reverse=True)
y_centers = np.array(y_centers).reshape(-1, 1)

# 使用DBSCAN进行聚类
dbscan = DBSCAN(eps=0.05, min_samples=1).fit(y_centers)
layers = dbscan.labels_

# 统计每层的箱子数量
layer_counts = {}
for label in layers:
    if label != -1:  # DBSCAN 可能会产生噪声点（-1表示未归类）
        layer_counts[label] = layer_counts.get(label, 0) + 1

# 输出层统计
print(f"{file_path}")
for layer, count in sorted(layer_counts.items()):
    print(f"Layer {layer}: {count} boxes")
