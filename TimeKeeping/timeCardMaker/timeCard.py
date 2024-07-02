import sys
import os
import logging
import time  # Importing the time module
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow, QLineEdit
from PyQt5.uic import loadUi
from TimeKeeping.checkSched import chkSched

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
    def __init__(self, filtered_data, from_date_str, to_date_str):
        super().__init__()
        self.setFixedSize(1345, 665)
        #loadUi(os.path.join(os.path.dirname(__file__), 'timecard.ui'), self)
        ui_file = (resource_path("TimeKeeping\\timeCardMaker\\timecard.ui"))
        loadUi(ui_file, self)

        self.filtered_data = filtered_data

        self.lblFrom = self.findChild(QLabel, 'lblFrom')
        self.lblTo = self.findChild(QLabel, 'lblTo')
        self.lblFrom.setText(from_date_str)
        self.lblTo.setText(to_date_str)

        # Add search functionality
        self.searchBioNum = self.findChild(QLineEdit, 'txtSearch')
        self.searchBioNum.textChanged.connect(self.searchBioNumFunction)

        self.btnCheckSched.clicked.connect(self.CheckSched)

        self.populateTimeList(self.filtered_data)

    def populateTimeList(self, data):
        self.TimeListTable.clearContents()
        self.TimeListTable.setRowCount(len(data))

        for row_index, row_data in enumerate(data):
            for col_index, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.TimeListTable.setItem(row_index, col_index, item)

    def searchBioNumFunction(self):
        search_text = self.searchBioNum.text().strip()
        if not search_text:
            self.populateTimeList(self.filtered_data)
            return

        filtered_data = [row for row in self.filtered_data if row['BioNum'].startswith(search_text)]
        self.populateTimeList(filtered_data)

    def CheckSched(self):
        dialog = chkSched()
        dialog.exec_()

