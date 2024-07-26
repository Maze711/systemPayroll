from mysql.connector import Error
from PyQt5.QtWidgets import QDialog,  QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

from MainFrame.Database_Connection.DBConnection import create_connection
from TimeKeeping.timekeeping_Function.timekeepingFunction import resource_path
from Logger_config import get_logger

logging = get_logger()


class DateChange(QDialog):
    def __init__(self):
        super(DateChange, self).__init__()
        self.setFixedSize(400, 300)
        ui_file = resource_path("TimeKeeping\\dateChange\\datechange.ui")
        loadUi(ui_file, self)

        self.connection = create_connection('TIMEKEEPING')
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
