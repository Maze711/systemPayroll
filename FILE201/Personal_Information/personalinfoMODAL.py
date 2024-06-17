from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
import sys

class personalModal(QMainWindow):
    def __init__(self):
        super(personalModal, self).__init__()
        self.setFixedSize(1153,665)
        loadUi("personalinfoMODAL.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = personalModal()
    ui.show()
    app.exec_()