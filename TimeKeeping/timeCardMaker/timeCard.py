import sys
import os
import mysql.connector
from mysql.connector import Error

import logging

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QPushButton, QMessageBox
from PyQt5.uic import loadUi
from TimeKeeping.schedValidator.checkSched import chkSched
from TimeKeeping.timeSheet.timeSheet import TimeSheet
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

def getTypeOfDate(trans_date):
    try:
        connection = create_connection('TIMEKEEPING')
        if connection is None:
            logging.error("Error: Could not establish database connection.")
            return "Ordinary Day"  # Return default value on connection failure

        cursor = connection.cursor()

        fetch_type_of_date = "SELECT dateType FROM type_of_dates WHERE date = %s"
        cursor.execute(fetch_type_of_date, (trans_date,))

        result = cursor.fetchone()
        if result:
            return result[0]  # Return the dateType if found

        return "Ordinary Day"  # Default to Ordinary Day if no match found

    except Error as e:
        logging.error(f"Error fetching type of date: {e}")
        return "Ordinary Day"  # Return default value on error

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Database connection closed")

class timecard(QDialog):
    def __init__(self, filtered_data, from_date_str, to_date_str):
        super().__init__()
        self.setFixedSize(1345, 665)
        ui_file = resource_path("TimeKeeping\\timeCardMaker\\timecard.ui")
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

        self.btnCheckSched = self.findChild(QPushButton, 'btnCheckSched')
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

            total_hours = self.getTotalHoursWorked(checkIn, checkOut)

            data = (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours)

            dialog = chkSched(data)
            dialog.exec_()
        else:
            QMessageBox.warning(
                self,
                "No Row Selected",
                "Please select a row from the table first!"
            )

    def createTimeSheet(self):
        dataMerge = []
        for item in self.filtered_data:
            checkIn = item['Check_In']
            checkOut = item['Check_Out']
            trans_date = item['Trans_Date']
            workHours = item['workHours'] if 'workHours' in item else 'N/A'
            hoursWorked = self.getTotalHoursWorked(checkIn, checkOut)
            difference = ''  # Initialize as empty string
            regularOT = ''
            specialOT = ''

            # Check the type of the date
            dateType = getTypeOfDate(trans_date)
            if dateType == "Ordinary Day" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    difference = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Difference: {difference:.2f}")
                except ValueError:
                    logging.error(f"Error calculating difference for BioNum: {item['BioNum']}")
                    difference = 'N/A'

            if dateType == "Regular Holiday" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    regularOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Regular Holiday Overtime: {regularOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating regular holiday for BioNum: {item['BioNum']}")
                    regularOT = 'N/A'

            if dateType == "Special Holiday" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    specialOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Special Holiday Overtime: {specialOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating special holiday for BioNum: {item['BioNum']}")
                    specialOT = 'N/A'

            dataMerge.append({
                'BioNum': item['BioNum'],
                'EmpName': item['EmpName'],
                'MachCode': item['MachCode'],
                'Check_In': checkIn,
                'Check_Out': checkOut,
                'Hours_Worked': str(hoursWorked),
                'Difference': difference,
                'Regular Holiday Overtime': regularOT,
                'Special Holiday Overtime': specialOT
            })

        for data in dataMerge:
            logging.info(data)

        # Now pass the dataMerge into the TimeSheet dialog
        try:
            dialog = TimeSheet(dataMerge)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error opening TimeSheet dialog: {e}")
