import json
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO

# 读取JSON配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 加载训练好的模型
model = YOLO(config["model"])

# 处理新文件的函数
def process_new_file(file_path):
    print(f"检测到新图片: {file_path}")
    # 添加延时确保文件可以完全写入
    time.sleep(config["sleep"])
    
    # 重试机制，直到文件可以访问
    retries = 3
    while retries > 0:
        try:
            # 检查文件是否存在，并且不是文件夹
            if os.path.exists(file_path) and os.path.isfile(file_path):
                results = model.predict(
                    source    = file_path,           # 输入单个图片路径
                    save      = config["save"],
                    iou       = config["iou"],
                    save_txt  = config["save_txt"],
                    save_conf = config["save_conf"],
                    conf      = config["conf"],
                    project   = config["project"],
                    name      = config["name"],
                    exist_ok  = config["exist_ok"],
                    verbose   = config["verbose"]
                )
                print(f"推理完成: {file_path}\n")
                break
            else:
                print(f"文件不存在或不是文件: {file_path}")
                break
        except PermissionError:
            print(f"文件被占用，等待重新尝试: {file_path}")
            retries -= 1
            time.sleep(1)  # 重试前稍作延迟
        except Exception as e:
            print(f"发生错误: {e}")
            break

# 自定义事件处理类
class NewImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 检查事件是否为新图片的创建
        if event.is_directory:
            return
        if event.src_path.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            process_new_file(event.src_path)

# 监视文件夹
def monitor_directory(directory_path):
    event_handler = NewImageHandler()
    observer      = Observer()
    observer.schedule(event_handler, path=directory_path, recursive=False)
    observer.start()
    print(f"开始监视文件夹: {directory_path}")
    try:
        while True:
            time.sleep(1)  # 保持监视
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# 开始监视指定的source文件夹
monitor_directory(config["source"])
