import sys
import json
from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel
import os

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Run pred_test_wd')
        self.setGeometry(100, 100, 800, 400)

        # 初始化UI
        self.initUI()

    def initUI(self):
        # 主布局
        layout = QVBoxLayout()

        # 选择路径部分（垂直排列）
        path_layout = QVBoxLayout()

        # Source路径部分
        self.source_label = QLabel("Source Path: ")
        self.source_path = QLabel("No Path Selected")
        self.source_button = QPushButton("Select Source")
        self.source_button.clicked.connect(self.select_source_path)

        path_layout.addWidget(self.source_label)
        path_layout.addWidget(self.source_path)
        path_layout.addWidget(self.source_button)

        # Project路径部分
        self.project_label = QLabel("Project Path: ")
        self.project_path = QLabel("No Path Selected")
        self.project_button = QPushButton("Select Project")
        self.project_button.clicked.connect(self.select_project_path)

        path_layout.addWidget(self.project_label)
        path_layout.addWidget(self.project_path)
        path_layout.addWidget(self.project_button)

        layout.addLayout(path_layout)

        # 运行按钮
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        # 日志输出框
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def select_source_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self.source_path.setText(path)

    def select_project_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_path.setText(path)

    def run_script(self):
        # 获取路径
        source_path = self.source_path.text()
        project_path = self.project_path.text()

        # 更新config.json
        with open('config.json', 'r') as f:
            config = json.load(f)

        # 更新源和项目路径
        config['source'] = source_path
        config['project'] = project_path

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            f.close()

        # 获取当前脚本的路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 运行脚本
        self.process = QProcess(self)
        self.process.setProgram("python")
        self.process.setArguments([os.path.join(current_dir, "pred_test_wd.py")])  # 使用绝对路径
        self.process.setWorkingDirectory(current_dir)  # 设置工作目录为当前目录

        # 捕获输出
        self.process.readyReadStandardOutput.connect(self.on_output_ready)
        self.process.readyReadStandardError.connect(self.on_output_ready)

        self.process.start()

    def on_output_ready(self):
        output = bytes(self.process.readAllStandardOutput()).decode("utf-8")
        error_output = bytes(self.process.readAllStandardError()).decode("utf-8")
        self.log_output.append(output + error_output)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
