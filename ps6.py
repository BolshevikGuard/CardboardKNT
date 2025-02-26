import sys
import json
# from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel
import os
# import time
# import watchdog
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Run pred_test')
        self.setGeometry(100, 100, 800, 400)

        # 初始化UI
        self.initUI()

    def initUI(self):
        # 主布局
        layout = QVBoxLayout()

        # 选择路径部分（垂直排列）
        path_layout = QVBoxLayout()
        source_layout = QHBoxLayout()
        project_layout = QHBoxLayout()
        config_layout = QHBoxLayout()

        # 显示部分（水平排列）
        display_layout = QHBoxLayout()

        # Source路径部分
        self.source_label = QLabel("Source Path: ")
        self.source_path = QLabel("No Path Selected")
        self.source_button = QPushButton("Select Source")
        self.source_button.clicked.connect(self.select_source_path)

        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_path)
        source_layout.addWidget(self.source_button)

        # Project路径部分
        self.project_label = QLabel("Project Path: ")
        self.project_path = QLabel("No Path Selected")
        self.project_button = QPushButton("Select Project")
        self.project_button.clicked.connect(self.select_project_path)

        project_layout.addWidget(self.project_label)
        project_layout.addWidget(self.project_path)
        project_layout.addWidget(self.project_button)

        # Config路径部分

        self.config_label = QLabel('Config Path: ')
        self.config_path = QLabel('No Path Selected')
        self.config_button = QPushButton('Select Config')
        self.config_button.clicked.connect(self.select_config_path)

        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_path)
        config_layout.addWidget(self.config_button)

        path_layout.addLayout(source_layout)
        path_layout.addLayout(project_layout)
        path_layout.addLayout(config_layout)

        layout.addLayout(path_layout)

        # 运行按钮
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        # 配置显示框
        self.config_output = QTextEdit()
        self.config_output.setReadOnly(True)
        display_layout.addWidget(self.config_output)

        # 日志输出框
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        display_layout.addWidget(self.log_output)

        layout.addLayout(display_layout)

        self.setLayout(layout)

    def select_source_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self.source_path.setText(path)

    def select_project_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_path.setText(path)
    
    def select_config_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Config File')
        if path:
            self.config_path.setText(path)

    def run_script(self):
        # 获取路径
        source_path = self.source_path.text()
        project_path = self.project_path.text()

        # 更新config.json
        with open(self.config_path.text(), 'r') as f:
            config = json.load(f)
            f.close()

        # 更新源和项目路径
        config['source'] = source_path
        config['project'] = project_path
        config['model'] = self.config_path.text()[:-11] + 'last.pt' # config.json has 11 chars

        with open(self.config_path.text(), 'w') as f:
            json.dump(config, f, indent=4)
            self.display_config(config)
            f.close()

        self.pred_test(config)
        
        # 获取当前脚本的路径
        # current_dir = os.path.dirname(os.path.abspath(__file__))

        # # 运行脚本
        # self.process = QProcess(self)
        # self.process.setProgram("python")
        # self.process.setArguments([os.path.join(current_dir, "pred_test.py"), self.config_path.text()])  # 使用绝对路径
        # self.process.setWorkingDirectory(current_dir)  # 设置工作目录为当前目录

        # # 捕获输出
        # self.process.readyReadStandardOutput.connect(self.on_output_ready)
        # self.process.readyReadStandardError.connect(self.on_output_ready)

        # self.process.start()

    # def on_output_ready(self):
    #     output = bytes(self.process.readAllStandardOutput()).decode("utf-8")
    #     error_output = bytes(self.process.readAllStandardError()).decode("utf-8")
    #     self.log_output.append(output + error_output)

    def display_config(self, config):
        formatted_config = json.dumps(config, indent=4)
        self.config_output.setPlainText(formatted_config)
    
    def pred_test(self, config):

        # 读取JSON配置文件
        with open(self.config_path.text(), 'r') as f:
            config = json.load(f)
            f.close()
        self.log_output.append("配置文件已读取\n")

        pic_cnt = 0
        for filename in os.listdir(config["source"]):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                pic_cnt += 1
        self.log_output.append(f'文件夹图片数量为：{pic_cnt}\n')

        # 加载训练好的模型
        model = YOLO(config["model"])
        self.log_output.append('模型已加载')

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

        self.log_output.append('\n推理结束')
        self.log_output.append(f'\n结果保存至{config["project"]}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
