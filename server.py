import socket
from threading import Thread


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        return s

    def handle_clients(self, socket, clients):
        while True:
            self.handle_one_client(socket, clients)

    def handle_one_client(self, socket, clients):
        addr = self.accept_client(socket, clients)
        
        thread_handle_message = Thread(target=self.handle_messages, args=(clients, addr))
        thread_handle_message.start()

    def accept_client(self, socket, clients):
        conn, addr = socket.accept()
        conn.send('nick'.encode())
        nickname = conn.recv(1024).decode()
        clients[addr] = (conn, nickname)
        self.send_server_messages_on_client_join(clients, addr)
        return addr

    def send_server_messages_on_client_join(self, clients, addr):
        nickname = self.get_nickname(clients, addr)
        conn = self.get_connection(clients, addr)
        print(f'Client {nickname} joined')
        message = f'Hello {nickname} from server to client'
        conn.send(message.encode())
        self.broadcast(f'{nickname} joined to server', clients, addr)

    def get_nickname(self, clients, addr):
        nickname = clients[addr][1]
        return nickname

    def get_connection(self, clients, addr):
        conn = clients[addr][0]
        return conn

    def handle_messages(self, clients, addr):
        while addr in clients:
            self.handle_messages_for_client(clients, addr)

    def handle_messages_for_client(self, clients, addr):
        nickname = self.get_nickname(clients, addr)
        conn = self.get_connection(clients, addr)
        self.handle_received_data(clients, addr, nickname, conn)

    def handle_received_data(self, clients, addr, nickname, conn):
        try:
            self.received_data = conn.recv(1024)
            if not self.received_data:
                self.broadcast(f'{nickname} has left the server', clients, addr)
                del clients[addr]
                return
        except:
            self.broadcast(f'{nickname} has left the server', clients, addr)
            del clients[addr]
            return

        message = self.received_data.decode()
        self.broadcast(message, clients, addr)

    def broadcast(self, message, clients, addr):
        connection = self.get_connection(clients, addr)

        for conn, addr in clients.values():
            if conn != connection:
                conn.send(message.encode())


def main():
    HOST = '127.0.0.1'
    PORT = 3889
    clients = dict()

    server = Server(HOST, PORT)
    socket = server.create_socket()
    thread_handle_clients = Thread(target=server.handle_clients, args=(socket, clients))

    thread_handle_clients.start()
    thread_handle_clients.join()


if __name__ == "__main__":
    main()
