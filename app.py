from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QLineEdit, QMainWindow, QInputDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt, QCoreApplication
import sys
import re
from client import Client
from datetime import datetime


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
        message = self.lineEdit.text()
        self.client.write_message(message)
        if self.not_empty(message):
            message = re.sub('\n+', ' ', message)
            self.append_message(message)
        return message
        
    def append_message(self, message):
        date = datetime.now()
        self.textBrowser.append(f'{self.client.nickname} : {message} {date.strftime(f"%Y-%m-%d %H:%M:%S")}')
        self.lineEdit.clear()
    
    def not_empty(self, message):
        if message.strip() != '': 
            return True
    
    def handle_message(self, message):
        self.textBrowser.append(message)

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
