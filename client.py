import socket
import threading
import json
import sys


def receive_messages(sock):
    while True:
        try:
            conn, addr = sock.accept()
            message = conn.recv(1024).decode()
            if message.startswith("\n현재 온라인"):
                _, user_list_json = message.split(',', 1)
                global users
                users = json.loads(user_list_json)
                print("온라인 유저:")
                for user in users:
                    print(user)
                print()
            else:
                print(message)
            conn.close()
        except:
            break

def show_options():
    print("\n원하시는 항목을 선택하십시오: ")
    print("1. 개인채팅")
    print("2. 단톡방 생성")
    print("3. 단톡방 참가")
    print("4. 단톡방 나가기")
    print("5. 나가기\n")
    option = input()
    return option

def main():
    global users
    user_id = input("아이디 입력 하시오: ")

    # 소켓 생성 및 바인딩
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', 0))
    listen_socket.listen(5)
    ip, port = listen_socket.getsockname()
    print(f"IP: {ip}")
    print(f"Port Number: {port}")

    # 로그인 서버에 연결
    server_ip = '127.0.0.1'
    server_port = 5000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_ip, server_port))
    conn.send(f'login,{user_id},{ip},{port}'.encode())
    print(f"{user_id}님이 로그인 하셨습니다")
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
                print("개인 채팅에서 나갑니다")
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
                    print(f"{target_user}님과의 개인채팅을 시작합니다")
                    continue
                else:
                    print(f"{target_user}님은 온라인 상에 없습니다.")

            elif option == '2':
                room_name = input("생성할 방의 제목을 입력하시오: ")
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
                print(f"{room_name}에 입장합니다.")
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
                    print(f"{current_chat_room}을 떠납니다")
                    conn.close()
                    continue
                elif in_private_chat:
                    in_private_chat = False
                    current_private_user = None
                    print()
                    continue

            elif option == '5':
                print("Exiting...")
                sys.exit()

if __name__ == "__main__":
    users = {}
    main()