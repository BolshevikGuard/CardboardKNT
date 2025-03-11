# -- coding: utf-8 --

import sys
import msvcrt
from ctypes import *
from MvCameraControl_class import *
import socket

HOST = '0.0.0.0'  # 监听所有网络接口
PORT = 12345  # 端口号，可自定义

server_mode = False

def To_hex_str(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2**32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr   
    return hexStr

def get_one_pic(obj_cam, pic_cnt, DeviceNum):
    for i in range(0, DeviceNum):
        stOutFrame = MV_FRAME_OUT()  
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))
        cam = obj_cam[i]
        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if None != stOutFrame.pBufAddr and 0 == ret:

            print (f"get one frame: Width[{stOutFrame.stFrameInfo.nWidth}], Height[{stOutFrame.stFrameInfo.nHeight}], picNum[{pic_cnt}]")

            stParam = MV_SAVE_IMG_TO_FILE_PARAM()
            stParam.enPixelType = stOutFrame.stFrameInfo.enPixelType
            stParam.pData = stOutFrame.pBufAddr
            stParam.nDataLen = stOutFrame.stFrameInfo.nFrameLen
            stParam.nWidth = stOutFrame.stFrameInfo.nWidth
            stParam.nHeight = stOutFrame.stFrameInfo.nHeight
            stParam.enImageType = MV_Image_Bmp
            stParam.pImagePath = f'savetest/cam{i}_{pic_cnt}.bmp'.encode('utf-8')
            stParam.iMethodValue = 0
            nRet = cam.MV_CC_SaveImageToFile(stParam)
            if nRet != 0:
                print(f'save failed[0x{To_hex_str(nRet)}]')
            else:
                print(f'cam_{i} img{pic_cnt} saved')
            
            nRet = cam.MV_CC_FreeImageBuffer(stOutFrame)

        else:
            print (f"no data[0x{To_hex_str(ret)}]")

if __name__ == "__main__":

    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    obj_cam = 0
    
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print (f"enum devices fail! ret[0x{To_hex_str(ret)}]")
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print ("find no device!")
        sys.exit()

    print (f"Find {deviceList.nDeviceNum} device(s)!")

    # 给出设备信息
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents

        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print (f"gige device: {i}")
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                strModeName = strModeName + chr(per)
            print (f"device model name: {strModeName}")

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print (f"current ip: {nip1}.{nip2}.{nip3}.{nip4}")

        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print (f"u3v device: {i}")
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print (f"device model name: {strModeName}")

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print (f"user serial number: {strSerialNumber}")

    # ch:创建相机实例 | en:Creat Camera Object
    obj_cam = []
    for i in range(0, deviceList.nDeviceNum):
        cam = MvCamera()
        # ch:选择设备并创建句柄 | en:Select device and create handle
        stDeviceList = cast(deviceList.pDeviceInfo[int(i)], POINTER(MV_CC_DEVICE_INFO)).contents
        ret = cam.MV_CC_CreateHandle(stDeviceList)
        obj_cam.append(cam)
        if ret != 0:
            print (f"create handle fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()

    # ch:打开设备 | en:Open device
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            print (f"open device fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()
        print(f'Device {i} opened')
    
    # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                if ret != 0:
                    print (f"Warning: Set Packet Size fail! ret[0x{To_hex_str(ret)}]")
            else:
                print (f"Warning: Get Packet Size fail! ret[0x{To_hex_str(nPacketSize)}]")
        stBool = c_bool(False)
        ret = cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
        if ret != 0:
            print (f"get AcquisitionFrameRateEnable fail! ret[0x{To_hex_str(ret)}]")

    # ch:设置触发模式为off | en:Set trigger mode as off
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            print (f"set trigger mode fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()

    # ch:开始取流 | en:Start grab image
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_StartGrabbing()
        if ret != 0:
            print (f"start grabbing fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()

    pic_cnt = 0
    
    # 拍摄一轮图像
    if server_mode:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            print('server activated, waiting for client...')
            conn, addr = server_socket.accept()
            with conn:
                print(f'client connected: {addr}')
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    elif data.strip().lower() == 's':
                        get_one_pic(obj_cam, pic_cnt, deviceList.nDeviceNum)
                        pic_cnt += 1
                    elif data.strip().lower() == 'e':
                        print('exit!')
                        break
                    else: print('invalid order!')
            conn.close()
    else:
        while True:
            print('[s] save one round / [esc] quit')
            key = msvcrt.getch().decode('utf-8')
            if key == 's':
                get_one_pic(obj_cam, pic_cnt, deviceList.nDeviceNum)
                pic_cnt += 1
            elif key == '\x1b':
                print('exit!')
                break
            else:
                print("press again")

    # ch:停止取流 | en:Stop grab image
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_StopGrabbing()
        if ret != 0:
            print (f"stop grabbing fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()

    # ch:关闭设备 | Close device
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_CloseDevice()
        if ret != 0:
            print (f"close deivce fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()

    # ch:销毁句柄 | Destroy handle
    for i in range(0, deviceList.nDeviceNum):
        cam = obj_cam[i]
        ret = cam.MV_CC_DestroyHandle()
        if ret != 0:
            print (f"destroy handle fail! ret[0x{To_hex_str(ret)}]")
            sys.exit()
