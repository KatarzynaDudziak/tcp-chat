import sys
from queue import Queue

from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6 import uic

from client import Client
from message import Message


class MainWindow(QMainWindow):
    work_requested = pyqtSignal()

    def __init__(self, nickname, q):
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
        self.worker = Worker(q)
        self.worker_thread = QThread()

        self.worker.moveToThread(self.worker_thread)

        self.work_requested.connect(self.worker.do_work)
        self.worker.received_message.connect(self.handle_message)

        self.worker_thread.start()
        self.work_requested.emit()

    def set_client(self, client):
        self.client = client

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
        self.textBrowser.append(f'{user_message.publication_date} {user_message.author}: {user_message.message}')

    def closeEvent(self, event):
        if self.client:
            self.client.stop()
        QMainWindow.closeEvent(self, event)


class Worker(QObject):
    received_message = pyqtSignal(Message)

    def __init__(self, q):
        super().__init__()
        self.q = q

    @pyqtSlot()
    def do_work(self):
        while True:
            item = self.q.get()
            self.received_message.emit(item)


def main():
    app = QApplication(sys.argv)
    nickname, ok = QInputDialog().getText(None, 'USER', 'NICKNAME')
    q = Queue()
    if ok and nickname:
        window = MainWindow(nickname, q)
        client = Client('127.0.0.1', 3819, nickname, q)
        window.set_client(client)
        window.show()
        sys.exit(app.exec())

if __name__=='__main__':
    main()
