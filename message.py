import json
from datetime import datetime
from enum import IntEnum
import struct


class Message:
    def __init__(self):
        date = datetime.now()

        self.publication_date = date.strftime(f"[%Y-%m-%d %H:%M:%S]")
        self.author = None
        self.message = None
        self.type = Type.USER

    def convert_to_str(self):
        message = {"publication_date" : self.publication_date,
                   "author" : self.author,
                   "message" : self.message,
                   "type" : self.type}
        json_obj = json.dumps(message)
        return json_obj

    def convert_to_obj(self, json_obj):
        dict_obj = json.loads(json_obj)
        self.publication_date = dict_obj["publication_date"]
        self.author = dict_obj["author"]
        self.message = dict_obj["message"]
        self.type = Type(dict_obj["type"])

    def encode(self):
        message = self.convert_to_str()
        message_length = len(message)
        header = struct.pack('!I', message_length)
        return (header + message.encode())
    
    def encode_nickname(self):
        message = 'nick'
        message_length = len(message)
        header = struct.pack('!I', message_length)
        return (header + message.encode())


class Type(IntEnum):
    USER = 1
    INFO = 2
    WARNING = 3
