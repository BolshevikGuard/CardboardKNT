from ultralytics import YOLO

# 加载训练好的模型
model = YOLO("runs/detect/yolov8n_test/weights/last.pt")

# 对文件夹进行推理
results = model.predict(
    source="my_test",  # 输入文件夹路径
    save=True,
    iou=0.3,
    save_txt=True,
    save_conf=True,
    conf=0.5,
    project="my_test_output",  # 指定输出父目录
    name="detection_results",  # 指定输出子目录
    exist_ok=True  # 允许覆盖已有目录
)