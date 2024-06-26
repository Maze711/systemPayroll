import sys
import os
import logging
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, \
    QTableWidget, QMainWindow
from PyQt5.uic import loadUi

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class timelogger(QMainWindow):
    def __init__(self, content):
        super().__init__()
        self.setFixedSize(1153, 665)
        loadUi(os.path.join(os.path.dirname(__file__), 'timeLog.ui'), self)

        self.content = content

        self.fromCalendar = self.findChild(QDateEdit, 'dateStart')
        self.toCalendar = self.findChild(QDateEdit, 'dateEnd')
        self.filterButton = self.findChild(QPushButton, 'btnFilter')
        self.employeeListTable = self.findChild(QTableWidget, 'employeeListTable')

        self.fromCalendar.setDate(QDate.currentDate())
        self.toCalendar.setDate(QDate.currentDate())

        self.filterButton.clicked.connect(self.showFilteredData)

        self.processContent()
        self.loadData()

    def processContent(self):
        self.data = []
        rows = self.content.strip().split('\n')
        for row in rows:
            columns = row.split('\t')
            if len(columns) < 6:
                logging.error(f"Row has missing columns: {row}")
                continue

            bio_no = columns[0].strip()
            trans_date, time = columns[1].strip().split(' ')
            mach_code = columns[2].strip()
            code_1 = columns[3].strip()
            code_2 = columns[4].strip()
            code_3 = columns[5].strip()

            self.data.append({
                'bio_no': bio_no,
                'trans_date': trans_date,
                'time': time,
                'mach_code': mach_code,
                'code_1': code_1,
                'code_2': code_2,
                'code_3': code_3
            })

    def loadData(self):
        try:
            self.populateTable(self.data)
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def showFilteredData(self):
        from_date = self.fromCalendar.date()
        to_date = self.toCalendar.date()

        filtered_data = [
            row for row in self.data
            if from_date <= QDate.fromString(row['trans_date'], "yyyy-MM-dd") <= to_date
        ]

        self.populateTable(filtered_data)

    def populateTable(self, data):
        self.employeeListTable.clearContents()
        self.employeeListTable.setRowCount(len(data))

        for row_position, row in enumerate(data):
            items = [
                QTableWidgetItem(row['bio_no']),
                QTableWidgetItem(row['trans_date']),
                QTableWidgetItem(row['time']),
                QTableWidgetItem(row['mach_code']),
                QTableWidgetItem(row['code_1']),
                QTableWidgetItem(row['code_2']),
                QTableWidgetItem(row['code_3'])
            ]
            for column, item in enumerate(items):
                self.employeeListTable.setItem(row_position, column, item)
