import sys
import os
import logging
import mysql.connector

from mysql.connector import Error
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_connection():
    try:
        connection = mysql.connector.connect(
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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DateChange(QDialog):
    def __init__(self):
        super(DateChange, self).__init__()
        self.setFixedSize(400, 300)
        ui_file = resource_path("TimeKeeping\\dateChange\\datechange.ui")
        loadUi(ui_file, self)

        self.connection = create_connection()
        self.cmbHoliday.currentIndexChanged.connect(self.fetch_holiday_data)
        self.btnUpdate.clicked.connect(self.update_holiday_date)

        self.fetch_holiday_data()

    def fetch_holiday_data(self):
        holiday_name = self.cmbHoliday.currentText()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT date, dateType, holidayIsMovable FROM type_of_dates WHERE holidayName = %s", (holiday_name,))
            result = cursor.fetchone()
            if result:
                date, date_type, holiday_is_movable = result
                date_str = date.strftime("%Y-%m-%d")
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                self.dateEdit.setDate(qdate)
                self.dateType.setText(date_type)

            if holiday_is_movable == 1:
                self.dateEdit.setEnabled(True)
                self.btnUpdate.setEnabled(True)
            else:
                self.dateEdit.setEnabled(False)
                self.btnUpdate.setEnabled(False)

        except Error as e:
            logging.exception("Error while fetching data from MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to load data")

    def update_holiday_date(self):
        holiday_name = self.cmbHoliday.currentText()
        new_date = self.dateEdit.date().toString("yyyy-MM-dd")

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE type_of_dates SET date = %s WHERE holidayName = %s", (new_date, holiday_name))
            self.connection.commit()
            QMessageBox.information(self, "Success", "Date updated successfully")
        except Error as e:
            logging.exception("Error while updating data in MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to update data")
