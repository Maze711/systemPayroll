import sys
import os
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PaytimeSheet(QMainWindow):

    def __init__(self, data, fromDate, toDate):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = (resource_path("TimeKeeping\\paytimeSheet\\paytimesheet.ui"))
        loadUi(ui_file, self)

        self.data = data

        # Make the column headers fixed size
        self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.lblFrom.setText(fromDate)
        self.lblTo.setText(toDate)

        self.populatePaytimeSheetTable(self.data)


    def populatePaytimeSheetTable(self, data):
        self.paytimesheetTable.setRowCount(len(data))

        for i, row in enumerate(data):
            bio_num_item = QTableWidgetItem(row['BioNum'])
            present_days_item = QTableWidgetItem(str(row['Present Days']))
            present_holidays_item = QTableWidgetItem(str(row['Present Holidays']))

            # Centers the all the item
            for item in [bio_num_item, present_days_item, present_holidays_item]:
                item.setTextAlignment(Qt.AlignCenter)

            self.paytimesheetTable.setItem(i, 1, bio_num_item)
            self.paytimesheetTable.setItem(i, 5, present_days_item)
            self.paytimesheetTable.setItem(i, 7, present_holidays_item)