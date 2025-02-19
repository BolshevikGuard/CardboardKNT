import json
from ultralytics import YOLO

# 读取JSON配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 加载训练好的模型
model = YOLO(config["model"])

# 对文件夹进行推理
results = model.predict(
    source=config["source"],  # 输入文件夹路径
    save=config["save"],
    iou=config["iou"],
    save_txt=config["save_txt"],
    save_conf=config["save_conf"],
    conf=config["conf"],
    project=config["project"],  # 指定输出父目录
    name=config["name"],  # 指定输出子目录
    exist_ok=config["exist_ok"]  # 允许覆盖已有目录
)
