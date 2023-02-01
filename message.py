import json
from datetime import datetime

class Message:
    def __init__(self):
        date = datetime.now()

        self.publication_date = date.strftime(f"[%Y-%m-%d %H:%M:%S]")
        self.author = None
        self.message = None

    def convert_to_str(self):
        message = {"publication_date" : self.publication_date,
                   "author": self.author,
                   "message" : self.message}
        json_obj = json.dumps(message)
        return json_obj

    def convert_to_obj(self, json_obj):
        dict_obj = json.loads(json_obj)
        self.publication_date = dict_obj["publication_date"]
        self.author = dict_obj["author"]
        self.message = dict_obj["message"]

    def encode(self):
        return self.convert_to_str().encode()
