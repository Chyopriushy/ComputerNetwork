import socket
import threading
import json

clients = {}
chat_rooms = {}

def sendList():
    user_list_json = json.dumps(clients)
    for user, (ip, port) in clients.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((ip, port))
                sock.send(f"\n현재 온라인,{user_list_json}".encode())
        except:
            continue

def notifyNewMember(room_name, message):
    if room_name in chat_rooms:
        for user in chat_rooms[room_name]:
            if user in clients:
                ip, port = clients[user]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip, port))
                    sock.send(message.encode())

def handleClient(client_socket, client_address):
    global clients, chat_rooms
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            info = message.split(',')
            if info[0] == '로그인':
                id, ip, port = info[1], info[2], info[3]
                clients[id] = (ip, int(port))
                sendList()
            elif info[0] == '방 생성':
                room_name = info[1]
                if room_name not in chat_rooms:
                    chat_rooms[room_name] = []
                    response = f"{room_name}이 생성되었습니다."
                else:
                    response = f"{room_name}방이 이미 존재합니다."
                client_socket.send(response.encode())
            elif info[0] == '방 참가':
                room_name, id = info[1], info[2]
                if room_name in chat_rooms:
                    chat_rooms[room_name].append(id)
                    response = f"Join room OK {room_name}"
                    notifyNewMember(room_name, f"{id}님이 방에 참여하셨습니다.")
                else:
                    response = f"{room_name}이 존재하지 않습니다."
                client_socket.send(response.encode())
            elif info[0] == '방 떠남':
                room_name, id = info[1], info[2]
                if room_name in chat_rooms and id in chat_rooms[room_name]:
                    chat_rooms[room_name].remove(id)
                    response = f"Left OK {room_name}"
                    notifyNewMember(room_name, f"{id}님이 방을 떠났습니다..")
                else:
                    response = f"Not in room {room_name}"
                client_socket.send(response.encode())
            elif info[0] == 'send_message':
                room_name, id, msg = info[1], info[2], info[3]
                if room_name in chat_rooms:
                    for user in chat_rooms[room_name]:
                        if user in clients:
                            ip, port = clients[user]
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                                sock.connect((ip, port))
                                sock.send(f"{id}@{room_name}: {msg}".encode())
        except:
            break
    client_socket.close()

def main():
    server_ip = '0.0.0.0'
    server_port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print(f"서버 가동중 {server_ip}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        threading.Thread(target=handleClient, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()