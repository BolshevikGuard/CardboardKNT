import os
import json
import cv2

class DepthProc():
    def __init__(self):
        pass

    def get_roi_means(self, img, label_path):
        h, w = img.shape[:2]

        with open(label_path, 'r') as f:
            labels = f.readlines()
        print(f"\nProcessing {os.path.basename(label_path)}")

        roi_means = []
        for i, line in enumerate(labels):
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # 跳过格式错误的行

            # YOLO: class cx cy w h [confidence]
            cx, cy, bw, bh = map(float, parts[1:5])

            # 转换为像素坐标
            x1 = int((cx - bw / 2) * w)
            y1 = int((cy - bh / 2) * h)
            x2 = int((cx + bw / 2) * w)
            y2 = int((cy + bh / 2) * h)

            # 裁剪在图像范围内
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))

            roi = img[y1:y2, x1:x2]
            if roi.size == 0:
                print(f"Box {i}: empty ROI, skipped.")
                continue

            mean_val = roi.mean()
            roi_means.append(mean_val)
        return roi_means

    def run(self):

        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        label_folder = config['label_path']
        depth_folder = config['outdir']

        paths = []
        for file in os.listdir(label_folder):
            if file.endswith('.txt'):
                paths.append(file.split('.')[0])
        label_paths = [os.path.join(label_folder, p+'.txt') for p in paths]
        depth_paths = [os.path.join(depth_folder, p+'.png') for p in paths]

        for idx, dpth in enumerate(depth_paths):
            # 读取灰度图像
            img = cv2.imread(dpth, cv2.IMREAD_GRAYSCALE)
            roi_means = self.get_roi_means(img, label_paths[idx])
            for idx, mean in enumerate(roi_means):
                print(f'Box {idx} Mean {mean:.2f}')

if __name__ == '__main__':
    dp = DepthProc()
    dp.run()