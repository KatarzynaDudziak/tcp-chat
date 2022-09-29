import socket
import threading

clients = {}

HOST = '127.0.0.1'
PORT = 3891


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    return s


def add_client(socket):
    client, address = socket.accept()
    client.send('nick'.encode())
    nickname = client.recv(1024).decode()
    clients[nickname] = client

    print(f'Client {nickname}, has joined us with address: {address}')
    message = f"Hello {nickname} from server to client"
    client.send(message.encode())

    thread = threading.Thread(target=handle, args=(client,))
    thread.start()

    return client, nickname


def handle(client, nickname):
    while True:
        try:
            message = client.recv(1024).decode()
            broadcast(message)
        except:
            clients.pop(nickname)
            client.close()


def broadcast(message):
    for client in clients:
        client.send(message.encode())


def main():
    socket = create_socket()
    client, nickname = add_client(socket)
    handle(client, nickname)


if __name__ == "__main__":
    main()