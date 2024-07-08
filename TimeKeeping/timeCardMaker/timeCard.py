import sys
import os
import mysql.connector
from mysql.connector import Error

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QPushButton, QMessageBox
from PyQt5.uic import loadUi
from TimeKeeping.schedValidator.checkSched import chkSched
from TimeKeeping.timeSheet.timeSheet import TimeSheet
# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_connection():
    try:
        connection = mysql.connector.connect(
            #host='127.0.0.1',
            host='localhost',
            database='file201',
            user='root',
            password=''
        )
        if connection.is_connected():
            logging.info("Connected to MySQL database")
            return connection
        else:
            logging.info("Failed to connect to MySQL database")
            return None
    except Error as e:
        logging.exception("Error while connecting to MySQL: %s", e)
        return None

class timecard(QDialog):
    def __init__(self, filtered_data, from_date_str, to_date_str):
        super().__init__()
        self.setFixedSize(1345, 665)
        #loadUi(os.path.join(os.path.dirname(__file__), 'timecard.ui'), self)
        ui_file = (resource_path("TimeKeeping\\timeCardMaker\\timecard.ui"))
        loadUi(ui_file, self)

        self.filtered_data = filtered_data

        # Make the column headers fixed size
        self.TimeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeListTable.horizontalHeader().setStretchLastSection(True)

        self.lblFrom = self.findChild(QLabel, 'lblFrom')
        self.lblTo = self.findChild(QLabel, 'lblTo')
        self.lblFrom.setText(from_date_str)
        self.lblTo.setText(to_date_str)

        self.timeSheetButton = self.findChild(QPushButton, 'btnTimeSheet')
        self.timeSheetButton.clicked.connect(self.createTimeSheet)

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
        selected_row = self.TimeListTable.currentRow()

        if selected_row != -1:
            empNum = self.TimeListTable.item(selected_row, 0).text()
            bioNum = self.TimeListTable.item(selected_row, 1).text()
            empName = self.TimeListTable.item(selected_row, 2).text()
            trans_date = self.TimeListTable.item(selected_row, 3).text()
            checkIn = self.TimeListTable.item(selected_row, 5).text()
            checkOut = self.TimeListTable.item(selected_row, 6).text()
            sched = self.TimeListTable.item(selected_row, 7).text()

            data = (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched)

            dialog = chkSched(data)
            dialog.exec_()
        else:
            QMessageBox.warning(
                self,
                "No Row Selected",
                "Please select a row from the table first!"
            )

    def createTimeSheet(self):
        dialog = TimeSheet()
        dialog.exec_()