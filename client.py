import socket
from threading import Thread
from message import Message
from message import Type
from queue import Queue
import struct


class Client:
    conn = None
    
    def __init__(self, host, port, nickname):
        self.host = host
        self.port = port
        self.create_client()
        self.nickname = nickname
        self.q = Queue()

        self.receive_thread = Thread(target=self.receive_message)
        self.receive_thread.start()

    def create_client(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

    def receive_message(self):
        try:
            while True:
                self.handle_recv_message()
        except:
            obj_message = Message()
            obj_message.message = f'The connection has been interrupt. Please try to connect again in a moment.'
            obj_message.author = 'WARNING'
            obj_message.type = Type.WARNING
            if self.q:
                self.q.put(obj_message)

    def decode(self):
        header = self.conn.recv(4)
        message_length = struct.unpack('!I', header)[0]
        recv_message = self.conn.recv(message_length).decode()
        return recv_message

    def handle_recv_message(self):
        recv_message = None
        try:
            recv_message = self.decode()
        except:
            raise Exception()
        if not recv_message:
            raise Exception()
        if recv_message == 'nick':
            self.conn.send(self.nickname.encode())
        else:
            message = Message()
            message.convert_to_obj(recv_message)
            if self.q:
                self.q.put(message)
    
    def get_queue(self):
        return self.q
            
    def write_message(self, message):
        try:
            self.send_message_to_server(message)
        except:
            self.conn.close()

    def send_message_to_server(self, message):
        message_to_send = message.encode()
        self.conn.send(message_to_send)

    def stop(self):
        self.conn.close()
        self.receive_thread.join()
