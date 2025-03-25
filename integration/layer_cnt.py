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
        return [list(map(float, line.split()[1:5])) for line in data]
    
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

            # 输出字符处理
            res = ''
            for layer, count in sorted(layer_counts.items()):
                res += f"[{layer}: {count}] "
            
            # 输出层统计结果
            print(f"{txt} {res}")

if __name__ == "__main__":
    lc = LayerCnt()
    lc.run()