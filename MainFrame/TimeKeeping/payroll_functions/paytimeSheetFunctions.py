import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.payTrans.payTransLoader import PayTrans
from MainFrame.TimeKeeping.payroll_functions.payComputations import PayComputation
from MainFrame.systemFunctions import timekeepingFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PaytimeSheetUI:
    def __init__(self, parent):
        self.parent = parent

    def setupUI(self):
        self.parent.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.parent.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.parent.payTransBtn = self.parent.findChild(QPushButton, 'btnPayTrans')
        self.parent.payTransBtn.clicked.connect(self.createPayTrans)

        self.parent.searchBioNum = self.parent.findChild(QLineEdit, 'txtSearch')
        if self.parent.searchBioNum is not None:
            self.parent.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self.parent))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.populatePaytimeSheetTable(self.parent.data)

    def populatePaytimeSheetTable(self, data):
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)  # Exclude header row
        for row in range(self.parent.paytimesheetTable.rowCount()):
            self.parent.paytimesheetTable.setRowHidden(row, False)

        # Define column names in the Excel file
        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'CostCenter': 'costcenter',
            'DaysWork': 'actual days',
            'DaysPresent': 'dayspresent',
            'RestDay': 'restday',
            'Holiday': 'holiday',
            'RestHoliday': 'rsthlyday',
            'OrdinaryDayNight': 'orddaynite',
            'RestDayNight': 'rstdaynite',
            'HolidayNight': 'hlydaynite',
            'RestHolidayNight': 'rsthlydayn',
            'OrdinaryDayOT': 'orddayot',
            'RestDayOT': 'rstdayot',
            'HolidayOT': 'hlydayot',
            'RestHolidayOT': 'rsthlydayo',
            'Late': 'late',
            'Undertime': 'undertime',
            'Absent': 'absent',
            'DatePosted': 'dateposted',
            'Remarks': 'remarks',
            'EmpCompany': 'empcompany',
            'LegalHoliday': 'legalholid'
        }

        # Extract column indices from the header row
        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]  # Handle None values
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        for i, row in enumerate(data[1:]):  # Skip header row
            for field_name, col_name in column_names.items():
                col_idx = col_indices.get(field_name)
                if col_idx is not None:
                    item = QTableWidgetItem(str(row[col_idx]))
                    if field_name in column_names:
                        item.setTextAlignment(Qt.AlignCenter)
                    if field_name == 'Employee Name':
                        item.setToolTip(row[col_idx])
                    self.parent.paytimesheetTable.setItem(i, list(column_names.keys()).index(field_name), item)
                else:
                    logging.warning(f"Column '{field_name}' not found in data.")
            logging.info(f"Adding row {i}: {row}")

    def readRatesFromExcel(self, file_path):
        bio_num_to_rate = {}

        try:
            workbook = xlrd.open_workbook(file_path, encoding_override='latin-1')
            sheet = workbook.sheet_by_index(0)  # Use the first sheet

            headers = [sheet.cell_value(0, col_idx).strip().lower() for col_idx in range(sheet.ncols)]
            empl_id_index = headers.index('empl_id') if 'empl_id' in headers else None
            rate_index = headers.index('rate') if 'rate' in headers else None

            if empl_id_index is None or rate_index is None:
                logging.error("Required columns 'empl_id' or 'rate' not found in the Excel file.")
                return bio_num_to_rate

            for row_idx in range(1, sheet.nrows):  # Skip the header row
                empl_id_value = str(sheet.cell_value(row_idx, empl_id_index))
                rate_value = str(sheet.cell_value(row_idx, rate_index))

                # Remove trailing '.0' from empl_id_value, if present
                if empl_id_value.endswith('.0'):
                    empl_id_value = empl_id_value[:-2]

                bio_num_to_rate[empl_id_value] = rate_value

            logging.info(f"Processed {sheet.nrows - 1} rows from Excel file.")

        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            print(f"Error reading Excel file: {e}")

        return bio_num_to_rate

    def createPayTrans(self, checked=False):
        from_date = self.parent.lblFrom.text()
        to_date = self.parent.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.parent.paytimesheetTable.rowCount()):
            emp_no_item = self.parent.paytimesheetTable.item(row, 0)
            bio_num_item = self.parent.paytimesheetTable.item(row, 1)
            emp_name_item = self.parent.paytimesheetTable.item(row, 2)
            present_days_item = self.parent.paytimesheetTable.item(row, 5)
            ordinary_day_ot_item = self.parent.paytimesheetTable.item(row, 13)

            if bio_num_item and bio_num_item.text():
                bio_num = bio_num_item.text()[2:]
            else:
                bio_num = ""

            selected_data.append({
                'EmpNo': emp_no_item.text(),
                'BioNum': bio_num,
                'EmpName': emp_name_item.text(),
                'Present Days': present_days_item.text(),
                'OrdinaryDayOT': ordinary_day_ot_item.text()
            })

        bio_num_to_rate = self.readRatesFromExcel('MainFrame\\Files Testers\\file201.xls')

        # Update selected_data with rate
        for item in selected_data:
            item['Rate'] = bio_num_to_rate.get(item['BioNum'], "Missing")

        # Perform automated calculations
        pay_computation = PayComputation(selected_data)
        pay_computation.basicComputation()
        pay_computation.overtimeComputation()

        match_count = sum(1 for item in selected_data if item['BioNum'] in bio_num_to_rate)
        logging.info(f"Total matches of bio_num with processed empl_id: {match_count}")
        print(f"Total matches of bio_num with processed empl_id: {match_count}")

        try:
            self.parent.window = PayTrans(from_date, to_date, selected_data)
            self.parent.main_window.open_dialogs.append(self.parent.window)
            self.parent.window.show()
            self.parent.close()
        except Exception as e:
            logging.error(f"Failed to create PayTrans window: {e}")
            print(f"Failed to create PayTrans window: {e}")