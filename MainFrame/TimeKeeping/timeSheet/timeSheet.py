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
            emp_name_item = QTableWidgetItem(row['Employee'])
            check_in_item = QTableWidgetItem(row['Check_In'])
            check_out_item = QTableWidgetItem(row['Check_Out'])
            hours_worked_item = QTableWidgetItem(row['Hours_Worked'])
            difference_item = QTableWidgetItem(str(row.get('Difference', '')))
            regular_holiday_overtime = QTableWidgetItem(str(row.get('Regular Holiday Overtime', '')))
            special_holiday_overtime = QTableWidgetItem(str(row.get('Special Holiday Overtime', '')))

            for item in [bio_num_item, emp_name_item, check_in_item, check_out_item, hours_worked_item,
                         difference_item, regular_holiday_overtime, special_holiday_overtime]:
                item.setTextAlignment(Qt.AlignCenter)

            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 1, emp_name_item)  # Employee
            self.TimeSheetTable.setItem(i, 2, check_in_item)  # Check In
            self.TimeSheetTable.setItem(i, 3, check_out_item)  # Check Out
            self.TimeSheetTable.setItem(i, 4, hours_worked_item)  # Hours Worked
            self.TimeSheetTable.setItem(i, 5, difference_item)  # Ordinary Day (Difference)
            self.TimeSheetTable.setItem(i, 6, regular_holiday_overtime)  # Regular Holiday Overtime
            self.TimeSheetTable.setItem(i, 7, special_holiday_overtime)  # Special Holiday Overtime

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
