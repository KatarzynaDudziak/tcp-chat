import socket
from enum import Enum
from socket import timeout
from threading import Thread, Event
from queue import Queue, Empty

from message import Message, Type


class EventType(Enum):
    ServerClient = 1
    MessageToServer = 2


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = list()
        self.q = Queue()
        self.builder = Builder()

    def start_server(self):
        try:
            print('Waiting for clients...')
            stop_event = Event()
            client_handler = ClientHandler(self.host, self.port, self.q, stop_event)
            client_handler.start()
            while True:
                try:
                    event, event_type = self.q.get(timeout=0.1)
                    if event_type == EventType.ServerClient:
                        self.handle_client(event)
                        event.start()
                    elif event_type == EventType.MessageToServer:
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
            self.remove_user(event)
            self.send_client_left_message(event)
            print(f'Client {event.nickname} left') 
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
        client.conn.send(self.builder.build_welcome_message(client.nickname))

    def send_message_about_client_join(self, client):
        message = self.builder.build_message_about_client_join(client.nickname)
        self.broadcast(message, client.conn)

    def send_client_left_message(self, client):
        message = self.builder.build_client_left_message(client.nickname)
        self.broadcast(message, client.sender)

    def broadcast(self, message, conn):
        for client in self.clients:
            if client.conn != conn:
                client.conn.send(message)


class ClientHandler(Thread):
    def __init__(self, host, port, q, event):
        super().__init__()
        self.host = host
        self.port = port
        self.q = q
        self.create_socket()
        self.event = event

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(1)

    def accept_client(self):
        try:
            conn, addr = self.socket.accept()
            conn.settimeout(1)
            message = Message()
            conn.send(message.encode_nickname())
            nickname = conn.recv(1024).decode()
            server_client = ServerClient(conn, addr, nickname, self.q, self.event)
            self.q.put((server_client, EventType.ServerClient))
        except timeout:
            pass

    def run(self):
        self.socket.listen()
        while not self.event.is_set():
            self.accept_client()


class MessageToServer:
    def __init__(self, message, sender, nickname):
        self.message = message
        self.sender = sender
        self.nickname = nickname


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
                    self.trigger_remove_client()
                    return                 
            except timeout:
                continue
            except ConnectionResetError:
                self.trigger_remove_client()
                return
            else:
                message = received_data
                self.queue_message(message)              

    def trigger_remove_client(self):
        message = 'left'
        self.queue_message(message)
    
    def queue_message(self, message):
        obj_message = MessageToServer(message, self.conn, self.nickname)
        self.q.put((obj_message, EventType.MessageToServer))

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


class Builder:
    def __init__(self):
        pass

    def build_welcome_message(self, nickname):
        obj_message = Message()
        obj_message.message = f'Hello {nickname}. Enjoy your conversation :)'
        obj_message.author = 'INFO'
        obj_message.type = Type.INFO
        return obj_message.encode()
    
    def build_message_about_client_join(self, nickname):
        obj_message = Message()
        obj_message.message = f'{nickname} joined to server'
        obj_message.author = 'INFO'
        obj_message.type = Type.INFO
        return obj_message.encode()
    
    def build_client_left_message(self, nickname):
        obj_message = Message()
        obj_message.message = f'{nickname} has left the server'
        obj_message.author = 'INFO'
        obj_message.type = Type.INFO
        return obj_message.encode()


def main():
    host = '127.0.0.1'
    port = 3819

    server = Server(host, port)
    server.start_server()


if __name__ == "__main__":
    main()
