from socket import timeout
import socket
from threading import Thread, Event
from message import Message
from message import Type
from queue import Queue, Empty
from enum import Enum


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = list()
        self.q = Queue()

    def start_server(self):
        try:
            print('Waiting for clients...')
            stop_event = Event()
            client_handler = ClientHandler(self.host, self.port, self.q, stop_event)
            client_handler.start()
            while True:
                try:
                    event, event_type = self.q.get(timeout=0.1)
                    if event_type == Event_Type.ServerClient:
                        self.handle_client(event)
                        event.start()
                    elif event_type == Event_Type.MessageToServer:
                        self.handle_message(event)
                except Empty:
                    pass
        except KeyboardInterrupt:
            stop_event.set()
            client_handler.join()

    def handle_client(self, event):
        self.clients.append(event)
        self.send_server_messages(event)

    def handle_message(self, event):
        if event.message == 'left':
            left_message = self.build_client_left_message(event)
            print(f'Client {event.nickname} left')
            self.broadcast(left_message, event.sender)
            self.remove_user(event)
        else:
            self.broadcast(event.message, event.sender)
            
    def remove_user(self, event):
        for client in self.clients:
            if client.conn == event.sender:
                self.clients.remove(client)

    def send_server_messages(self, client):
        print(f'Client {client.nickname} joined')
        self.send_welcome_message(client)
        self.send_message_about_client_join(client)

    def send_welcome_message(self, client):
        obj_message = Message()
        obj_message.message = f'Hello {client.nickname} from server to client'
        obj_message.author = 'INFO'
        obj_message.type = Type.INFO
        enc_message = obj_message.encode()
        client.conn.send(enc_message)

    def send_message_about_client_join(self, client):
        obj_message = Message()
        obj_message.message = f'{client.nickname} joined to server'
        obj_message.author = 'INFO'
        obj_message.type = Type.INFO
        enc_message = obj_message.encode()
        self.broadcast(enc_message, client.conn)

    def build_client_left_message(self, client):
        client_left = Message()
        client_left.message = f'{client.nickname} has left the server'
        client_left.author = 'INFO'
        client_left.type = Type.INFO
        enc_message = client_left.encode()
        return enc_message

    def broadcast(self, message, conn):
        for element in self.clients:
            if element.conn != conn:
                element.conn.send(message)

 
class Event_Type(Enum):

    ServerClient = 1
    MessageToServer = 2


class ClientHandler(Thread):
    def __init__(self, host, port, q, event):
        super().__init__()
        self.host = host
        self.port = port
        self.q = q
        self.create_socket()
        self.event = event

    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        self.socket = s
        self.socket.settimeout(1)

    def accept_client(self):
        try:
            conn, addr = self.socket.accept()
            conn.settimeout(1)
            conn.send('nick'.encode())
            nickname = conn.recv(1024).decode()
            server_client = ServerClient(conn, addr, nickname, self.q, self.event)
            self.q.put((server_client, Event_Type.ServerClient))
        except timeout:
            pass
        
    def run(self):
        self.socket.listen()
        while not self.event.is_set():
            self.accept_client()


class MessageHandler(Thread):
    def __init__(self, conn, nickname, q, event):
        super().__init__()
        self.conn = conn
        self.nickname = nickname
        self.q = q
        self.event = event

    def handle_received_data(self):
        while not self.event.is_set():
            try:
                received_data = self.conn.recv(1024)
                if not received_data:
                    raise Exception()
            except timeout:
                continue
            except:
                message = 'left'
                self.queue_message(message)
                return

            message = received_data
            self.queue_message(message)
    
    def queue_message(self, message):
        obj_message = MessageToServer(message, self.conn, self.nickname)
        self.q.put((obj_message, Event_Type.MessageToServer))

    def run(self):
        self.handle_received_data()
        self.conn.close()


class ServerClient:
    def __init__(self, conn, addr, nickname, q, event):
        self.conn = conn
        self.addr = addr
        self.nickname = nickname
        self.q = q
        self.event = event
        self.message_handler = MessageHandler(conn, nickname, q, event)

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
