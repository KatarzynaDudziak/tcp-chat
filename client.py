import socket
import struct
from message import Message, Type
from queue import Queue
from threading import Thread


class Client:
    def __init__(self, host, port, nickname, q):
        self.host = host
        self.port = port
        self.create_client()
        self.nickname = nickname
        self.q = q

        self.receive_thread = Thread(target=self.receive_message)
        self.receive_thread.start()

    def create_client(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

    def receive_message(self):
        try:
            while True:
                self.handle_recv_message()
        except ConnectionAbortedError:
            obj_message = Message()
            obj_message.message = f'The connection has been interrupt. Please try to connect again in a moment.'
            obj_message.author = 'WARNING'
            obj_message.type = Type.WARNING
            if self.q:
                self.q.put(obj_message)

    def decode(self) -> str:
        header = self.conn.recv(4)
        message_length = struct.unpack('!I', header)[0]
        recv_message = self.conn.recv(message_length).decode()
        return recv_message

    def handle_recv_message(self):
        # FIXME:
        # 1. Do not use general Exceptions, check the particular ones and raise them if needed instead
        # Maybe raising is not needed - we might want to just "do something" when particular exception occurs;
        # no reason to crash the program itself.
        # 2. 
        recv_message = self.decode()

        if recv_message == 'nick':
            self.conn.send(self.nickname.encode())
            return
        message = Message()
        message.convert_to_obj(recv_message)
        if self.q:
            self.q.put(message)

    def write_message(self, message):
        self.send_message_to_server(message)

    def send_message_to_server(self, message):
        message_to_send = message.encode()
        self.conn.send(message_to_send)

    def stop(self):
        self.conn.close()
        self.receive_thread.join()
