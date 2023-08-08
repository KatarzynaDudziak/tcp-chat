import sys
import time
from queue import Queue, Empty
from threading import Event
import speech_recognition

from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog, QScrollBar
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6 import uic

from client import Client
from message import Message


class Worker(QObject):
    received_message = pyqtSignal(Message)

    def __init__(self, q, stop_event):
        super().__init__()
        self.q = q
        self.stop_event = stop_event

    @pyqtSlot()
    def do_work(self):
        while not self.stop_event.is_set():
            try:
                item = self.q.get(timeout=0.1)
            except Empty:
                continue
            else:
                self.received_message.emit(item)


class WorkerSR(QObject):
    recv = pyqtSignal(str)

    def __init__(self):
        super().__init__()
 
    @pyqtSlot()
    def do_work(self):
        message = self.record_message()
        self.recv.emit(message)

    def record_message(self):
        recognizer = speech_recognition.Recognizer()

        with speech_recognition.Microphone() as source:
            audio_text = recognizer.listen(source)
            try:
                return recognizer.recognize_google(audio_text, language = 'pl-PL')
            except speech_recognition.UnknownValueError:
                print('Didn\'t understand')
            except speech_recognition.RequestError:
                print('Sorry, speech recognition failed')
        return ''


class MainWindow(QMainWindow):
    work_requested = pyqtSignal()

    def __init__(self, nickname, q):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.stop_event = Event()
        self.client = None
        self.nickname = nickname
        self.scroll_bar = QScrollBar(self)
        self.setWindowTitle('CHAT')
        self.textBrowser.append(f'Welcome {self.nickname}! Let\'s talk.')
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setVerticalScrollBar(self.scroll_bar)
        self.pushButtonSend.setCheckable(True)
        self.lineEdit.returnPressed.connect(self.send_message)
        self.pushButtonSend.clicked.connect(self.send_message)
        self.worker = Worker(q, self.stop_event)
        self.speech_recognizer = WorkerSR()
        self.worker_thread = QThread()
        self.second_thread = QThread()

        self.worker.moveToThread(self.worker_thread)
        self.speech_recognizer.moveToThread(self.second_thread)

        self.work_requested.connect(self.worker.do_work)
        self.work_requested.connect(self.speech_recognizer.do_work)

        self.worker.received_message.connect(self.handle_message)
        self.speech_recognizer.recv.connect(self.handle_sr_message)
        
        self.worker_thread.start()
        self.pushButton.clicked.connect(self.second_thread.start)
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

    def handle_sr_message(self, message: str):
        user_message = self.create_message_obj()
        user_message.message = message
        self.client.write_message(user_message)
        self.append_message(user_message)

    def closeEvent(self, event):
        if self.client:
            self.stop_event.set()
            self.worker_thread.quit()
            self.second_thread.quit()
            self.worker_thread.wait()
            self.second_thread.wait()
            self.client.stop()
        QMainWindow.closeEvent(self, event)


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
