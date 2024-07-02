import sys
import os

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow, QLineEdit
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class chkSched(QDialog):
    def __init__(self):
        super(chkSched, self).__init__()
        self.setFixedSize(731, 409)
        ui_file = (resource_path("TimeKeeping\\Schedule.ui"))
        loadUi(ui_file, self)