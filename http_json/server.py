import socket

HOST = '0.0.0.0'  # 监听所有网络接口
PORT = 12345  # 端口号，可自定义

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # 允许一个客户端连接
    print(f"服务器启动，等待客户端连接...")

    conn, addr = server_socket.accept()
    with conn:
        print(f"客户端已连接: {addr}")
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"收到: {data}")
            if data.strip().lower() == "exit":
                print("收到退出命令，关闭连接")
                break
        conn.close()
