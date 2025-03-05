# -- coding: utf-8 --

import sys
import threading
import msvcrt
from ctypes import *
from MvCameraControl_class import *
import time

g_bExit = False

# 为线程定义一个函数
def work_thread(cam=0, pData=0, nDataSize=0):
    stOutFrame = MV_FRAME_OUT()  
    memset(byref(stOutFrame), 0, sizeof(stOutFrame))
    while True:
        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if None != stOutFrame.pBufAddr and 0 == ret:

            print (f"get one frame: Width[{stOutFrame.stFrameInfo.nWidth}], Height[{stOutFrame.stFrameInfo.nHeight}], nFrameNum[{stOutFrame.stFrameInfo.nFrameNum}]")

            stParam = MV_SAVE_IMG_TO_FILE_PARAM()
            stParam.enPixelType = stOutFrame.stFrameInfo.enPixelType
            stParam.pData = stOutFrame.pBufAddr
            stParam.nDataLen = stOutFrame.stFrameInfo.nFrameLen
            stParam.nWidth = stOutFrame.stFrameInfo.nWidth
            stParam.nHeight = stOutFrame.stFrameInfo.nHeight
            stParam.enImageType = MV_Image_Bmp
            stParam.pImagePath = f'hk/savetest/{stOutFrame.stFrameInfo.nFrameNum}.bmp'.encode('utf-8')
            stParam.iMethodValue = 0
            nRet = cam.MV_CC_SaveImageToFile(stParam)
            if nRet != 0:
                print(f'save failed[0x{nRet}]')
            else:
                print('img saved')
            
            nRet = cam.MV_CC_FreeImageBuffer(stOutFrame)

            time.sleep(1)
        else:
            print (f"no data[0x{ret}]")
        if g_bExit == True:
            break

if __name__ == "__main__":

    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print (f"enum devices fail! ret[0x{ret}]")
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print ("find no device!")
        sys.exit()

    print (f"Find {deviceList.nDeviceNum} device(s)!")

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

    nConnectionNum = input("please input the number of the device to connect: ")

    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print ("intput error!")
        sys.exit()

    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()
    
    # ch:选择设备并创建句柄 | en:Select device and create handle
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print (f"create handle fail! ret[0x{ret}]")
        sys.exit()

    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print (f"open device fail! ret[0x{ret}]")
        sys.exit()
    
    # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
            if ret != 0:
                print (f"Warning: Set Packet Size fail! ret[0x{ret}]")
        else:
            print (f"Warning: Get Packet Size fail! ret[0x{nPacketSize}]")

    stBool = c_bool(False)
    ret = cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
    if ret != 0:
        print (f"get AcquisitionFrameRateEnable fail! ret[0x{ret}]")

    # ch:设置触发模式为off | en:Set trigger mode as off
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print (f"set trigger mode fail! ret[0x{ret}]")
        sys.exit()

    # ch:开始取流 | en:Start grab image
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print (f"start grabbing fail! ret[0x{ret}]")
        sys.exit()

    try:
        hThreadHandle = threading.Thread(target=work_thread, args=(cam, None, None))
        hThreadHandle.start()
    except:
        print ("error: unable to start thread")
        
    print ("press a key to stop grabbing.")
    msvcrt.getch()

    g_bExit = True
    hThreadHandle.join()

    # ch:停止取流 | en:Stop grab image
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print (f"stop grabbing fail! ret[0x{ret}]")
        sys.exit()

    # ch:关闭设备 | Close device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print (f"close deivce fail! ret[0x{ret}]")
        sys.exit()

    # ch:销毁句柄 | Destroy handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print (f"destroy handle fail! ret[0x{ret}]")
        sys.exit()
