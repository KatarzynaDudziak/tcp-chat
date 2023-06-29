import socket
from threading import Thread
from message import Message
from message import Type
import struct


class Client:
    connection = None
    
    def __init__(self, host, port, nickname, receive_callback):
        self.host = host
        self.port = port
        self.create_client()
        self.nickname = nickname
        self.receive_callback = receive_callback

        self.receive_thread = Thread(target=self.receive_message)
        self.receive_thread.start()

    def create_client(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))

    def receive_message(self):
        try:
            while True:
                self.handle_recv_message()
        except:
            obj_message = Message()
            obj_message.message = f'The connection has been interrupt. Please try to connect again in a moment.'
            obj_message.author = 'WARNING'
            obj_message.type = Type.WARNING
            if self.receive_callback:
                self.receive_callback(obj_message)

    def handle_recv_message(self):
        recv_message = None
        try:
            header = self.connection.recv(4)
            message_length = struct.unpack('!I', header)[0]
            recv_message = self.connection.recv(message_length).decode()
        except Exception as ex:
            raise Exception()
        if not recv_message:
            raise Exception()
        if recv_message == 'nick':
            self.connection.send(self.nickname.encode())
        else:
            message = Message()
            message.convert_to_obj(recv_message)
            if self.receive_callback:
                self.receive_callback(message)

    def write_message(self, message):
        try:
            self.send_message_to_server(message)
        except Exception as ex:
            print('close')
            self.connection.close()

    def send_message_to_server(self, message):
        message_length = len(message.convert_to_str())
        header = struct.pack('!I', message_length)
        message_to_send = (header + message.convert_to_str().encode())
        self.connection.send(message_to_send)

    def stop(self):
        self.connection.close()
        self.receive_thread.join()
