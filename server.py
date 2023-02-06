import socket
import time
import sys
import threading
from threading import Thread, Event
from message import Message
import queue


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = dict()
        self.q = queue.Queue()

    def start_server(self):
        try:
            client_handler = ClientHandler(self.host, self.port, self.q)
            client_handler.start()
            while True:
                event = self.q.get()
                if isinstance(event, ServerClient):
                    # MessageHandler(event)
                    print(f'client {event.nickname} connected')
                else:
                    pass #todo
        #     while client_handler.is_alive():
        #         client_handler.join(1)
        except KeyboardInterrupt:
            sys.exit()

    def send_server_messages(self, addr):
        nickname = self.get_nickname(addr)
        conn = self.get_connection(addr)
        print(f'Client {nickname} joined')
        self.send_welcome_message(nickname, conn)
        self.send_message_about_client_join(nickname, addr)

    def send_welcome_message(self, nickname, conn):
        obj_message = Message()
        obj_message.message = f'Hello {nickname} from server to client'
        obj_message.author = 'server'
        enc_message = obj_message.encode()
        conn.send(enc_message)

    def send_message_about_client_join(self, nickname, addr):
        obj_message = Message()
        obj_message.message = f'{nickname} joined to server'
        obj_message.author = 'server'
        enc_message = obj_message.encode()
        self.broadcast(enc_message, addr)

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
        client_left = self.build_client_left_message(nickname)
        try:
            self.received_data = conn.recv(1024)
            if not self.received_data:
                self.broadcast(client_left, addr)
                del self.clients[addr]
                return
        except:
            self.broadcast(client_left, addr)
            print(f'{nickname} has left the server')
            del self.clients[addr]
            return

        message = self.received_data
        self.broadcast(message, addr)
    
    def build_client_left_message(self, nickname):
        client_left = Message()
        client_left.message = f'{nickname} has left the server'
        client_left.author = 'server'
        enc_message = client_left.encode()
        return enc_message

    def broadcast(self, message, addr):
        connection = self.get_connection(addr)

        for conn, addr in self.clients.values():
            if conn != connection:
                conn.send(message)


class ClientHandler(Thread):
    def __init__(self, host, port, q):
        super().__init__()
        self.host = host
        self.port = port
        self.q = q
        self.create_socket()

    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        self.socket = s

    def accept_client(self):
        conn, addr = self.socket.accept()
        conn.send('nick'.encode())
        nickname = conn.recv(1024).decode()
        server_client = ServerClient(conn, addr, nickname)
        self.q.put(server_client)
        
    def run(self):
        self.socket.listen()
        while True:
            self.accept_client()


class MessageHandler(Thread):
    def __init__(self, server_client):
        super().__init__()
        self.server_client = server_client

    def run(self):
        pass


class ServerClient:
    def __init__(self, conn, addr, nickname):
        self.conn = conn
        self.addr = addr
        self.nickname = nickname


def main():
    host = '127.0.0.1'
    port = 3889

    server = Server(host, port)
    server.start_server()


if __name__ == "__main__":
    main()
