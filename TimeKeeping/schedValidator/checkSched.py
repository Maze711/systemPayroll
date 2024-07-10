import sys
import os
import mysql.connector
from mysql.connector import Error

import logging

from PyQt5.QtCore import QDate, Qt, QTime
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QDateEdit, QLabel, QPushButton, QTableWidget, QMainWindow, QLineEdit, QMessageBox, QHeaderView
from PyQt5.uic import loadUi

from MainFrame.Database_Connection.DBConnection import create_connection

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class chkSched(QDialog):
    def __init__(self, data):
        super(chkSched, self).__init__()
        self.setFixedSize(780, 413)
        ui_file = resource_path("TimeKeeping\\schedValidator\\Schedule.ui")
        loadUi(ui_file, self)

        self.data = data

        self.populate_schedule_with_data(data)

    def populate_schedule_with_data(self, data):
        (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours) = data

        self.empNameTxt.setText(empName)
        self.bioNumTxt.setText(bioNum)
        self.dateOfWork.setDate(QDate.fromString(trans_date, "yyyy-MM-dd"))
        self.timeInTxt.setText(checkIn)
        self.timeOutTxt.setText(checkOut)
        self.hoursWorkedTxt.setText(str(total_hours))
        self.holidayNameTxt.setText(self.getHolidayName(trans_date))
        self.typeOfDayCb.setCurrentText(self.getTypeOfDate(trans_date))

    def getHolidayName(self, trans_date):
        try:
            connection = create_connection('TIMEKEEPING')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return None
            cursor = connection.cursor()

            # Fetches the holiday name in type_of_dates database
            fetch_holiday_name = "SELECT holidayName FROM type_of_dates WHERE date = %s"
            cursor.execute(fetch_holiday_name, (trans_date, ))

            result = cursor.fetchone()
            if result:
                return result[0]

            return "Normal Day"

        except Error as e:
            logging.error(f"Error fetching holiday name: {e}")
            return
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def getTypeOfDate(self, trans_date):
        try:
            connection = create_connection('TIMEKEEPING')
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