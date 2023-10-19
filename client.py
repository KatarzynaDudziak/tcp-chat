import socket
import struct
from threading import Thread, Event
from message import Message, Type


class Client:
    def __init__(self, host, port, nickname, q):
        self.host = host
        self.port = port
        self.create_socket()
        self.nickname = nickname
        self.q = q
        self.stop_event = Event()
    
        self.receive_thread = MessageHandler(self.conn, self.q, self.nickname, self.stop_event)
        self.receive_thread.start()

    def create_socket(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.settimeout(0.1)
        self.conn.connect((self.host, self.port))

    def write_message(self, message):
        self.send_message_to_server(message)

    def send_message_to_server(self, message):
        message_to_send = message.encode()
        self.conn.send(message_to_send)

    def stop(self):
        self.stop_event.set()
        self.receive_thread.join()
        self.conn.close()


def get_message(conn):
    header = conn.recv(4)
    if header == b'':
        raise ConnectionAbortedError

    message_length = struct.unpack('!I', header)[0]
    recv_message = conn.recv(message_length).decode()
    return recv_message


class MessageHandler(Thread):
    def __init__(self, conn, q, nickname, event):
        super().__init__()
        self.conn = conn
        self.q = q
        self.nickname = nickname
        self.event = event

    def receive_message(self):
        try:
            self.handle_recv_message()
        except ConnectionAbortedError:
            obj_message = Message()
            obj_message.message = f'The connection has been interrupted. Please try to connect again in a moment.'
            obj_message.author = 'WARNING'
            obj_message.type = Type.WARNING
            if self.q:
                self.q.put(obj_message)
            return
        except socket.timeout:
            pass

    def handle_recv_message(self):
        recv_message = get_message(self.conn)

        if recv_message == 'nick':
            self.conn.send(self.nickname.encode())
            return
        if recv_message == None:
            return
        message_obj = Message()
        message_obj.convert_to_obj(recv_message)
        if self.q:
            self.q.put(message_obj)
    
    def run(self):
        while not self.event.is_set():
            self.receive_message()
        self.conn.close()
