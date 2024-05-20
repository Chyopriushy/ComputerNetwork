import socket
import threading

def getMessage(recv_sock):
    while True:
        try:
            message = recv_sock.recv(1024).decode()
            if message:
                print(message)
            else:
                break
        except:
            print("Message Error : ")
            break

def client_connection(sock):
    while True:
        try:
            conn, addr = sock.accept()
            threading.Thread(target=getMessage, args=(conn,)).start()
        except:
            print("Connection Error : ")

def select_opt():
    print("1. 개인채팅\n 2. 그룹대화방 만들기\n 3. 그룹대화방 참가\n 4. 그룹대화방 나가기\n 5. 프로그램 종료")
    opt = int(input("Select your option : "))
    return opt


def messenger_program():

    # 로그인 준비하기
    id = input("ID를 입력하시오 : ")

    # 다른 사람들과 대화하기 위한 소켓 생성
    comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comm_socket.bind(("", 0))
    comm_socket.listen(5)
    client_ip, client_port = comm_socket.getsockname()

    # 로그인
    server_ip, server_port = '127.0.0.1', 10000
    login_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    login_socket.connect((server_ip, server_port))

    login_socket.sendall(f"{id}님이 로그인하셨습니다 ip_address: {client_ip}, port: {client_port}".encode())

    online_list = login_socket.recv(1024).decode()
    print(online_list)
    login_socket.close()

    threading.Thread(target=client_connection, args=(comm_socket,)).start()

    # 옵션추가 => ex) 채팅방 만들기, 참가, 퇴장, 나가기, 메세지 보내기 등등
    join_groupchat = False
    join_1vs1 = False
    client = None
    group = None

    while True:
        if join_groupchat:
            message = input("")
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((server_ip, server_port))
            conn.sendall(f"group message {group} {id} {message}".encode())
            conn.close()

        elif join_1vs1:
            message = input("")
            opp_ip, opp_port = online_list[client]
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((opp_ip, opp_port))
            conn.sendall(f"{id} : {message}".encode())

        else:
            option = select_opt()

            if option == 1:
                try:
                    opp_user = input("대화상태를 선택하세요")
                    if opp_user in online_list:
                        join_1vs1 = True
                        client = opp_user
                        print(f"{opp_user} 개인 대화 시작")
                except:
                    print("opt 1 : Error")

            elif option == 2:
                room_name = input("개설할 방의 제목을 입력하시오")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))

                conn.sendall(f"Create {room_name} {id}".encode())

                response = conn.recv(1024).decode()

                if not join_groupchat:
                    join_groupchat = True
                    group = room_name

                print(response)

            elif option == 3:
                room_name = input("들어가고 싶은 방을 입력하시오")
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server_ip, server_port))

                conn.sendall(f"Join room {room_name} : {id}".encode())
                response = conn.recv(1024).decode()

                if "Joined room" in response:
                    join_groupchat = True
                    group = room_name

                print(response)










if __name__ == "__main__":
    messenger_program()
