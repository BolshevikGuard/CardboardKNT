if __name__ == '__main__':

    from ultralytics import YOLO

    # 加载模型
    # 你可以加载预训练模型（如 yolov8n.pt），或者从头开始训练（如 'yolov8n.yaml'）
    model = YOLO("runs/detect/yolov8n_test/weights/last.pt")  # 加载预训练模型
    # model = YOLO("yolov8n.yaml")  # 从头开始训练

    # 开始训练
    results = model.train(
        data="data.yaml",  # 数据集配置文件路径
        epochs=100,           # 训练轮数
        batch=16,             # 批次大小
        imgsz=640,            # 输入图像尺寸
        device="0",           # 使用 GPU（"0" 表示 GPU 0，如果是 CPU 则设置为 "cpu"）
        name="yolov8n_test", # 训练结果的保存名称
        mosaic=0
    )