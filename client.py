import socket
import threading
import json




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

def getOptions():
    print("\n원하시는 항목을 선택하십시오: ")
    print("1. 개인채팅")
    print("2. 단톡방 생성")
    print("3. 단톡방 참가")
    print("4. 나가기\n")
    option = input()
    return option

def main():
    global users
    id = input("아이디 입력 하시오: ")


    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', 0))
    listen_socket.listen(5)
    ip, port = listen_socket.getsockname()
    print(f"IP: {ip}")
    print(f"Port Number: {port}")


    server_ip = '127.0.0.1'
    server_port = 5000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_ip, server_port))
    conn.send(f'로그인,{id},{ip},{port}'.encode())
    print(f"{id}님이 로그인 하셨습니다")
    conn.close()


    threading.Thread(target=receive_messages, args=(listen_socket,), daemon=True).start()


    checkChatRoom = False
    checkPrivateChat = False
    currChatRoom = None
    curr1vs1User = None

    while True:
        if checkChatRoom:
            message = input()
            if message == "/leave":
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'방 떠남,{currChatRoom},{id}'.encode())
                response = conn.recv(1024).decode()
                if "Left OK" in response:
                    checkChatRoom = False
                    currChatRoom = None
                print(f"{id}님이 방에서 나갔습니다.")
                conn.close()
                continue

            else:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'send_message,{currChatRoom},{id},{message}'.encode())
                conn.close()
                continue
        elif checkPrivateChat:
            message = input()
            if message == "/leave":
                checkPrivateChat = False
                curr1vs1User = None
                print("개인 채팅에서 나갑니다")
                continue
            else:
                oppo_ip, oppo_port = users[curr1vs1User]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as msg_socket:
                    msg_socket.connect((oppo_ip, oppo_port))
                    msg_socket.send(f'{id}@개인채팅: {message}'.encode())
                continue
        else:
            option = getOptions()

            if option == '1':
                target_user = input("개인 채팅을 원하는 상대의 ID를 입력하시오: ")
                if target_user in users:
                    curr1vs1User = target_user
                    checkPrivateChat = True
                    print(f"{target_user}님과의 개인채팅을 시작합니다")
                    continue
                else:
                    print(f"{target_user}님은 온라인 상에 없습니다.")

            elif option == '2':
                room_name = input("생성할 방의 제목을 입력하시오: ")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'방 생성,{room_name},{id}'.encode())
                response = conn.recv(1024).decode()
                if "Create OK" in response:
                    checkChatRoom = True
                    currChatRoom = room_name
                    print(f"{room_name}에 입장합니다")
                else:
                    print(response)
                conn.close()
                continue

            elif option == '3':
                room_name = input("참여할 방의 제목을 입력하세요: ")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))
                conn.send(f'방 참가,{room_name},{id}'.encode())
                response = conn.recv(1024).decode()
                if "Join room OK" in response:
                    checkChatRoom = True
                    currChatRoom = room_name
                    print(f"{room_name}에 입장합니다.")
                else:
                    print(response)
                conn.close()
                continue

            elif option == '4':
                print("메신저 프로그램을 종료합니다.")
                exit(0)



if __name__ == "__main__":
    users = {}
    main()