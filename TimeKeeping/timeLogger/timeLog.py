import sys
import os
import logging
import time  # Importing the time module
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow
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
        start_time = time.time()  # Start timing

        rows = self.content.strip().split('\n')
        self.data = []
        for row in rows:
            columns = row.split('\t')
            if len(columns) < 6:
                logging.error(f"Row has missing columns: {row}")
                continue

            try:
                bio_no, date_time, mach_code, code_1, code_2, code_3 = columns[:6]
                trans_date, time_value = date_time.split(' ')
            except ValueError as e:
                logging.error(f"Error parsing row: {row}, Error: {e}")
                continue

                # Determine sched based on code_1, code_2, code_3 values
            if code_1 == '0' and code_2 == '1' and code_3 == '0':
                sched = 'Time IN'
            elif code_1 == '1' and code_2 == '1' and code_3 == '0':
                sched = 'Time OUT'
            else:
                sched = 'Unknown'

            self.data.append({
                'bio_no': bio_no.strip(),
                'trans_date': trans_date.strip(),
                'time': time_value.strip(),
                'mach_code': mach_code.strip(),
                'sched': sched  # Store sched instead of code_1, code_2, code_3
            })

        end_time = time.time()  # End timing
        logging.info(f"processContent took {end_time - start_time:.4f} seconds")

    def loadData(self):
        start_time = time.time()  # Start timing

        try:
            self.populateTable(self.data)
        except Exception as e:
            logging.error(f"Error loading data: {e}")

        end_time = time.time()  # End timing
        logging.info(f"loadData took {end_time - start_time:.4f} seconds")

    def showFilteredData(self):
        start_time = time.time()  # Start timing

        from_date = self.fromCalendar.date()
        to_date = self.toCalendar.date()
        from_date_str = from_date.toString("yyyy-MM-dd")
        to_date_str = to_date.toString("yyyy-MM-dd")

        filtered_data = [
            row for row in self.data
            if from_date_str <= row['trans_date'] <= to_date_str
        ]

        self.populateTable(filtered_data)

        end_time = time.time()  # End timing
        logging.info(f"showFilteredData took {end_time - start_time:.4f} seconds")

    def populateTable(self, data):
        start_time = time.time()  # Start timing

        self.employeeListTable.setRowCount(len(data))
        self.employeeListTable.clearContents()

        for row_position, row in enumerate(data):
            items = [
                QTableWidgetItem(row['bio_no']),
                QTableWidgetItem(row['trans_date']),
                QTableWidgetItem(row['time']),
                QTableWidgetItem(row['mach_code']),
                QTableWidgetItem(row['sched'])
            ]
            for item in items:
                item.setTextAlignment(Qt.AlignCenter)

            for column, item in enumerate(items):
                self.employeeListTable.setItem(row_position, column, item)

        end_time = time.time()  # End timing
        logging.info(f"populateTable took {end_time - start_time:.4f} seconds")