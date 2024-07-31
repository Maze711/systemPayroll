from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QLineEdit
from PyQt5.uic import loadUi

from MainFrame.systemFunctions import globalFunction, timekeepingFunction
import logging


class TimeSheet(QDialog):
    def __init__(self, data):
        super(TimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = (globalFunction.resource_path("TimeKeeping\\timeSheet\\TimeSheet.ui"))
        loadUi(ui_file, self)

        self.data = data
        self.filtered_data = data
        self.setupTable()
        self.populateTimeSheet()

        self.searchBioNum = self.findChild(QLineEdit, 'txtSearch_4')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

    def setupTable(self):
        self.TimeSheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.horizontalHeader().setStretchLastSection(True)

    def populateTimeSheet(self, data=None):
        if data is None:
            data = self.data

        self.TimeSheetTable.setRowCount(len(data))

        for i, row in enumerate(data):
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            emp_name_item.setToolTip(row['EmpName'])
            check_in_item = QTableWidgetItem(row['Check_In'])
            check_out_item = QTableWidgetItem(row['Check_Out'])
            hours_worked_item = QTableWidgetItem(row['Hours_Worked'])
            difference_item = QTableWidgetItem(str(row.get('Difference', '')))
            regular_holiday_overtime = QTableWidgetItem(str(row.get('Regular Holiday Overtime', '')))
            special_holiday_overtime = QTableWidgetItem(str(row.get('Special Holiday Overtime', '')))

            for item in [bio_num_item, emp_name_item, check_in_item, check_out_item, hours_worked_item, difference_item,
                         regular_holiday_overtime, special_holiday_overtime]:
                item.setTextAlignment(Qt.AlignCenter)

            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 2, emp_name_item)  # Employee
            self.TimeSheetTable.setItem(i, 3, check_in_item)  # Check In
            self.TimeSheetTable.setItem(i, 4, check_out_item)  # Check Out
            self.TimeSheetTable.setItem(i, 5, hours_worked_item)  # Hours Worked
            self.TimeSheetTable.setItem(i, 6, difference_item)  # Ordinary Day (Difference)
            self.TimeSheetTable.setItem(i, 7, regular_holiday_overtime)  # Regular Holiday Overtime
            self.TimeSheetTable.setItem(i, 8, special_holiday_overtime)  # Special Holiday Overtime

            if i == 0:
                self.lblMach.setText(row['MachCode'])
