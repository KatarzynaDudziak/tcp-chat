from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QLineEdit, QMainWindow, QInputDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt, QCoreApplication
import sys
import re
from client import Client
from datetime import datetime
from message import Message
from message import Type


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

    def send_message(self):
        if not self.client:
            return
        user_message = self.create_message_obj()
        if self.not_empty(user_message.message):
            message = re.sub('\n+', ' ', user_message.message)
            self.client.write_message(user_message)
            self.append_message(user_message)

    def create_message_obj(self):
        date = datetime.now()
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
        self.textBrowser.append(f'{user_message.publication_date} {user_message.author}: {user_message.message}')

    def closeEvent(self, event):
        if self.client:
            self.client.stop()
        QMainWindow.closeEvent(self, event)


def main():
    app = QApplication(sys.argv)
    nickname, ok = QInputDialog().getText(None, 'USER', 'NICKNAME')
    if ok and nickname:
        window = MainWindow(nickname)
        client = Client('127.0.0.1', 3889, nickname, window.handle_message)
        window.set_client(client)
        window.show()
        app.exec()
    QCoreApplication.quit()

if __name__=='__main__':
    main()
