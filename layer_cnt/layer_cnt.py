from sklearn.cluster import DBSCAN
import numpy as np
import os

# 读取YOLO推理结果文件
def read_yolo_results(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [list(map(float, line.split()[1:5])) for line in data]

# 读取YOLO识别结果
folderpath = 'src/'
txts = [folderpath+f for f in os.listdir(folderpath) if f.endswith('.txt')]
for txt in txts:
    detections = read_yolo_results(txt)
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
    print(f"\n{txt} ", end='')
    for layer, count in sorted(layer_counts.items()):
        print(f"[{layer}: {count}] ", end='')