import sys
import os
import mysql.connector
from mysql.connector import Error

import logging

from PyQt5.QtCore import QDate, Qt, QTime
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow, QLineEdit
from PyQt5.uic import loadUi

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
            database='timekeeping',
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

class chkSched(QDialog):
    def __init__(self, data):
        super(chkSched, self).__init__()
        self.setFixedSize(731, 405)
        ui_file = (resource_path("TimeKeeping\\schedValidator\\Schedule.ui"))
        loadUi(ui_file, self)

        self.data = data

        self.populate_schedule_with_data(data)

    def populate_schedule_with_data(self, data):
        (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched) = data

        self.empNameTxt.setText(empName)
        self.bioNumTxt.setText(bioNum)
        self.dateOfWork.setDate(QDate.fromString(trans_date, "yyyy-MM-dd"))
        self.timeInTxt.setText(checkIn)
        self.timeOutTxt.setText(checkOut)
        self.typeDayTxt.setText(self.getTypeOfDate(trans_date))
        self.hoursWorkedTxt.setText(str(self.getTotalHoursWorked(checkIn, checkOut)))
        self.typeOfDayCb.setCurrentText(self.getTypeOfDate(trans_date))

    def getTotalHoursWorked(self, time_start, time_end):
        if time_start == 'Missing' or time_end == 'Missing':
            return "Unknown"

        timeIn = QTime.fromString(time_start, "HH:mm:ss")
        timeOut = QTime.fromString(time_end, "HH:mm:ss")

        # Converting time into seconds
        seconds_in_a_day = 24 * 60 * 60
        time_in_seconds = (timeIn.hour() * 3600) + (timeIn.minute() * 60) + timeIn.second()
        time_out_seconds = (timeOut.hour() * 3600) + (timeOut.minute() * 60) + timeOut.second()

        # Handle crossing midnight
        if time_out_seconds < time_in_seconds:
            time_out_seconds += seconds_in_a_day

        time_difference = time_out_seconds - time_in_seconds

        # Convert the difference to hours
        work_duration_in_hours = time_difference / 3600

        return round(work_duration_in_hours, 2)

    def getTypeOfDate(self, trans_date):
        try:
            connection = create_connection()
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return None
            cursor = connection.cursor()

            # Fetches the type of date in type_of_dates database
            fetch_type_of_date = "SELECT dateType FROM type_of_dates WHERE date = %s"
            cursor.execute(fetch_type_of_date, (trans_date, ))

            result = cursor.fetchone()
            if result:
                return result[0]

            return "Ordinary Day"

        except Error as e:
            logging.error(f"Error fetching type of date: {e}")
            return
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")