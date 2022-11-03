import socket
from threading import Thread


def create_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return client


def receive_message(nickname, client):
    try:
        message = True
        while message:  # if message == -1 then connection is closed
            message = client.recv(1024).decode()
            if message == 'nick':
                client.send(nickname.encode())
            else:
                print(message)
    except Exception as ex:
        print(ex)
        client.close()


def write_message(client, nickname):
    while True:
        try:
            message = f'{nickname}: {input()}'
            client.send(message.encode())
        except:
            print('Cannot send message')
            client.close()


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
