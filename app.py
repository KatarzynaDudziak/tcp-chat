from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QTextEdit, QMainWindow, QInputDialog, QLineEdit
from PyQt6 import uic
import sys
from client import Client


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.setWindowTitle('Chat')
        self.show_popup()
        self.client = Client('127.0.0.1', 3888, self.nickname)    
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(True)
        self.pushButtonSend.setCheckable(True)
        self.pushButtonSend.clicked.connect(self.append_message)

    def append_message(self):
        message = self.textEdit.toPlainText()
        self.client.write_message(message)
        self.textBrowser.append(message)
        self.textEdit.clear()

    def show_popup(self):
        self.nickname, ok = QInputDialog().getText(self, 'user', 'nickname')
        if ok and self.nickname:
            self.textBrowser.append(f'{self.nickname}, welcome on the chat')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
