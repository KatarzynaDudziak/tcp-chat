from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QTextEdit, QMainWindow, QInputDialog, QLineEdit, QMessageBox
from PyQt6 import uic
import sys
import re
from client import Client


class MainWindow(QMainWindow):
    def __init__(self, nickname):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.client = None
        self.nickname = nickname
        self.setWindowTitle('Chat')
        self.textBrowser.append('Welcome in chat')
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(True)
        self.pushButtonSend.setCheckable(True)
        self.pushButtonSend.clicked.connect(self.send_message)

    def set_client(self, client):
        self.client = client

    def send_message(self):
        if not self.client:
            return
        message = self.textEdit.toPlainText()
        self.client.write_message(message)
        if self.not_empty(message):
            message = re.sub('\n+', ' ', message)
            self.append_message(message)
        return message
        
    def append_message(self, message):
        self.textBrowser.append(f'{self.client.nickname}: {message}')
        self.textEdit.clear()
    
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
    nickname, ok = QInputDialog().getText(None, 'user', 'nickname')
    client = Client('127.0.0.1', 3889, nickname)
    if ok and nickname:
        window = MainWindow(nickname)
        window.set_client(client)
        client.set_callback(window.handle_message)
        window.show()
        app.exec()


if __name__=='__main__':
    main()
