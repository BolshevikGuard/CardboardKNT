import socket

SERVER_IP = 'IP'  # 服务器端电脑 B 的 IP 地址
PORT = 12345  # 端口号，与服务器端保持一致

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_IP, PORT))
    print("已连接到服务器，输入消息发送，输入 'exit' 退出")

    while True:
        message = input("请输入消息: ")
        client_socket.sendall(message.encode())
        if message.strip().lower() == "exit":
            print("发送退出命令，断开连接")
            break
