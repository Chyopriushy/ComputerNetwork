import socket
import threading
import sys

def getMessage():
    recv_message = client_socket.recv(1024)
    if recv_message:
        print(recv_message, flush=True)


def sendMessage():
    while True:
        message = input(">>>")
        if message == "exit":
            print("메신저 프로그램을 종료하겠습니다")
            client_socket.sendall("exit".encode())
            client_socket.close()
            sys.exit()
        else:
            client_socket.sendall(message.encode())

while True:
    id = input("Enter ID: ")

    if len(id) == 0:
        print("ID is empty")
        continue

    while True:
        host, port = "localhost", 9999
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        # id 넘기기
        client_socket.send(id.encode())

        get_thread = threading.Thread(target=getMessage)
        get_thread.start()

        sent_thread = threading.Thread(target=sendMessage)
        sent_thread.start()

