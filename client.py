import socket
from threading import Thread


nickname = input("Write your nickname: ") 

HOST = '127.0.0.1'
PORT = 3888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive_message():
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


def write_message(client):
    while True:
        try:
            message = f'{nickname}: {input()}'
            client.send(message.encode())
        except:
            print('cannot send message')
            client.close()


def main():

    receive_thread = Thread(target=receive_message, )
    receive_thread.start()
    write_message(client)   


if __name__ == "__main__":
    main()