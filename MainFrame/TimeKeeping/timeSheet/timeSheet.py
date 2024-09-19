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
            # Create QTableWidgetItems for each column
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_num_item = QTableWidgetItem(row['EmpNumber'])
            emp_name_item = QTableWidgetItem(row['Employee'])
            days_work_item = QTableWidgetItem(str(row['Days_Work']))
            days_present_item = QTableWidgetItem(str(row['Days_Present']))
            total_hours_work_item = QTableWidgetItem(str(row['Total_Hours_Worked']))
            ordday_nd_item = QTableWidgetItem(str(row['Night_Differential']))
            ordday_nd_ot_item = QTableWidgetItem(str(row['Night_Differential_OT']))

            # Additional fields as per your request
            ordday_item = QTableWidgetItem(str(row.get('OrdDay', 0)))
            ordday_ot_item = QTableWidgetItem(str(row.get('OrdDayOT', 0)))
            rd_item = QTableWidgetItem(str(row.get('RD', 0)))
            rd_ot_item = QTableWidgetItem(str(row.get('RDOT', 0)))
            rd_nd_item = QTableWidgetItem(str(row.get('RDND', 0)))
            rd_nd_ot_item = QTableWidgetItem(str(row.get('RDNDOT', 0)))
            shldy_item = QTableWidgetItem(str(row.get('SHLDy', 0)))
            shldy_ot_item = QTableWidgetItem(str(row.get('SHLDyOT', 0)))
            shldy_nd_item = QTableWidgetItem(str(row.get('SHLDyND', 0)))
            shldy_nd_ot_item = QTableWidgetItem(str(row.get('SHLDyNDOT', 0)))
            reghldy_item = QTableWidgetItem(str(row.get('RegHldy', 0)))
            reghldy_ot_item = QTableWidgetItem(str(row.get('RegHldyOT', 0)))
            shldy_rd_item = QTableWidgetItem(str(row.get('SHLDyRD', 0)))
            shldy_rd_ot_item = QTableWidgetItem(str(row.get('SHLDyRDOT', 0)))
            reghldy_rd_item = QTableWidgetItem(str(row.get('RegHldyRD', 0)))
            reghldy_rd_ot_item = QTableWidgetItem(str(row.get('RegHldyRDOT', 0)))

            # Align items to the center
            items = [
                bio_num_item, emp_num_item, emp_name_item, days_work_item, days_present_item, total_hours_work_item,
                ordday_nd_item, ordday_nd_ot_item, ordday_item, ordday_ot_item, rd_item, rd_ot_item, rd_nd_item,
                rd_nd_ot_item, shldy_item, shldy_ot_item, shldy_nd_item, shldy_nd_ot_item, reghldy_item,
                reghldy_ot_item,
                shldy_rd_item, shldy_rd_ot_item, reghldy_rd_item, reghldy_rd_ot_item
            ]
            for item in items:
                item.setTextAlignment(Qt.AlignCenter)

            # Set table items for each row
            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 1, emp_num_item)  # Employee No.
            self.TimeSheetTable.setItem(i, 2, emp_name_item)  # Employee Name
            self.TimeSheetTable.setItem(i, 4, days_work_item)  # Days Worked
            self.TimeSheetTable.setItem(i, 5, days_present_item)  # Days Present
            self.TimeSheetTable.setItem(i, 6, total_hours_work_item)  # Total Hours Worked
            self.TimeSheetTable.setItem(i, 9, ordday_nd_item)  # Ord Day ND
            self.TimeSheetTable.setItem(i, 10, ordday_nd_ot_item)  # Ord Day ND OT
            self.TimeSheetTable.setItem(i, 7, ordday_item)  # Ord Day
            self.TimeSheetTable.setItem(i, 8, ordday_ot_item)  # Ord Day OT
            self.TimeSheetTable.setItem(i, 11, rd_item)  # RD
            self.TimeSheetTable.setItem(i, 12, rd_ot_item)  # RD OT
            self.TimeSheetTable.setItem(i, 13, rd_nd_item)  # RD ND
            self.TimeSheetTable.setItem(i, 14, rd_nd_ot_item)  # RD ND OT
            self.TimeSheetTable.setItem(i, 15, shldy_item)  # SHLDy
            self.TimeSheetTable.setItem(i, 16, shldy_ot_item)  # SHLDy OT
            self.TimeSheetTable.setItem(i, 17, shldy_nd_item)  # SHLDy ND
            self.TimeSheetTable.setItem(i, 18, shldy_nd_ot_item)  # SHLDy ND OT
            self.TimeSheetTable.setItem(i, 19, reghldy_item)  # RegHldy
            self.TimeSheetTable.setItem(i, 20, reghldy_ot_item)  # RegHldy OT
            self.TimeSheetTable.setItem(i, 21, shldy_rd_item)  # SHLDyRD
            self.TimeSheetTable.setItem(i, 22, shldy_rd_ot_item)  # SHLDyRD OT
            self.TimeSheetTable.setItem(i, 23, reghldy_rd_item)  # RegHldyRD
            self.TimeSheetTable.setItem(i, 24, reghldy_rd_ot_item)  # RegHldyRD OT

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
