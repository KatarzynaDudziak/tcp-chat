from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt6 import uic
import sys
from client import Client
from message import Message, Type
from queue import Empty
from threading import Thread
import time


class MainWindow(QMainWindow):
    def __init__(self, nickname):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.client = None
        self.nickname = nickname
        self.setWindowTitle('CHAT')
        self.textBrowser.append(f'Welcome {self.nickname}! Let\'s talk.')
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(True)
        self.pushButtonSend.setCheckable(True)
        self.lineEdit.returnPressed.connect(self.send_message)
        self.pushButtonSend.clicked.connect(self.send_message)

    def set_client(self, client):
        self.client = client
        
    def run(self, q):
        message_receiver = MessageReceiver(q, self.handle_message)
        message_receiver.daemon = True
        message_receiver.start()

    def send_message(self):
        if not self.client:
            return
        user_message = self.create_message_obj()
        if self.not_empty(user_message.message):
            self.client.write_message(user_message)
            self.append_message(user_message)

    def create_message_obj(self):
        user_message = Message()
        user_message.message = self.lineEdit.text()
        user_message.author = self.client.nickname
        return user_message

    def append_message(self, user_message):
        self.textBrowser.append(f'{user_message.publication_date} {user_message.message}')
        self.lineEdit.clear()

    def not_empty(self, message):
        return message.strip() != ''
    
    def handle_message(self, user_message):
        if user_message.type == Type.WARNING:
             self.pushButtonSend.clicked.disconnect()
        try:
           self.textBrowser.append(f'{user_message.publication_date} {user_message.author}: {user_message.message}')
        except Exception as ex:
             print(ex)

    def closeEvent(self, event):
        if self.client:
            self.client.stop()
        QMainWindow.closeEvent(self, event)


class MessageReceiver(Thread):
    def __init__(self, q, handle_message):
        super().__init__()
        self.q = q
        self.handle_message = handle_message

    def get_message(self):
        while True:
            try:
                item = self.q.get()
            except Empty:
                continue
            else:
                self.handle_message(item)

    def run(self):
        self.get_message()


def main():
    app = QApplication(sys.argv)
    nickname, ok = QInputDialog().getText(None, 'USER', 'NICKNAME')
    if ok and nickname:
        window = MainWindow(nickname)
        client = Client('127.0.0.1', 3819, nickname)
        window.run(client.get_queue())
        window.set_client(client)
        window.show()
        sys.exit(app.exec())

if __name__=='__main__':
    main()
