import socket
import threading
import json

clients = {}
chat_rooms = {}

def send_user_list():
    user_list_json = json.dumps(clients)
    for user, (ip, port) in clients.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((ip, port))
                sock.send(f"\n현재 온라인,{user_list_json}".encode())
        except:
            continue

def notify_room_members(room_name, message):
    if room_name in chat_rooms:
        for user in chat_rooms[room_name]:
            if user in clients:
                ip, port = clients[user]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip, port))
                    sock.send(message.encode())

def handle_client(client_socket, client_address):
    global clients, chat_rooms
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            command = message.split(',')
            if command[0] == 'login':
                user_id, ip, port = command[1], command[2], command[3]
                clients[user_id] = (ip, int(port))
                send_user_list()
            elif command[0] == 'create_room':
                room_name = command[1]
                if room_name not in chat_rooms:
                    chat_rooms[room_name] = []
                    response = f"{room_name}이 생성되었습니다."
                else:
                    response = f"{room_name}방이 이미 존재합니다."
                client_socket.send(response.encode())
            elif command[0] == 'join_room':
                room_name, user_id = command[1], command[2]
                if room_name in chat_rooms:
                    chat_rooms[room_name].append(user_id)
                    response = f"Joined room {room_name}"
                    notify_room_members(room_name, f"{user_id} has joined the room.")
                else:
                    response = f"Chat room {room_name} does not exist."
                client_socket.send(response.encode())
            elif command[0] == 'leave_room':
                room_name, user_id = command[1], command[2]
                if room_name in chat_rooms and user_id in chat_rooms[room_name]:
                    chat_rooms[room_name].remove(user_id)
                    response = f"Left room {room_name}"
                    notify_room_members(room_name, f"{user_id} has left the room.")
                else:
                    response = f"Not in room {room_name}"
                client_socket.send(response.encode())
            elif command[0] == 'send_message':
                room_name, user_id, msg = command[1], command[2], command[3]
                if room_name in chat_rooms:
                    for user in chat_rooms[room_name]:
                        if user in clients:
                            ip, port = clients[user]
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                                sock.connect((ip, port))
                                sock.send(f"{user_id}@{room_name}: {msg}".encode())
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
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()