import socket
import time
import sys
import threading
from threading import Thread
from message import Message
import queue


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = list()
        self.q = queue.Queue()

    def start_server(self):
        try:
            client_handler = ClientHandler(self.host, self.port, self.q)
            client_handler.start()
            # while client_handler.is_alive():
            #     client_handler.join(1)
            while True:
                event = self.q.get()
                if isinstance(event, ServerClient):
                    self.clients.append(event)
                    self.send_server_messages(event.addr)
                    event.start()
                elif isinstance(event, MessageToServer):
                    if event.message == 'left':
                        print('client left')
                    else:
                        print('new message')
                        self.broadcast(event.message, event.sender)
                else:
                    pass #todo
        
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
        for client in self.clients:
            if client.addr == addr:
                return client.nickname

    def get_connection(self, addr):
        for client in self.clients:
            if client.addr == addr:
                return client.conn

    def build_client_left_message(self, nickname):
        client_left = Message()
        client_left.message = f'{nickname} has left the server'
        client_left.author = 'server'
        enc_message = client_left.encode()
        return enc_message

    def broadcast(self, message, conn):
        for client in self.clients:
            if client.conn != conn:
                client.conn.send(message)

 
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
        server_client = ServerClient(conn, addr, nickname, self.q)
        self.q.put(server_client)
        
    def run(self):
        self.socket.listen()
        while True:
            self.accept_client()


class MessageHandler(Thread):
    def __init__(self, conn, q):
        super().__init__()
        self.conn = conn
        self.q = q

    # def handle_messages(self):
    #     while self.addr in self.clients:
    #         self.handle_messages_for_client(addr)
    
    # def handle_messages_for_client(self):
    #     nickname = self.get_nickname()
    #     conn = self.get_connection()
    #     self.handle_received_data()

    def handle_received_data(self):
        # client_left = self.build_client_left_message(nickname)
        while True:
            try:
                received_data = self.conn.recv(1024)
                if not received_data:
                    # print(f'Client {nickname} left the server')
                    # self.broadcast(client_left, addr)
                    # del self.clients[addr]
                    # return
                    message = 'left'
                    print('Recv data is empty')
                    obj_message = MessageToServer(message, self.conn)
                    self.q.put(obj_message)
                    return
            except:
                # self.broadcast(client_left, addr)
                # print(f'Client {nickname} left the server')
                # del self.clients[addr]
                # return
                message = 'left'
                print('left due to exception')
                obj_message = MessageToServer(message, self.conn)
                self.q.put(obj_message)
                return

            message = received_data
            obj_message = MessageToServer(message, self.conn)
            self.q.put(obj_message)
        
    def run(self):
        self.handle_received_data()


class ServerClient:
    def __init__(self, conn, addr, nickname, q):
        self.conn = conn
        self.addr = addr
        self.nickname = nickname
        self.q = q
        self.message_handler = MessageHandler(conn, q)

    def start(self):
        self.message_handler.start()


class MessageToServer:
    def __init__(self, message, sender):
        self.message = message
        self.sender = sender


def main():
    host = '127.0.0.1'
    port = 3889

    server = Server(host, port)
    server.start_server()


if __name__ == "__main__":
    main()
