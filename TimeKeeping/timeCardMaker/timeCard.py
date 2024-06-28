import sys
import os
import logging
import time  # Importing the time module
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow
from PyQt5.uic import loadUi

# Configure the logger
#logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    #format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class timecard(QDialog):
    def __init__(self, filtered_data):
        super().__init__()
        self.setFixedSize(1153, 665)
        #loadUi(os.path.join(os.path.dirname(__file__), 'timecard.ui'), self)
        ui_file = (resource_path("TimeKeeping\\timeCardMaker\\timecard.ui"))
        loadUi(ui_file, self)

        self.filtered_data = filtered_data
        self.populateTimeList()

    def populateTimeList(self):
        self.TimeListTable.clearContents()
        self.TimeListTable.setRowCount(len(self.filtered_data))

        for row_index, row_data in enumerate(self.filtered_data):
            for col_index, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.TimeListTable.setItem(row_index, col_index, item)
