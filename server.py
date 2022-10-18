import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 3888


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    return s


def handle_client(socket, clients):
    while True:
        conn, addr = socket.accept()
        conn.send('nick'.encode())
        nickname = conn.recv(1024).decode()
        clients[addr] = (conn, nickname)

        server_messages(clients, addr)

        thread_handle_message = Thread(target=handle_message, args=(clients, addr))
        thread_handle_message.start()


def server_messages(clients, addr):
    nickname = get_nickname(clients, addr)
    conn = get_connection(clients, addr)

    print(f'Client {nickname} joined')
    message = f'Hello {nickname} from server to client'
    conn.send(message.encode())
    broadcast(f'{nickname} joined to server', clients, addr)


def get_nickname(clients, addr):
    nickname = clients[addr][1]
    return nickname


def get_connection(clients, addr):
    conn = clients[addr][0]
    return conn


def handle_message(clients, addr):
    nickname = get_nickname(clients, addr)
    conn = get_connection(clients, addr)

    while True:
        try:
            received_data = conn.recv(1024)
            if not received_data:
                broadcast(f'{nickname} left from server', clients, addr)
                del clients[addr]
                break

            message = received_data.decode()
            broadcast(message, clients, addr)
        except:
            del clients[addr]
            break


def broadcast(message, clients, addr):
    connection = get_connection(clients, addr)

    for conn, _ in clients.values():
        if conn != connection:
            conn.send(message.encode())


def main():
    clients = dict()

    socket = create_socket()
    thread_handle_client = Thread(target=handle_client, args=(socket, clients))

    thread_handle_client.start()
    thread_handle_client.join()


if __name__ == "__main__":
    main()
