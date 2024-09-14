import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import globalFunction, timekeepingFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class TimeSheet(QDialog):
    def __init__(self, data, lblFrom, lblTo, lblMach):
        super(TimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\TimeSheet.ui"))
        loadUi(ui_file, self)

        self.data = data
        self.lblFrom = lblFrom
        self.lblTo = lblTo
        self.lblMach = lblMach
        self.setupTable()
        self.populateTimeSheet()
        self.setupLabels()

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
            emp_num_item = QTableWidgetItem(row['EmpNumber'])
            emp_name_item = QTableWidgetItem(row['Employee'])
            days_work_item = QTableWidgetItem(str(row['Days_Work']))
            days_present_item = QTableWidgetItem(str(row['Days_Present']))
            total_hours_work = QTableWidgetItem(str(row['Total_Hours_Worked']))
            ordday_nd = QTableWidgetItem(str(row['Night_Differential']))
            ordday_nd_ot = QTableWidgetItem(str(row['Night_Differential_OT']))

            for item in [bio_num_item, emp_num_item, emp_name_item, days_work_item, days_present_item, total_hours_work,
                         ordday_nd, ordday_nd_ot]:
                item.setTextAlignment(Qt.AlignCenter)

            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 1, emp_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 2, emp_name_item)  # Employee
            self.TimeSheetTable.setItem(i, 4, days_work_item)  # Sum of days of work
            self.TimeSheetTable.setItem(i, 5, days_present_item)  # Sum of days of work
            self.TimeSheetTable.setItem(i, 6, total_hours_work)  # Sum of days of work
            self.TimeSheetTable.setItem(i, 9, ordday_nd)  # Sum of days of work
            self.TimeSheetTable.setItem(i, 10, ordday_nd_ot)  # Sum of days of work

    def setupLabels(self):
        lblFrom_widget = self.findChild(QLabel, 'lblFrom')
        lblTo_widget = self.findChild(QLabel, 'lblTo')
        lblMach_widget = self.findChild(QLabel, 'lblMach')

        if lblFrom_widget is not None:
            lblFrom_widget.setText(self.lblFrom)
        else:
            logging.error("Error: lblFrom QLabel not found in the UI.")

        if lblTo_widget is not None:
            lblTo_widget.setText(self.lblTo)
        else:
            logging.error("Error: lblTo QLabel not found in the UI.")

        if lblMach_widget is not None:
            lblMach_widget.setText(self.lblMach)
        else:
            logging.error("Error: lblMach QLabel not found in the UI.")
