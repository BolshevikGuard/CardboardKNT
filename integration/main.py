import sys
from centerControl import CenterControl
import pred_test
import qr_scan
import layer_cnt
import depth_sim
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
    def __init__(self, center_control):
        super().__init__()
        self.controller = center_control

    def run(self):
        try:
            self.controller.run()
            print('Cuise Done!')
        except Exception as e:
            print(f"Cruise Error: {str(e)}")
    
class PredictThread(QThread):
    def __init__(self, pred_test):
        super().__init__()
        self.predictor = pred_test
    def run(self):
        self.predictor.run()

class DepthSimThread(QThread):
    def __init__(self, depth_sim):
        super().__init__()
        self.depthsimer = depth_sim
    def run(self):
        self.depthsimer.run()

class QrScanThread(QThread):
    def __init__(self, qr_scan):
        super().__init__()
        self.qrscanner = qr_scan
    def run(self):
        self.qrscanner.run()

class LayerCntThread(QThread):
    def __init__(self, layer_cnt):
        super().__init__()
        self.layercnter = layer_cnt
    def run(self):
        self.layercnter.run()

# GUI 界面
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能仓储盘点系统")
        self.init()
        self.center_control = CenterControl()
        self.pred_test = pred_test.PredictTest()
        self.depth_sim = depth_sim.DepthSim()
        self.qr_read = qr_scan.QrScan()
        self.layer_cnt = layer_cnt.LayerCnt()
        self.setGeometry(100, 100, 1000, 600)

    def init(self):
        layout      = QHBoxLayout()
        leftlayout  = QVBoxLayout()
        midlayout   = QVBoxLayout()
        rightlayout = QVBoxLayout()

        # 左侧布局 包括AGV启动按钮、AGV结束按钮、读图与推理按钮
        self.start_button = QPushButton("启动AGV巡航", self)
        self.start_button.clicked.connect(self.start_center_control)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.start_button)

        self.stop_button = QPushButton("结束AGV巡航", self)
        self.stop_button.clicked.connect(self.stop_center_control)
        self.stop_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.stop_button)

        self.pred_button = QPushButton("读取图片\n&&\n推理", self)
        self.pred_button.clicked.connect(self.read_pred)
        self.pred_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.pred_button)

        # 中部布局 包括QR识读与计数按钮、计数结果输出框
        self.QRcnt_button = QPushButton("扫描条码\n&&\n箱体计数", self)
        self.QRcnt_button.clicked.connect(self.qr_scan)
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

        # self.worker_thread = None
        sys.stdout = QTextEditLogger(self.log_output)

    # 启动AGV
    def start_center_control(self):
        if self.center_control.running:
            return
        self.center_control.running = True
        self.center_control_thread = CenterControlThread(self.center_control)
        self.center_control_thread.start()

    # 停止AGV
    def stop_center_control(self):
        self.center_control.stop()
        if self.center_control_thread:
            self.center_control_thread.quit()
            self.center_control_thread.wait()
        print('Cruise Finished!')

    # 读图与推理
    def read_pred(self):
        self.pred_test_thread = PredictThread(self.pred_test)
        self.pred_test_thread.start()
        self.pred_test_thread.wait()
        self.depth_sim_thread = DepthSimThread(self.depth_sim)
        self.depth_sim_thread.start()
        
    # 读码与计数
    def qr_scan(self):
        sys.stdout = QTextEditLogger(self.cnt_output)
        self.qr_scan_thread = QrScanThread(self.qr_read)
        self.qr_scan_thread.start()
        self.qr_scan_thread.wait()
        self.layer_cnt_thread = LayerCntThread(self.layer_cnt)
        self.layer_cnt_thread.start()
        self.layer_cnt_thread.wait()
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
