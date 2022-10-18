import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 3891


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

        print(f'Client {nickname} joined')                      # te 4 linie aż proszą się o zamknięcie w funkcję i nazwanie tego kawałka, nawet
        message = f'Hello {nickname} from server to client'     # oddzieliłaś je pustymi liniami, czyli tworzą jakąś logiczną całość
        conn.send(message.encode())
        broadcast(f'{nickname} joined to server', clients, conn)

        thread_handle_message = Thread(target=handle_message, args=(conn, addr,nickname, clients,  ))
        thread_handle_message.start()


def handle_message(conn, addr, nickname, clients):  # gdy znamy addr (klucz) to conn i nickname można wyciągnąć ze słownika clients,
    while True:                                     # nie trzeba ich przekazywać w parametrach.
        try:                                        # W tym celu możesz napisać funkcje pomocnicze np. get_nickname() i get_connection() podając
            received_data = conn.recv(1024)         # w parametrach słownik oraz klucz (czyli addr)
            if not received_data:
                broadcast(f'{nickname} left from server', clients, conn)
                del clients[addr]
                break

            message = received_data.decode()
            broadcast(message, clients, conn)
        except:
            conn.close()                            # w tym przypadku nie usuniemy klienta ze słownika ani nie poinformujemy innych, a chcielibyśmy
            break


def broadcast(message, clients, connection):
    for conn, _ in clients.values():
        if conn != connection:
            conn.send(message.encode())


def main():
    clients = dict()

    socket = create_socket()
    thread_handle_client = Thread(target=handle_client, args=(socket, clients))   # to samo co na początku, przecinek jest zbędny

    thread_handle_client.start()
    thread_handle_client.join()

if __name__ == "__main__":
    main()
