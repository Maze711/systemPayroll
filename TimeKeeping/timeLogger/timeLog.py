import sys
import os
import mysql.connector
from mysql.connector import Error

import logging

import time
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow
from PyQt5.uic import loadUi

from TimeKeeping.timeCardMaker.timeCard import timecard

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


class timelogger(QMainWindow):
    def __init__(self, content):
        super().__init__()
        self.setFixedSize(1180, 665)
        #loadUi(os.path.join(os.path.dirname(__file__), 'timeLog.ui'), self)
        ui_file = (resource_path("TimeKeeping\\timeLogger\\timeLog.ui"))
        loadUi(ui_file, self)

        self.content = content

        self.fromCalendar = self.findChild(QDateEdit, 'dateStart')
        self.toCalendar = self.findChild(QDateEdit, 'dateEnd')
        self.filterButton = self.findChild(QPushButton, 'btnFilter')
        self.createCard = self.findChild(QPushButton, 'btnCard')
        self.employeeListTable = self.findChild(QTableWidget, 'employeeListTable')

        self.fromCalendar.setDate(QDate.currentDate())
        self.toCalendar.setDate(QDate.currentDate())

        self.filterButton.clicked.connect(self.showFilteredData)
        self.createCard.clicked.connect(self.openTimeCard)
        self.createCard.setEnabled(False)

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
        self.createCard.setEnabled(bool(filtered_data))

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

    def openTimeCard(self):
        from_date = self.fromCalendar.date()
        to_date = self.toCalendar.date()
        from_date_str = from_date.toString("yyyy-MM-dd")
        to_date_str = to_date.toString("yyyy-MM-dd")

        filtered_data = [
            row for row in self.data
            if from_date_str <= row['trans_date'] <= to_date_str
        ]

        combined_data = {}
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                for row in filtered_data:
                    bio_no = row['bio_no']
                    query = f"SELECT pi.surname, pi.firstname, pi.mi, ep.sche_name " \
                            f"FROM personal_information pi " \
                            f"JOIN emp_posnsched ep ON pi.emp_id = ep.emp_id " \
                            f"WHERE pi.emp_id = '{bio_no}'"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result:
                        surname, firstname, mi, sche_name = result
                        emp_name = f"{surname}, {firstname} {mi}"
                    else:
                        emp_name = "Unknown"

                    if bio_no not in combined_data:
                        combined_data[bio_no] = {
                            'EmpNumber': '',  # Replace with actual EmpNumber if available
                            'BioNum': bio_no,
                            'EmpName': emp_name,
                            'Trans_Date': row['trans_date'],
                            'MachCode': row['mach_code'],
                            'Check_In': 'Missing',
                            'Check_Out': 'Missing',
                            'Schedule': sche_name  # Assign sche_name to the Schedule key
                        }

                    if row['sched'] == 'Time IN':
                        combined_data[bio_no]['Check_In'] = row['time']
                    elif row['sched'] == 'Time OUT':
                        combined_data[bio_no]['Check_Out'] = row['time']

                final_data = list(combined_data.values())

                self.timecard_window = timecard(final_data, from_date_str, to_date_str)
                self.timecard_window.show()
                self.close()

            except Error as e:
                logging.error(f"Error fetching employee data: {e}")

            finally:
                cursor.close()
                connection.close()
        else:
            logging.error("Failed to establish database connection")