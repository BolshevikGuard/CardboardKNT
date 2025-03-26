import requests
import json
import time
import socket

class CenterControl():
    def __init__(self):
        self.client_socket = None
        self.running = False

    def run(self):
        print('hello from center control')
        # return
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        map_dict           = config['map_dict']
        devicePos          = config['devicePos']
        startPos           = devicePos
        taskpath           = config['taskpath']
        AGV_IP             = config['AGV_IP']
        config['orderId'] += 1
        orderId            = config['orderId']
        SERVER_IP          = config['SERVER_IP']
        PORT               = config['PORT']
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        addTask_ip_address = f'http://{AGV_IP}:7000/ics/taskOrder/addTask'
        deviceInfo_ip_address = f'http://{AGV_IP}:7000/ics/out/device/list/deviceInfo'
        controlDevice_ip_address = f'http://{AGV_IP}:7000/ics/out/controlDevice'

        pause_time = 1

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
            'orderId'     : f'{orderId}',
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
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_IP, PORT))
        print('server connected!')

        task_response = requests.post(addTask_ip_address, headers=headers, data=json.dumps(task_data))

        # 检查响应状态码
        if task_response.status_code == 200:
            # 如果请求成功，解析JSON数据
            task_response_data = task_response.json()

            # 检查返回的code是否为1000（成功）
            if task_response_data['code'] == 1000:
                print("请求成功")
                
                while self.running:
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
                                requests.post(controlDevice_ip_address, headers=headers, data=json.dumps(pause_data))
                                time.sleep(pause_time)
                                self.client_socket.sendall(b's')
                                time.sleep(pause_time)
                                requests.post(controlDevice_ip_address, headers=headers, data=json.dumps(act_data))
                        else:
                            print(info_response_data['desc'])

                    else:
                        print(f"{info_response.status_code} {info_response.text}")            
            else:
                print(f"{task_response_data['code']} {task_response_data['desc']}")
        else:
            print(f"{task_response.status_code} {task_response.text}")
    
    def stop(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.sendall(b'e')
                self.client_socket.close()
                print('Disconnected!')
            except Exception as e:
                print(f'Error when disconnecting: {e}')

if __name__ == '__main__':
    rcc = CenterControl()
    rcc.run()