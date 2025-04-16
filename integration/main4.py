import sys
import centerControl, pred_test, qr_scan, layer_cnt, depth_sim, whole_cnt
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QGridLayout
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QGuiApplication, QImage, QPixmap

# 自定义日志重定向类
class QTextEditLogger:
    def __init__(self, text_edit_widget):
        self.widget = text_edit_widget
    def write(self, message):
        self.widget.append(message.strip())  # 更新 GUI 日志框
    def flush(self):
        pass

# 创建各种线程类
class GenericThread(QThread): # 通用线程类
    def __init__(self, task_obj):
        super().__init__()
        self.task_obj = task_obj
    def run(self):
        self.task_obj.run()

class QrScanThread(QThread):
    qr_signal = Signal(dict)
    def __init__(self, qr_scan, batch_num, image_labels):
        super().__init__()
        self.qrscanner           = qr_scan(batch_num, image_labels)
        self.qrscanner.qr_signal = self.qr_signal
        # self.batch_num = batch_num
    def run(self):
        self.qrscanner.run()

class WholeCntThread(QThread):
    cnt_signal = Signal(list)
    def __init__(self, whole_cnt, batch_num):
        super().__init__()
        self.wholecnter            = whole_cnt(batch_num)
        self.wholecnter.cnt_signal = self.cnt_signal
        # self.batch_num = batch_num
    def run(self):
        self.wholecnter.run()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('智能仓储盘点系统')
        self.ui_init()
        self.batch_num      = 0
        self.center_control = centerControl.CenterControl()
        self.pred_test      = pred_test.PredictTest()
        self.depth_sim      = depth_sim.DepthSim()
        self.qr_read        = qr_scan.QrScan
        self.layer_cnt      = layer_cnt.LayerCnt()
        self.whole_cnt      = whole_cnt.WholeCnt
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width()//5*4, screen.height()//5*4)
    
    # 界面描述
    def ui_init(self):
        layout      = QHBoxLayout()
        leftlayout  = QVBoxLayout()
        midlayout   = QVBoxLayout()
        rightlayout = QVBoxLayout()

        # 左侧：示意图及其标签 开始按钮 结束按钮 RFID及其标签
        self.cruisemap_title = QLabel('当前AGV巡航地图示意')
        self.cruisemap_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cruisemap      = QImage('cruise_map.png')
        cruisemaplabel = QLabel()
        cruisemaplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cruisemaplabel.setPixmap(QPixmap.fromImage(cruisemap))
        cruisemaplabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cruisemaplabel.setMinimumSize(1, 1)

        leftbuttons       = QHBoxLayout()
        self.start_button = QPushButton("启动AGV巡航", self)
        self.start_button.clicked.connect(self.start_center_control)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftbuttons.addWidget(self.start_button)

        self.stop_button = QPushButton("结束AGV巡航", self)
        self.stop_button.clicked.connect(self.stop_center_control)
        self.stop_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stop_button.setEnabled(False)
        leftbuttons.addWidget(self.stop_button)

        self.rfid_title = QLabel('RFID信息')
        self.rfid_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rfid_table = QTableWidget()
        rfid_table.setRowCount(5)
        rfid_table.setColumnCount(3)
        rfid_table.verticalHeader().setVisible(False)
        rfid_table.horizontalHeader().setVisible(False)
        rfid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        rfid_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        rfid_table.setStyleSheet('background-color: grey')

        leftlayout.addWidget(self.cruisemap_title, stretch=1)
        leftlayout.addWidget(cruisemaplabel, stretch=6)
        leftlayout.addLayout(leftbuttons, stretch=1)
        leftlayout.addWidget(self.rfid_title, stretch=1)
        leftlayout.addWidget(rfid_table, stretch=6)

        # 中间：堆垛图像及其标题 开始处理按钮 下一堆垛按钮 上一堆垛按钮
        self.boxpics_title = QLabel('当前处理批次图像')
        self.boxpics_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_labels = [QLabel(self) for _ in range(4)]
        for label in self.image_labels:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setText('None for now')
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setMinimumSize(1, 1)
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.image_labels[0], 0, 0)
        grid_layout.addWidget(self.image_labels[1], 0, 1)
        grid_layout.addWidget(self.image_labels[2], 1, 0)
        grid_layout.addWidget(self.image_labels[3], 1, 1)

        midbuttons       = QHBoxLayout()
        self.pred_button = QPushButton("开始处理", self)
        self.pred_button.clicked.connect(self.read_pred)
        self.pred_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
        self.next_button = QPushButton("下一堆垛", self)
        self.next_button.clicked.connect(self.next_stack)
        self.next_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.next_button.setEnabled(False)

        self.former_buttom = QPushButton("上一堆垛", self)
        self.former_buttom.clicked.connect(self.former_stack)
        self.former_buttom.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.former_buttom.setEnabled(False)

        midbuttons.addWidget(self.pred_button)
        midbuttons.addWidget(self.next_button)
        midbuttons.addWidget(self.former_buttom)
        midlayout.addWidget(self.boxpics_title, stretch=1)
        midlayout.addLayout(grid_layout, stretch=14)
        midlayout.addLayout(midbuttons, stretch=1)

        # 右侧：二维码信息及其标题 数量结果及其标题 日志框及其标题
        self.qr_title = QLabel('二维码/条形码信息')
        self.qr_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qrtable = QTableWidget(self)
        self.qrtable.setRowCount(5)
        self.qrtable.setColumnCount(4)
        self.qrtable.verticalHeader().setVisible(False)
        self.qrtable.horizontalHeader().setVisible(False)
        self.qrtable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.qrtable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.qrtable.setStyleSheet('background-color: grey')

        self.cnt_title = QLabel('计数结果')
        self.cnt_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnttable = QTableWidget(self)
        self.cnttable.setRowCount(2)
        self.cnttable.setColumnCount(3)
        self.cnttable.verticalHeader().setVisible(False)
        self.cnttable.horizontalHeader().setVisible(False)
        self.cnttable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cnttable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        item0 = QTableWidgetItem('应有数量')
        item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnttable.setItem(0, 0, item0)
        item1 = QTableWidgetItem('实际数量')
        item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnttable.setItem(0, 1, item1)
        item2 = QTableWidgetItem('应有数量')
        item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnttable.setItem(0, 2, item2)
        self.cnttable.setStyleSheet('background-color: grey')

        self.log_title = QLabel('日志输出')
        self.log_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)

        rightlayout.addWidget(self.qr_title, stretch=1)
        rightlayout.addWidget(self.qrtable, stretch=7)
        rightlayout.addWidget(self.cnt_title, stretch=1)
        rightlayout.addWidget(self.cnttable, stretch=3)
        rightlayout.addWidget(self.log_title, stretch=1)
        rightlayout.addWidget(self.log_output, stretch=4)

        # 布局汇总
        layout.addLayout(leftlayout, stretch=2)
        layout.addLayout(midlayout, stretch=3)
        layout.addLayout(rightlayout, stretch=2)
        self.setLayout(layout)

        sys.stdout = QTextEditLogger(self.log_output)
    
    # 启动AGV
    def start_center_control(self):
        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)
        if self.center_control.running:
            return
        self.center_control.running = True
        self.center_control_thread  = GenericThread(self.center_control)
        self.center_control_thread.start()

    # 停止AGV
    def stop_center_control(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.center_control.stop()
        if self.center_control_thread:
            self.center_control_thread.quit()
            self.center_control_thread.wait()
        print('Cruise Finished!')

    # 读图推理 单目深度估计 分层聚类 第一堆垛展示
    def read_pred(self):
        self.batch_num = 0
        self.pred_test_thread = GenericThread(self.pred_test)
        self.pred_test_thread.start()
        self.pred_test_thread.wait()
        self.depth_sim_thread = GenericThread(self.depth_sim)
        self.depth_sim_thread.start()
        self.depth_sim_thread.wait()
        self.layer_cnt_thread = GenericThread(self.layer_cnt)
        self.layer_cnt_thread.start()
        self.layer_cnt_thread.wait()
        self.qr_scan_thread = QrScanThread(self.qr_read, self.batch_num, self.image_labels)
        self.qr_scan_thread.qr_signal.connect(self.update_qrdict)
        self.qr_scan_thread.start()
        self.qr_scan_thread.wait()
        self.whole_cnt_thread = WholeCntThread(self.whole_cnt, self.batch_num)
        self.whole_cnt_thread.cnt_signal.connect(self.update_cntlist)
        self.whole_cnt_thread.start()
        self.whole_cnt_thread.wait()
        self.next_button.setEnabled(True)

    # 下一堆垛
    def next_stack(self):
        self.batch_num += 1
        self.qr_scan_thread = QrScanThread(self.qr_read, self.batch_num, self.image_labels)
        self.qr_scan_thread.qr_signal.connect(self.update_qrdict)
        self.qr_scan_thread.start()
        self.qr_scan_thread.wait()
        self.whole_cnt_thread = WholeCntThread(self.whole_cnt, self.batch_num)
        self.whole_cnt_thread.cnt_signal.connect(self.update_cntlist)
        self.whole_cnt_thread.start()
        self.whole_cnt_thread.wait()
        self.former_buttom.setEnabled(True)

    def former_stack(self):
        self.batch_num = max(0, self.batch_num-1)
        self.qr_scan_thread = QrScanThread(self.qr_read, self.batch_num, self.image_labels)
        self.qr_scan_thread.qr_signal.connect(self.update_qrdict)
        self.qr_scan_thread.start()
        self.qr_scan_thread.wait()
        self.whole_cnt_thread = WholeCntThread(self.whole_cnt, self.batch_num)
        self.whole_cnt_thread.cnt_signal.connect(self.update_cntlist)
        self.whole_cnt_thread.start()
        self.whole_cnt_thread.wait()

    # 更新条形码/二维码信息表格
    def update_qrdict(self, qr_dict):
        col = 0
        for key in qr_dict.keys():
            vals = qr_dict[key]
            self.qrtable.setItem(0, col, QTableWidgetItem(str(key)))
            for i in range(0, len(vals)):
                self.qrtable.setItem(i+1, col, QTableWidgetItem(str(vals[i])))
            col += 1

    # 更新计数结果表格
    def update_cntlist(self, cnt_list):
        for val in cnt_list:
            self.cnttable.setItem(1, 1, QTableWidgetItem(str(val)))

    # 窗口放缩事件函数
    def resizeEvent(self, event):
        new_size = max(self.width() // 100, 8)  # 防止太小
        font = QFont()
        font.setPointSize(new_size)
        self.cruisemap_title.setFont(font)
        self.start_button.setFont(font)
        self.stop_button.setFont(font)
        self.rfid_title.setFont(font)
        self.boxpics_title.setFont(font)
        self.pred_button.setFont(font)
        self.next_button.setFont(font)
        self.former_buttom.setFont(font)
        self.qr_title.setFont(font)
        # self.qrtable.setFont(font)
        self.cnt_title.setFont(font)
        self.cnttable.setFont(font)
        self.log_title.setFont(font)
        # self.log_output.setFont(font)

        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())