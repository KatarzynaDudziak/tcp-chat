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
            while True:
                event = self.q.get()
                if isinstance(event, ServerClient):
                    self.clients.append(event)
                    self.send_server_messages(event)
                    event.start()
                elif isinstance(event, MessageToServer):
                    if event.message == 'left':
                        self.build_client_left_message(event)
                        print(f'Client {event.nickname} left')
                        for client in self.clients:
                            if client.conn == event.sender:
                                self.clients.remove(client)
                    else:
                        self.broadcast(event.message, event.sender)
                else:
                    pass #todo
        except KeyboardInterrupt:
            sys.exit()

    def send_server_messages(self, client):
        print(f'Client {client.nickname} joined')
        self.send_welcome_message(client)
        self.send_message_about_client_join(client)

    def send_welcome_message(self, client):
        obj_message = Message()
        obj_message.message = f'Hello {client.nickname} from server to client'
        obj_message.author = 'server'
        enc_message = obj_message.encode()
        client.conn.send(enc_message)

    def send_message_about_client_join(self, client):
        obj_message = Message()
        obj_message.message = f'{client.nickname} joined to server'
        obj_message.author = 'server'
        enc_message = obj_message.encode()
        self.broadcast(enc_message, client.conn)

    def build_client_left_message(self, client):
        client_left = Message()
        client_left.message = f'{client.nickname} has left the server'
        client_left.author = 'server'
        enc_message = client_left.encode()
        return enc_message

    def broadcast(self, message, conn):
        for element in self.clients:
            if element.conn != conn:
                element.conn.send(message)

 
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
    def __init__(self, conn, nickname, q):
        super().__init__()
        self.conn = conn
        self.nickname = nickname
        self.q = q

    def handle_received_data(self):
        while True:
            try:
                received_data = self.conn.recv(1024)
                if not received_data:
                    message = 'left'
                    obj_message = MessageToServer(message, self.conn, self.nickname)
                    self.q.put(obj_message)
                    return
            except:
                message = 'left'
                obj_message = MessageToServer(message, self.conn, self.nickname)
                self.q.put(obj_message)
                return

            message = received_data
            obj_message = MessageToServer(message, self.conn, self.nickname)
            self.q.put(obj_message)
        
    def run(self):
        self.handle_received_data()


class ServerClient:
    def __init__(self, conn, addr, nickname, q):
        self.conn = conn
        self.addr = addr
        self.nickname = nickname
        self.q = q
        self.message_handler = MessageHandler(conn, nickname, q)

    def start(self):
        self.message_handler.start()


class MessageToServer:
    def __init__(self, message, sender, nickname):
        self.message = message
        self.sender = sender
        self.nickname = nickname


def main():
    host = '127.0.0.1'
    port = 3889

    server = Server(host, port)
    server.start_server()


if __name__ == "__main__":
    main()
