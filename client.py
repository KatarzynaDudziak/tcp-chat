import socket
import threading

nickname = input("Write your nickname: ") 

HOST = '127.0.0.1'
PORT = 3891


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive_message(client):
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'nick':
                client.send(nickname.encode())
            else:
                print(message)
        except:
            print('error')
            client.close()


def write_message(client):
    while True:
        message = f'{nickname}: {input()}'
        client.send(message.encode())


def main():
    receive_thread = threading.Thread(target=receive_message, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write_message, args=(client,))
    write_thread.start()

if __name__ == "__main__":
    main()