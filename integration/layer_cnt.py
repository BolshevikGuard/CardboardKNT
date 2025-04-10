from sklearn.cluster import DBSCAN
import numpy as np
import os
import json

class LayerCnt():
    def __init__(self):
        pass

    def read_yolo_results(self, file_path):
        with open(file_path, 'r') as file:
            data = file.readlines()
        return [list(map(float, line.split())) for line in data]
    
    def write_yolo_results_with_layer(self, file_path, detections, layers):
        with open(file_path, 'w') as file:
            for i, det in enumerate(detections):
                # type cx cy x y conf layer
                file.write(f"0 {det[1]} {det[2]} {det[3]} {det[4]} {det[5]} {layers[i]}\n")
    
    def run(self):
        print('hello from layer cnt')
        # return
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        label_path = config['label_path']
        
        # 读取YOLO识别结果
        txts = [os.path.join(label_path, f) for f in os.listdir(label_path) if f.endswith('.txt')]

        for txt in txts:
            detections = self.read_yolo_results(txt)
            detections.sort(key=lambda x: x[2], reverse=True)
            y_centers = [det[2] for det in detections]
            # y_centers.sort(reverse=True)
            y_centers = np.array(y_centers).reshape(-1, 1)

            # 使用DBSCAN进行聚类
            dbscan = DBSCAN(eps=0.05, min_samples=1).fit(y_centers)
            layers = dbscan.labels_

            # 分配层数
            layer_labels = [layers[i] for i in range(len(detections))]
            self.write_yolo_results_with_layer(txt, detections, layer_labels)

            # 统计每层的箱子数量
            layer_counts = {}
            for label in layers:
                if label != -1:  # DBSCAN 可能会产生噪声点（-1表示未归类）
                    layer_counts[label] = layer_counts.get(label, 0) + 1

            # 输出字符处理
            res = ''
            for layer, count in sorted(layer_counts.items()):
                res += f"[{layer}: {count}] "
            
            # 输出层统计结果
            print(f"{os.path.basename(txt)} {res}")
        
        print("Layer Count Done!")

if __name__ == "__main__":
    lc = LayerCnt()
    lc.run()