import cv2
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import os
import json

class QrScan():
    def __init__(self):
        pass

    def read_qrcode(self, image_path, roi_cnt=1):
        # 读取图像
        image = cv2.imread(image_path)
        # 获取图像尺寸
        height, width = image.shape[:2]
        # 灰度化
        if len(image.shape) >= 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if roi_cnt == 4:
        # 仅提取右上角的区域
            roi1 = image[0:int(height * 0.5), int(width * 0.5):width]
            roi2 = image[0:int(height * 0.5), 0:int(width * 0.5)]
            roi3 = image[int(height * 0.5):height, 0:int(width * 0.5)]
            roi4 = image[int(height * 0.5):height, int(width * 0.5):width]
            rois = [roi1, roi2, roi3, roi4]
        elif roi_cnt == 9:
            roi1 = image[0:int(height*0.3), 0:int(width*0.3)]
            roi2 = image[int(height*0.3):int(height*0.6), 0:int(width*0.3)]
            roi3 = image[int(height*0.6):int(height*0.9), 0:int(width*0.3)]
            roi4 = image[0:int(height*0.3), int(width*0.3):int(width*0.6)]
            roi5 = image[int(height*0.3):int(height*0.6), int(width*0.3):int(width*0.6)]
            roi6 = image[int(height*0.6):int(height*0.9), int(width*0.3):int(width*0.6)]
            roi7 = image[0:int(height*0.3), int(width*0.6):int(width*0.9)]
            roi8 = image[int(height*0.3):int(height*0.6), int(width*0.6):int(width*0.9)]
            roi9 = image[int(height*0.6):int(height*0.9), int(width*0.6):int(width*0.9)]
            rois = [roi1, roi2, roi3, roi4, roi5, roi6, roi7, roi8, roi9]
        elif roi_cnt == 1:
            rois = [image]
        else:
            return []

        # 解码条形码
        qrcodes = []
        for roi in rois:
            qrcodes.append(pyzbar.decode(roi, symbols=[ZBarSymbol.CODABAR, ZBarSymbol.CODE128, ZBarSymbol.CODE39,
                                                       ZBarSymbol.CODE93, ZBarSymbol.COMPOSITE, ZBarSymbol.DATABAR,
                                                       ZBarSymbol.DATABAR_EXP, ZBarSymbol.EAN13, ZBarSymbol.EAN2,
                                                       ZBarSymbol.EAN5, ZBarSymbol.EAN8, ZBarSymbol.I25,
                                                       ZBarSymbol.ISBN10, ZBarSymbol.ISBN13, ZBarSymbol.PARTIAL, 
                                                       ZBarSymbol.QRCODE, ZBarSymbol.SQCODE, ZBarSymbol.UPCA, 
                                                       ZBarSymbol.UPCE]))
        # 处理解码结果
        res = [qrcode.data.decode('utf-8') for lists in qrcodes for qrcode in lists]
        return res

    def run(self):
        print('hello from qrtest')
        # return
        # 指定文件夹路径
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        folder_path = config['qr_src_path']
        roi_cnt     = config['roi_cnt']

        # 遍历文件夹中的所有图片
        for filename in os.listdir(folder_path):
            if filename.endswith((".bmp", "png", "jpg", "jpeg")):
                image_path = os.path.join(folder_path, filename)
                qrcodes    = self.read_qrcode(image_path, roi_cnt=roi_cnt)
                if qrcodes:
                    print(f"{os.path.basename(filename)} {qrcodes}")
        
        print("QR Scan Done!")

if __name__ == "__main__":
    qt = QrScan()
    qt.run()