import socket
from threading import Thread


def create_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    return s


def handle_clients(socket, clients):
    while True:
        handle_one_client(socket, clients)


def handle_one_client(socket, clients):
    addr = accept_client(socket, clients)
        
    thread_handle_message = Thread(target=handle_messages, args=(clients, addr))
    thread_handle_message.start()


def accept_client(socket, clients):
    conn, addr = socket.accept()
    conn.send('nick'.encode())
    nickname = conn.recv(1024).decode()
    clients[addr] = (conn, nickname)
    send_server_messages_on_client_join(clients, addr)
    return addr


def send_server_messages_on_client_join(clients, addr):
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


def handle_messages(clients, addr):
    while len(clients) > 0:
        handle_messages_for_client(clients, addr)


def handle_messages_for_client(clients, addr):
    nickname = get_nickname(clients, addr)
    conn = get_connection(clients, addr)

    handle_received_data(clients, addr, nickname, conn)


def handle_received_data(clients, addr, nickname, conn):
    received_data = conn.recv(1024)
    if not received_data:
        broadcast(f'{nickname} left from server', clients, addr)
        del clients[addr]
        return

    message = received_data.decode()
    broadcast(message, clients, addr)


def broadcast(message, clients, addr):
    connection = get_connection(clients, addr)

    for conn, addr in clients.values():
        if conn != connection:
            conn.send(message.encode())


def main():
    HOST = '127.0.0.1'
    PORT = 3888
    clients = dict()

    socket = create_socket(HOST, PORT)
    thread_handle_clients = Thread(target=handle_clients, args=(socket, clients))

    thread_handle_clients.start()
    thread_handle_clients.join()


if __name__ == "__main__":
    main()
