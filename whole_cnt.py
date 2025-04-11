# from sklearn.cluster import DBSCAN
# import numpy as np
import os
import json
import cv2

class WholeCnt():
    def __init__(self):
        self.cnt_list = []
        self.cnt_signal = None

    def depth2level(self, src_list, thresh=10):
        max_val = max(src_list)
        res = []
        for num in src_list:
            res.append(int(max_val-num)//thresh)
        return res

    def get_roi_means(self, img, data, layer):
        h, w = img.shape[:2]
        roi_means = []
        for i, line in enumerate(data):
            if line[-1] != layer:
                continue
            cx, cy, bw, bh = map(float, line[1:5])
            x1 = int((cx - bw / 2) * w)
            y1 = int((cy - bh / 2) * h)
            x2 = int((cx + bw / 2) * w)
            y2 = int((cy + bh / 2) * h)
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

    def front_proc(self, input, front_view):
        m = len(input)
        n = len(input[0])
        for i in range(n):
            b = front_view[i]
            for j in range(m-b, m):
                input[j][i] = 0
        return input

    def right_proc(self, input, right_view):
        m = len(input)
        n = len(input[0])
        for i in range(m):
            b = right_view[i]
            for j in range(n-b, n):
                input[m-i-1][j] = 0
        return input

    def back_proc(self, input, back_view):
        m = len(input)
        n = len(input[0])
        for i in range(n):
            b = back_view[i]
            for j in range(0, b):
                input[j][n-i-1] = 0
        return input

    def left_proc(self, input, left_view):
        m = len(input)
        n = len(input[0])
        for i in range(m):
            b = left_view[i]
            for j in range(0, b):
                input[i][j] = 0
        return input

    def update_cntlist(self):
        if self.cnt_signal:
            self.cnt_signal.emit(self.cnt_list)

    def run(self):

        print('Hello from WholeCnt')

        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        label_folder = config["label_path"]
        depth_folder = config["outdir"]

        common_names = []
        for file in os.listdir(label_folder):
            if file.endswith('txt'):
                common_names.append(file.split('.')[0])

        label_paths = [os.path.join(label_folder, p+'.txt') for p in common_names]
        depth_paths = [os.path.join(depth_folder, p+'.png') for p in common_names]

        # 4张图片为一批
        batch_size = 4

        # 每批的处理
        for i in range(0, len(label_paths), batch_size):
            cur_whole_cnt = 0
            bat_label_paths = label_paths[i:i+batch_size]
            bat_depth_paths = depth_paths[i:i+batch_size]
            bat_label_data = []
            for label_path in bat_label_paths:
                with open(label_path, 'r', encoding='utf-8') as f:
                    matrix = []
                    data = f.readlines()
                    matrix = [list(map(float, line.split())) for line in data]
                bat_label_data.append(matrix)
            # print(f'{bat_label_data=}')    

            # 最大层高
            max_layer = int(bat_label_data[0][-1][-1])
            print(f'\nGroup {int(i/4)+1}')

            # 每层计数
            for cur_layer in range(max_layer+1):
                width  = sum(1 for ly in bat_label_data[0] if ly[-1]==cur_layer) # 当前层最大宽长
                length = sum(1 for ly in bat_label_data[1] if ly[-1]==cur_layer) # 当前层最大纵长
                print(f'{cur_layer=} {width=} {length=}')
                flag_mat = [[1] * width for _ in range(length)] # 当前层的标志矩阵初始全为1
                print(f'{flag_mat=}')

                if width != 1 and length != 1:
                    view_levels = []
                    for i in range(4):
                        depth_img = cv2.imread(bat_depth_paths[i], cv2.IMREAD_GRAYSCALE)
                        layer_roi_means = self.get_roi_means(depth_img, bat_label_data[i], cur_layer)
                        layer_level = self.depth2level(layer_roi_means)
                        view_levels.append(layer_level)
                    flag_mat = self.front_proc(flag_mat, view_levels[0])
                    flag_mat = self.right_proc(flag_mat, view_levels[1])
                    flag_mat = self.back_proc(flag_mat, view_levels[2])
                    flag_mat = self.left_proc(flag_mat, view_levels[3])
                    layer_cnt = sum(sum(row) for row in flag_mat)
                else:
                    layer_cnt = width * length
                print(f'{layer_cnt=}')
                cur_whole_cnt += layer_cnt
            print(f'{cur_whole_cnt=}')
            self.cnt_list.append(cur_whole_cnt)
        
        self.update_cntlist()
        print("Count Done!")
            
if __name__ == "__main__":
    wc = WholeCnt()
    wc.run()