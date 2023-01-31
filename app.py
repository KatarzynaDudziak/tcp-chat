from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QLineEdit, QMainWindow, QInputDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt, QCoreApplication
import sys
import re
from client import Client
from datetime import datetime
from message import Message


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
        date = datetime.now()
        user_message = Message()
        user_message.publication_date = date.strftime(f"[%Y-%m-%d %H:%M:%S]")
        user_message.message = self.lineEdit.text()
        user_message.author = self.client.nickname
        if self.not_empty(user_message.message):
            message = re.sub('\n+', ' ', user_message.message)
        self.client.write_message(user_message)
        self.append_message(user_message)
        return user_message
  
    def append_message(self, user_message):
        self.textBrowser.append(f'{user_message.publication_date} {user_message.author} {user_message.message}')
        self.lineEdit.clear()

    def not_empty(self, message):
        if message.strip() != '':
            return True
    
    def handle_message(self, user_message):
        self.textBrowser.append(f'{user_message.publication_date} {user_message.author} {user_message.message}')

    def closeEvent(self, event):
        if self.client:
            self.client.stop()
        QMainWindow.closeEvent(self, event)


def main():
    app = QApplication(sys.argv)
    nickname, ok = QInputDialog().getText(None, 'USER', 'NICKNAME')
    if ok and nickname:
        client = Client('127.0.0.1', 3889, nickname)
        window = MainWindow(nickname)
        window.set_client(client)
        client.set_callback(window.handle_message)
        window.show()
        app.exec()
    QCoreApplication.quit()

if __name__=='__main__':
    main()
