import socket
from threading import Thread


def create_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return client


def receive_message(nickname, client):
    try:
        while True:
            handle_recv_message(client, nickname)
    except Exception as ex:
        print(ex)
        client.close()


def handle_recv_message(client, nickname):
    message = client.recv(1024).decode()
    if not message:
        raise Exception
    if message == 'nick':
        client.send(nickname.encode())
    else:
        print(message)


def write_message(client, nickname):
    try:
        while True:
            send_message_to_server(client, nickname)
    except:
        print('Cannot send message')
        client.close()    


def send_message_to_server(client, nickname):
    message = f'{nickname}: {input()}'
    client.send(message.encode())


def main():
    nickname = input("Write your nickname: ") 

    HOST = '127.0.0.1'
    PORT = 3888

    client = create_client(HOST, PORT)
    receive_thread = Thread(target=receive_message, args=(nickname, client))
    receive_thread.start()
    write_message(client, nickname)   


if __name__ == "__main__":
    main()
