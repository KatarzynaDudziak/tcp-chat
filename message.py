import json
import struct

from datetime import datetime
from enum import IntEnum


class Type(IntEnum):
    USER = 1
    INFO = 2
    WARNING = 3


class Message:
    NICK = 'nick'

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

    def encode_message(self):
        message = self.convert_to_str()
        message_length = len(message)
        header = struct.pack('!I', message_length)
        return (header + message.encode())
    
    def encode_nickname(self, NICK):
        message_length = len(NICK)
        header = struct.pack('!I', message_length)
        return (header + NICK.encode())
