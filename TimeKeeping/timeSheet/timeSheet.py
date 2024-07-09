import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem, \
    QHeaderView, QDialog
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TimeSheet(QDialog):
    def __init__(self, data):
        super(TimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = resource_path("TimeKeeping\\timeSheet\\TimeSheet.ui")
        loadUi(ui_file, self)

        self.data = data
        self.setupTable()
        self.populateTimeSheet()

    def setupTable(self):
        self.TimeSheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.horizontalHeader().setStretchLastSection(True)

    def populateTimeSheet(self):
        self.TimeSheetTable.setRowCount(len(self.data))

        for i, row in enumerate(self.data):
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            emp_name_item.setToolTip(row['EmpName'])  # Set tooltip to show full name on hover
            check_in_item = QTableWidgetItem(row['Check_In'])
            check_out_item = QTableWidgetItem(row['Check_Out'])
            hours_worked_item = QTableWidgetItem(row['Hours_Worked'])

            for item in [bio_num_item, emp_name_item, check_in_item, check_out_item, hours_worked_item]:
                item.setTextAlignment(Qt.AlignCenter)

            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 2, emp_name_item)  # Employee
            self.TimeSheetTable.setItem(i, 3, check_in_item)  # Check In
            self.TimeSheetTable.setItem(i, 4, check_out_item)  # Check Out
            self.TimeSheetTable.setItem(i, 5, hours_worked_item)  # Hours Worked

            if i == 0:
                self.lblMach.setText(row['MachCode'])
