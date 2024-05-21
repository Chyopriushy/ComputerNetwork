import socket
import threading
import json
import sys

def receive_messages(sock):
    while True:
        try:
            conn, addr = sock.accept()
            message = conn.recv(1024).decode()
            if message.startswith("user_list"):
                _, user_list_json = message.split(',', 1)
                global users
                users = json.loads(user_list_json)
                print("Online users:")
                for user in users:
                    print(user)
            else:
                print(message)
            conn.close()
        except:
            break

def show_options():
    print("\nOptions: ")
    print("1. Message a user")
    print("2. Create chat room")
    print("3. Join chat room")
    print("4. Leave chat room")
    print("5. Exit")
    option = input("Choose an option: ")
    return option

def main():
    global users
    user_id = input("Enter your ID: ")

    # 소켓 생성 및 바인딩
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', 0))
    listen_socket.listen(5)
    ip, port = listen_socket.getsockname()
    print(f"Your IP: {ip}")
    print(f"Your port: {port}")

    # 로그인 서버에 연결
    server_ip = '127.0.0.1'
    server_port = 5000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_ip, server_port))
    conn.send(f'login,{user_id},{ip},{port}'.encode())
    conn.close()

    # 메시지 송수신 스레드 시작
    threading.Thread(target=receive_messages, args=(listen_socket,)).start()

    in_chat_room = False
    in_private_chat = False
    current_chat_room = None
    current_private_user = None

    while True:
        if in_chat_room:
            message = input()
            if message == "/leave":
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'leave_room,{current_chat_room},{user_id}'.encode())
                response = conn.recv(1024).decode()
                if "Left room" in response:
                    in_chat_room = False
                    current_chat_room = None
                print(response)
                conn.close()
                continue
            else:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'send_message,{current_chat_room},{user_id},{message}'.encode())
                conn.close()
                continue
        elif in_private_chat:
            message = input()
            if message == "/leave":
                in_private_chat = False
                current_private_user = None
                print("Left private chat")
                continue
            else:
                target_ip, target_port = users[current_private_user]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as msg_socket:
                    msg_socket.connect((target_ip, target_port))
                    msg_socket.send(f'{user_id}@private: {message}'.encode())
                continue
        else:
            option = show_options()

            if option == '1':
                target_user = input("Enter the user ID to message: ")
                if target_user in users:
                    current_private_user = target_user
                    in_private_chat = True
                    print(f"Started private chat with {target_user}")
                    continue
                else:
                    print(f"User {target_user} not found.")

            elif option == '2':
                room_name = input("Enter chat room name: ")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'create_room,{room_name}'.encode())
                response = conn.recv(1024).decode()
                print(response)
                conn.close()
                continue

            elif option == '3':
                room_name = input("Enter chat room name to join: ")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'join_room,{room_name},{user_id}'.encode())
                response = conn.recv(1024).decode()
                if "Joined room" in response:
                    in_chat_room = True
                    current_chat_room = room_name
                print(response)
                conn.close()
                continue

            elif option == '4':
                if in_chat_room:
                    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn.connect((server_ip, server_port))
                    conn.send(f'leave_room,{current_chat_room},{user_id}'.encode())
                    response = conn.recv(1024).decode()
                    if "Left room" in response:
                        in_chat_room = False
                        current_chat_room = None
                    print(response)
                    conn.close()
                    continue
                elif in_private_chat:
                    in_private_chat = False
                    current_private_user = None
                    print("Left private chat")
                    continue

            elif option == '5':
                print("Exiting...")
                sys.exit()

if __name__ == "__main__":
    users = {}
    main()