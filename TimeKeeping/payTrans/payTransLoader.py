import sys
import os
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView, QLineEdit
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PayTrans(QDialog):
    def __init__(self):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = (resource_path("TimeKeeping\\payTrans\\paytrans.ui"))
        loadUi(ui_file, self)