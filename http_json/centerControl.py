import requests
import json
import keyboard
import time
import socket

map_dict = {'10000016': 'B003',
            '10000015': 'B002',
            '10000014': 'B001',
            '10000027': 'D002',
            '10000017': 'C001',
            '10000018': 'C002',
            '10000019': 'C003',
            '10000029': 'D001'}
devicePos = 10000016
taskpath = '10000015,10000014,10000027,10000017,10000018,10000019,10000029,10000016'
IP = ''

addTask_ip_address = f'http://{IP}:7000/ics/taskOrder/addTask'
deviceInfo_ip_address = f'http://{IP}:7000/ics/out/device/list/deviceInfo'
controlDevice_ip_address = f'http://{IP}:7000/ics/out/controlDevice'

orderId = '83'
pause_time = 2

# 请求头，指定Content-Type为application/json
headers = {'Content-Type': 'application/json'}

# JSON数据
task_data = {
    'modelProcessCode': 'cruiseMove',
    'priority'        : 6,
    'fromSystem'      : 'PC',
    'orderId'         : orderId,
    'taskOrderDetail' : [
        {
            'taskPath': taskpath
        }
    ]
}

info_data = {
    "areaId"    : "1",
    "deviceType": "0"
}

pause_data = {
    "areaId"      : "1",
    'deviceNumber': 'AGV1',
    'all'         : 0,
    'orderId'     : orderId,
    'controlWay'  : 0,
    'stopType'    : 0
}

act_data = {
    "areaId"      : "1",
    'deviceNumber': 'AGV1',
    'all'         : 0,
    'orderId'     : orderId,
    'controlWay'  : 1
}

# 连接工控机服务端
SERVER_IP = ''
PORT = 12345
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_IP, PORT))
    print('server connected!')

task_response = requests.post(addTask_ip_address, headers=headers, data=json.dumps(task_data))

# 检查响应状态码
if task_response.status_code == 200:
    # 如果请求成功，解析JSON数据
    task_response_data = task_response.json()

    # 检查返回的code是否为1000（成功）
    if task_response_data['code'] == 1000:
        print("请求成功")
        
        while(True):
            # 发送POST请求
            info_response = requests.post(deviceInfo_ip_address, headers=headers, data=json.dumps(info_data))

            # 检查响应状态码
            if info_response.status_code == 200:
                # 如果请求成功，解析JSON数据
                info_response_data = info_response.json()

                # 检查返回的code是否为1000（成功）
                if info_response_data['code'] == 1000:
                    task_info = info_response_data['data'][0]  # 获取任务信息
                    
                    # 到达各个预设点位
                    if task_info['devicePosition'] != devicePos and str(task_info['devicePosition']) in map_dict.keys():

                        # 回报位置并暂停若干秒 拍摄照片
                        devicePos = task_info['devicePosition']
                        print(f'reach position {devicePos} aka {map_dict[str(devicePos)]}')
                        pause_response = requests.post(controlDevice_ip_address, headers=headers, data=json.dumps(pause_data))
                        time.sleep(pause_time)
                        client_socket.sendall('s')
                        time.sleep(pause_time)
                        act_response = requests.post(controlDevice_ip_address, headers=headers, data=json.dumps(act_data))
                else:
                    print(info_response_data['desc'])

            else:
                print(f"{info_response.status_code} {info_response.text}")
            
            if keyboard.is_pressed('esc'):
                client_socket.sendall('e')
                client_socket.close()
                exit()
                
    
    else:
        print(f"{task_response_data['code']} {task_response_data['desc']}")
else:
    print(f"{task_response.status_code} {task_response.text}")
