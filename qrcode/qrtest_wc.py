# 依赖：opencv-python opencv-contrib-python

import cv2
# import numpy as np
import os

depro = './config/detect.prototxt'
decaf = './config/detect.caffemodel'
srpro = './config/sr.prototxt'
srcaf = './config/sr.caffemodel'
global detector
detector = cv2.wechat_qrcode.WeChatQRCode(depro, decaf, srpro, srcaf)

def read_qrcode(image_path, roi_cnt=1):
    global detector
    # 读取图像
    image = cv2.imread(image_path)
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 灰度化
    if len(image.shape) >= 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # ROI    
    if roi_cnt == 4:
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
    results = []
    for roi in rois:
        result, _ = detector.detectAndDecode(roi)
        results.append(list(result))
    res = [qrcode for lists in results for qrcode in lists]
    return res

# 指定文件夹路径
folder_path = "savetest_alt"
roi_cnt = 9

# 遍历文件夹中的所有图片
for filename in os.listdir(folder_path):
    if filename.endswith((".bmp", "png")):  # 只处理 .bmp 文件
        image_path = os.path.join(folder_path, filename)
        qrcodes = read_qrcode(image_path, roi_cnt=roi_cnt)
        if qrcodes:
            print(f"wc roi{roi_cnt} {filename} ", qrcodes)
        else:
            print(f"wc roi{roi_cnt} {filename} None\r", end='', flush=True)