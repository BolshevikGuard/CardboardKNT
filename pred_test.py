import json
from ultralytics import YOLO
import os

class PredictTest():
    def __init__(self):
        pass

    def run(self):
        print("hello from pred!")
        # return
        # 读取JSON配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("Prediction config loaded")

        pic_cnt = 0
        for filename in os.listdir(config["source"]):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                pic_cnt += 1
        print(f'Img count: {pic_cnt}')

        # 加载训练好的模型
        model = YOLO(config["model"])
        print('Model loaded')

        # 对文件夹进行推理
        results = model.predict(
            source    = config["source"],    # 输入文件夹路径
            save      = config["save"],
            iou       = config["iou"],
            save_txt  = config["save_txt"],
            save_conf = config["save_conf"],
            conf      = config["conf"],
            project   = config["project"],   # 指定输出父目录
            name      = config["name"],      # 指定输出子目录
            exist_ok  = config["exist_ok"],  # 允许覆盖已有目录
            verbose   = config["verbose"]
        )

        print('\nPrediction Done!')

if __name__ == '__main__':
    pt = PredictTest()
    pt.run()