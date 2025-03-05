import requests
import json

# AGV设备的IP地址
ip_address = 'http://192.168.10.50:7000/ics/out/device/list/deviceInfo'

# 请求头，指定Content-Type为application/json
headers = {'Content-Type': 'application/json'}

# JSON数据
data = {
    "areaId"    : "1",
    "deviceType": "0"
}

devicePos = 10000016

map_dict = {'10000016': 'B003',
            '10000015': 'B002',
            '10000014': 'B001',
            '10000027': 'D002',
            '10000017': 'C001',
            '10000018': 'C002',
            '10000019': 'C003',
            '10000029': 'D001'}

while(True):
    # 发送POST请求
    response = requests.post(ip_address, headers=headers, data=json.dumps(data))

    # 检查响应状态码
    if response.status_code == 200:
        # 如果请求成功，解析JSON数据
        response_data = response.json()

        # 检查返回的code是否为1000（成功）
        if response_data['code'] == 1000:
            task_info = response_data['data'][0]  # 获取任务信息（假设data是一个列表）
            
            if task_info['devicePosition'] != devicePos and str(task_info['devicePosition']) in map_dict.keys():
                devicePos = task_info['devicePosition']
                print(f'reach position {devicePos} aka {map_dict[str(devicePos)]}')
        else:
            print("请求失败，错误信息:", response_data.get('desc', '未知错误'))
    else:
        print(f"请求失败, 状态码: {response.status_code}, 错误信息: {response.text}")