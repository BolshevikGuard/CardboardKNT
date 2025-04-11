import sys
from centerControl import CenterControl
import pred_test
import qr_scan
import layer_cnt
import depth_sim
import whole_cnt
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont, QGuiApplication

# 自定义日志重定向类
class QTextEditLogger:
    def __init__(self, text_edit_widget):
        self.widget = text_edit_widget

    def write(self, message):
        self.widget.append(message.strip())  # 更新 GUI 日志框

    def flush(self):
        pass

# 创建各种线程类
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
    qr_signal = Signal(dict)
    def __init__(self, qr_scan):
        super().__init__()
        self.qrscanner = qr_scan
        self.qrscanner.qr_signal = self.qr_signal
    def run(self):
        self.qrscanner.run()

class LayerCntThread(QThread):
    def __init__(self, layer_cnt):
        super().__init__()
        self.layercnter = layer_cnt
    def run(self):
        self.layercnter.run()

class WholeCntThread(QThread):
    cnt_signal = Signal(list)
    def __init__(self, whole_cnt):
        super().__init__()
        self.wholecnter = whole_cnt
        self.wholecnter.cnt_signal = self.cnt_signal
    def run(self):
        self.wholecnter.run()

# GUI 界面
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能仓储盘点系统")
        self.init()
        self.center_control = CenterControl()
        self.pred_test      = pred_test.PredictTest()
        self.depth_sim      = depth_sim.DepthSim()
        self.qr_read        = qr_scan.QrScan()
        self.layer_cnt      = layer_cnt.LayerCnt()
        self.whole_cnt      = whole_cnt.WholeCnt()
        # self.setGeometry(100, 100, 1000, 600)
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

    def init(self):
        layout      = QHBoxLayout()
        leftlayout  = QVBoxLayout()
        uplayout   = QHBoxLayout()
        rightlayout = QVBoxLayout()

        # 左侧布局 包括AGV启动按钮、AGV结束按钮、读图与推理按钮、QR识读与计数按钮
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

        self.QRcnt_button = QPushButton("扫描条码\n&&\n箱体计数", self)
        self.QRcnt_button.clicked.connect(self.qr_scan)
        self.QRcnt_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftlayout.addWidget(self.QRcnt_button)

        # 右上部布局 包括读码结果、分层计数结果

        self.qrtable = QTableWidget(self)
        self.qrtable.setRowCount(5)
        self.qrtable.setColumnCount(8)
        self.qrtable.verticalHeader().setVisible(False)
        self.qrtable.horizontalHeader().setVisible(False)
        self.qrtable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.qrtable.setStyleSheet('background-color: grey')
        uplayout.addWidget(self.qrtable)

        self.cnttable = QTableWidget(self)
        self.cnttable.setRowCount(5)
        self.cnttable.setColumnCount(2)
        self.cnttable.verticalHeader().setVisible(False)
        self.cnttable.horizontalHeader().setVisible(False)
        self.cnttable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cnttable.setStyleSheet('background-color: grey')
        uplayout.addWidget(self.cnttable)

        uplayout.setStretchFactor(self.qrtable, 4)
        uplayout.setStretchFactor(self.cnttable, 1)

        # 右侧布局 包括右上布局和日志框
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        rightlayout.addLayout(uplayout)
        rightlayout.addWidget(self.log_output)
        rightlayout.setStretchFactor(uplayout, 5)
        rightlayout.setStretchFactor(self.log_output, 1)

        # 布局汇总
        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)
        layout.setStretchFactor(leftlayout, 1)
        layout.setStretchFactor(rightlayout, 5)
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

    # 推理与深度估计
    def read_pred(self):
        self.pred_test_thread = PredictThread(self.pred_test)
        self.pred_test_thread.start()
        self.pred_test_thread.wait()
        self.depth_sim_thread = DepthSimThread(self.depth_sim)
        self.depth_sim_thread.start()
        
    # 读码与计数
    def qr_scan(self):
        self.qr_scan_thread = QrScanThread(self.qr_read)
        self.qr_scan_thread.qr_signal.connect(self.update_qrdict)
        self.qr_scan_thread.start()
        self.qr_scan_thread.wait()

        self.layer_cnt_thread = LayerCntThread(self.layer_cnt)
        self.layer_cnt_thread.start()
        self.layer_cnt_thread.wait()

        self.whole_cnt_thread = WholeCntThread(self.whole_cnt)
        self.whole_cnt_thread.cnt_signal.connect(self.update_cntlist)
        self.whole_cnt_thread.start()
        self.whole_cnt_thread.wait()

    def update_qrdict(self, qr_dict):
        col = 0
        for key in qr_dict.keys():
            vals = qr_dict[key]
            self.qrtable.setItem(0, col, QTableWidgetItem(str(key)))
            for i in range(0, len(vals)):
                self.qrtable.setItem(i+1, col, QTableWidgetItem(str(vals[i])))
            col += 1
    
    def update_cntlist(self, cnt_list):
        for idx, val in enumerate(cnt_list):
            self.cnttable.setItem(idx, 0, QTableWidgetItem(f'Group {idx+1}'))
            self.cnttable.setItem(idx, 1, QTableWidgetItem(str(val)))

    # 当窗口大小改变时调整按钮字体大小
    def resizeEvent(self, event):
        new_size = max(self.width() // 80, 8)  # 防止太小
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
