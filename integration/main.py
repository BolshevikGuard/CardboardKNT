import sys
import centerControl
import pred_test
import qrtest
import layer_cnt
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QSizePolicy
from PySide6.QtCore import QThread
from PySide6.QtGui import QFont

# 自定义日志重定向类
class QTextEditLogger:
    def __init__(self, text_edit_widget):
        self.widget = text_edit_widget

    def write(self, message):
        self.widget.append(message.strip())  # 更新 GUI 日志框

    def flush(self):
        pass

# 创建一个线程类来运行 centerControl
class CenterControlThread(QThread):

    def __init__(self):
        super().__init__()
        self.controller = centerControl.CenterControl()

    def run(self):
        try:
            self.controller.run()
            print('cuise done')
        except Exception as e:
            print(f"Cruise Error: {str(e)}")
    
    def stop(self):
        self.controller.stop()
        print('Cruise Finished!')

# GUI 界面
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能仓储盘点系统")
        self.init()
        self.setGeometry(100, 100, 1000, 600)

    def init(self):
        layout      = QHBoxLayout()
        leftlayout  = QVBoxLayout()
        midlayout   = QVBoxLayout()
        rightlayout = QVBoxLayout()

        # 左侧布局 包括AGV启动按钮、AGV结束按钮、读图与推理按钮
        self.start_button = QPushButton("Activate\nCenter Control", self)
        self.start_button.clicked.connect(self.start_center_control)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop\nCenter Control", self)
        self.stop_button.clicked.connect(self.stop_center_control)
        self.stop_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.stop_button)

        self.pred_button = QPushButton("Read Imgs\n&&\nPredict", self)
        self.pred_button.clicked.connect(self.read_pred)
        self.pred_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.pred_button)

        # 中部布局 包括QR识读与计数按钮、计数结果输出框
        self.QRcnt_button = QPushButton("Scan QR\n&&\nCount Boxes", self)
        self.QRcnt_button.clicked.connect(self.qr_count)
        self.QRcnt_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        midlayout.addWidget(self.QRcnt_button)

        self.cnt_output = QTextEdit(self)
        self.cnt_output.setReadOnly(True)
        self.cnt_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        midlayout.addWidget(self.cnt_output)

        midlayout.setStretchFactor(self.QRcnt_button, 1)
        midlayout.setStretchFactor(self.cnt_output, 2)

        # 右侧布局 包括日志框
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        rightlayout.addWidget(self.log_output)

        # 布局汇总
        layout.addLayout(leftlayout)
        layout.addLayout(midlayout)
        layout.addLayout(rightlayout)
        self.setLayout(layout)

        self.worker_thread = None
        sys.stdout = QTextEditLogger(self.log_output)

    # 启动AGV
    def start_center_control(self):
        if not self.worker_thread or not self.worker_thread.isRunning():
            self.worker_thread = CenterControlThread()
            self.worker_thread.run()

    # 停止AGV
    def stop_center_control(self):
        if self.worker_thread:
            self.worker_thread.stop()

    # 读图与推理
    def read_pred(self):
        pred = pred_test.PredictTest()
        pred.run()
        
    # 读码与计数
    def qr_count(self):
        sys.stdout = QTextEditLogger(self.cnt_output)
        qr = qrtest.QrTest()
        qr.run()
        lc = layer_cnt.LayerCnt()
        lc.run()
        sys.stdout = QTextEditLogger(self.log_output)

    # 当窗口大小改变时调整按钮字体大小
    def resizeEvent(self, event):
        new_size = max(self.width() // 50, 10)  # 防止太小
        font = QFont()
        font.setPointSize(new_size)
        self.start_button.setFont(font)
        self.stop_button.setFont(font)
        self.pred_button.setFont(font)
        self.QRcnt_button.setFont(font)
        super().resizeEvent(event)

# 运行应用
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
