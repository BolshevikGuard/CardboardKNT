import socket

SERVER_IP = 'IP'  # 服务器端电脑 B 的 IP 地址
PORT = 12345  # 端口号，与服务器端保持一致

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_IP, PORT))
    print("server connected")

    while True:
        print("[s] take one round pics / [e] exit")
        message = input()
        client_socket.sendall(message.encode())
        if message.strip().lower() == "exit":
            print("disconnected!")
            break
