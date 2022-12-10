from PyQt6.QtWidgets import QApplication, QPushButton, QTextBrowser, QTextEdit, QMainWindow, QInputDialog, QLineEdit, QMessageBox
from PyQt6 import uic
import sys
import re
from client import Client


class MainWindow(QMainWindow):
    def __init__(self, nickname):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.nickname = nickname

        self.setWindowTitle('Chat')
        self.client = Client('127.0.0.1', 3888, self.nickname)    
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(True)
        self.pushButtonSend.setCheckable(True)
        self.pushButtonSend.clicked.connect(self.append_message)

    def append_message(self):
        message = self.textEdit.toPlainText()
        self.client.write_message(message)
        if self.is_not_empty(message):
            message = re.sub('\n+', ' ', message)
            self.textBrowser.append(message)
        self.textEdit.clear()
    
    def is_not_empty(self, message):
        if message != '' and message.strip() != '': 
            return True
        
    def closeEvent(self, event):
        self.client.stop()
        QMainWindow.closeEvent(self, event)


def main():
    app = QApplication(sys.argv)
    nickname, ok = QInputDialog().getText(None, 'user', 'nickname')
    if ok and nickname:
        window = MainWindow(nickname)
        window.show()
        app.exec()


if __name__=='__main__':
    main()
