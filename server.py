import socket, time, sys
import threading
from threading import Thread, Event


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = dict()

    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        return s

    def handle_clients(self, socket):
        while True:
            self.handle_one_client(socket)

    def handle_one_client(self, socket):
        addr = self.accept_client(socket)

        thread_handle_message = Thread(target=self.handle_messages, args=(addr, ))
        thread_handle_message.start()

    def accept_client(self, socket):
        conn, addr = socket.accept()
        conn.send('nick'.encode())
        nickname = conn.recv(1024).decode()
        self.clients[addr] = (conn, nickname)
        self.send_server_messages_on_client_join(addr)
        return addr

    def send_server_messages_on_client_join(self, addr):
        nickname = self.get_nickname(addr)
        conn = self.get_connection(addr)
        print(f'Client {nickname} joined')
        message = f'Hello {nickname} from server to client'
        conn.send(message.encode())
        self.broadcast(f'{nickname} joined to server', addr)

    def get_nickname(self, addr):
        nickname = self.clients[addr][1]
        return nickname

    def get_connection(self, addr):
        conn = self.clients[addr][0]
        return conn

    def handle_messages(self, addr):
        while addr in self.clients:
            self.handle_messages_for_client(addr)

    def handle_messages_for_client(self, addr):
        nickname = self.get_nickname(addr)
        conn = self.get_connection(addr)
        self.handle_received_data(addr, nickname, conn)

    def handle_received_data(self, addr, nickname, conn):
        try:
            self.received_data = conn.recv(1024)
            if not self.received_data:
                self.broadcast(f'{nickname} has left the server', addr)
                del self.clients[addr]
                return
        except:
            self.broadcast(f'{nickname} has left the server', addr)
            del self.clients[addr]
            return

        message = self.received_data.decode()
        self.broadcast(message, addr)

    def broadcast(self, message, addr):
        connection = self.get_connection(addr)

        for conn, addr in self.clients.values():
            if conn != connection:
                conn.send(message.encode())


def main():
    host = '127.0.0.1'
    port = 3889

    server = Server(host, port)
    socket = server.create_socket()
    try:
        thread_handle_clients = Thread(target=server.handle_clients, args=(socket, ))
        thread_handle_clients.start()
        while thread_handle_clients.is_alive():
            thread_handle_clients.join(1)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
