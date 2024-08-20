import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.payTrans.payTransLoader import PayTrans
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
from MainFrame.TimeKeeping.paytimeSheet.storeDeductionLoader import StoreDeductionLoader
from MainFrame.Database_Connection.user_session import UserSession

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PayComputation:
    def __init__(self, data):
        self.data = data

    def basicComputation(self):
        for item in self.data:
            days_work = item.get('Present Days')
            rate = item.get('Rate')

            try:
                days_work_int = int(float(days_work))
                rate_int = int(float(rate))
            except ValueError:
                days_work_int = 0
                rate_int = 0

            basic = days_work_int * rate_int
            item['Basic'] = basic
            logging.info(f"Calculated basic for EmpNo {item['EmpNo']}: {basic}")

    def overtimeComputation(self):
        overtime_rate = 74.844  # Define the overtime rate
        for item in self.data:
            ordinary_day_ot = item.get('OrdinaryDayOT')

            try:
                ordinary_day_ot_float = float(ordinary_day_ot)
            except ValueError:
                ordinary_day_ot_float = 0

            overtime_value = ordinary_day_ot_float * overtime_rate
            item['OT_Earn'] = round(overtime_value, 2)
            logging.info(f"Calculated overtime for EmpNo {item['EmpNo']}: {item['OT_Earn']}")


class PaytimeSheetUI:
    def __init__(self, parent):
        self.parent = parent

    def setupUI(self):
        self.parent.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.parent.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.parent.payTransBtn = self.parent.findChild(QPushButton, 'btnPayTrans')
        self.parent.payTransBtn.clicked.connect(self.parent.createPayTrans)

        self.parent.searchBioNum = self.parent.findChild(QLineEdit, 'txtSearch')
        if self.parent.searchBioNum is not None:
            self.parent.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self.parent))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.parent.populatePaytimeSheetTable(self.parent.data)


class DeductionUI:
    def __init__(self, parent):
        self.parent = parent
        self.user_session = UserSession().getALLSessionData()

    def setupUI(self):
        self.parent.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.parent.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.parent.btnEdit = self.parent.findChild(QPushButton, 'btnEdit')
        self.parent.placeBTN = self.parent.findChild(QPushButton, 'placeBTN')
        self.parent.btnStore = self.parent.findChild(QPushButton, 'btnStore')

        if self.parent.btnEdit:
            self.parent.btnEdit.clicked.connect(self.showDeductionUI)
        else:
            logging.error("Error: btnEdit QPushButton not found in the UI.")

        if self.parent.placeBTN:
            self.parent.placeBTN.clicked.connect(self.placeDeductions)
        else:
            logging.error("Error: placeBTN QPushButton not found in the UI.")

        if self.parent.btnStore:
            self.parent.btnStore.clicked.connect(self.showStoreDeductionLoader)
        else:
            logging.error("Error: placeBTN QPushButton not found in the UI.")

        self.populatePaytimeSheetTable(self.parent.data)

    def populatePaytimeSheetTable(self, data):
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)
        for row in range(self.parent.paytimesheetTable.rowCount()):
            self.parent.paytimesheetTable.setRowHidden(row, False)

        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'Pay Ded 1': 'payded1',
            'Pay Ded 2': 'payded2',
            'Pay Ded 3': 'payded3',
            'Pay Ded 4': 'payded4',
            'Pay Ded 5': 'payded5',
            'Pay Ded 6': 'payded6',
            'Pay Ded 7': 'payded7',
            'Pay Ded 8': 'payded8',
            'Pay Ded 9': 'payded9',
            'Pay Ded 10': 'payded10',
            'Pay Ded 11': 'payded11',
            'Pay Ded 12': 'payded12',
            'Pay Ded 13': 'payded13',
            'Pay Ded 14': 'payded14',
        }

        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        for i, row in enumerate(data[1:]):
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

    def showDeductionUI(self):
        selected_row = self.parent.paytimesheetTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
            return

        try:
            emp_name_item = self.parent.paytimesheetTable.item(selected_row, 2)
            bio_num_item = self.parent.paytimesheetTable.item(selected_row, 1)

            emp_name = emp_name_item.text() if emp_name_item else ""
            bio_num = bio_num_item.text() if bio_num_item else ""

            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\deduction.ui")
            self.deductionQDialog = QDialog()
            loadUi(ui_file, self.deductionQDialog)

            empNameTxt = self.deductionQDialog.findChild(QLabel, 'empNameTxt')
            bioNumTxt = self.deductionQDialog.findChild(QLabel, 'bioNumTxt')

            if empNameTxt:
                empNameTxt.setText(emp_name)
            if bioNumTxt:
                bioNumTxt.setText(bio_num)

            self.placeBTN = self.deductionQDialog.findChild(QPushButton, 'placeBTN')
            if self.placeBTN:
                self.placeBTN.clicked.connect(self.placeDeductions)
            else:
                logging.error("Error: placeBTN QPushButton not found in the deduction UI.")

            self.deductionQDialog.show()
            logging.info("Deduction UI loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load deduction UI: {e}")
            print(f"Failed to load deduction UI: {e}")

    def placeDeductions(self):
        try:
            selected_row = self.parent.paytimesheetTable.currentRow()
            if selected_row == -1:
                logging.warning("No row selected.")
                QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
                return

            for i in range(1, 15):
                deduction_field = self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}')
                if deduction_field and deduction_field.text().isdigit():
                    deduction_value = deduction_field.text()
                    deduction_col = self.getColumnIndex(f'Pay Ded {i}')
                    if deduction_col != -1:
                        item = QTableWidgetItem(deduction_value)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.parent.paytimesheetTable.setItem(selected_row, deduction_col, item)
                        logging.info(f"Updated Pay Ded {i} for row {selected_row} with value {deduction_value}")
                    else:
                        logging.warning(f"Pay Ded {i} column not found in the table.")
        except Exception as e:
            logging.error(f"Failed to place deductions: {e}")
            print(f"Failed to place deductions: {e}")

    def get_deduction_table_data(self):
        deduction_data = []

        # Get the number of rows and columns
        row_count = self.parent.paytimesheetTable.rowCount()
        column_count = self.parent.paytimesheetTable.columnCount()

        pay_deduction_columns = [f'Pay Ded {i}' for i in range(1, 15)]

        for row_index in range(row_count):
            row_data = {}

            for column_index in range(column_count):
                # Get the header/column name
                column_name = self.parent.paytimesheetTable.horizontalHeaderItem(column_index).text()

                # Get each cell data
                cell_item = self.parent.paytimesheetTable.item(row_index, column_index)
                cell_data = cell_item.text() if cell_item else None

                if column_name in pay_deduction_columns:
                    row_data[column_name] = int(cell_data) if cell_data else 0
                else:
                    row_data[column_name] = cell_data

            deduction_data.append(row_data)

        return deduction_data

    def showStoreDeductionLoader(self):
        message = QMessageBox.question(self.parent, "Storing Deduction into Database",
                                       "Are you sure you want to store all the data into database "
                                       "even though not all data has deductions?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.deduction_data = self.get_deduction_table_data()
            self.storeDeductionLoader = StoreDeductionLoader(self.deduction_data, self.parent)
            self.storeDeductionLoader.show()

    def getColumnIndex(self, column_name):
        header_items = [self.parent.paytimesheetTable.horizontalHeaderItem(i).text()
                        for i in range(self.parent.paytimesheetTable.columnCount())]
        if column_name in header_items:
            return header_items.index(column_name)
        return -1

    def getBioNum(self, row):
        bio_num_item = self.parent.paytimesheetTable.item(row, 1)
        return bio_num_item.text() if bio_num_item else "Unknown"

class PaytimeSheet(QMainWindow):
    def __init__(self, main_window, content, user_role):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)

        # Load different UI based on user_role
        if user_role == "Pay Master 2":
            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\payDeduction.ui")
        else:
            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytimesheet.ui")

        loadUi(ui_file, self)

        self.main_window = main_window
        self.data = content
        self.user_role = user_role
        self.original_data = content  # Store original data

        # Print the user_role
        print(f"User Role: {self.user_role}")

        if user_role == "Pay Master 1":
            self.uiHandler = PaytimeSheetUI(self)
            self.uiHandler.setupUI()
        elif user_role == "Pay Master 2":
            self.uiHandler = DeductionUI(self)
            self.uiHandler.setupUI()

    def populatePaytimeSheetTable(self, data):
        self.paytimesheetTable.setRowCount(len(data) - 1)  # Exclude header row
        for row in range(self.paytimesheetTable.rowCount()):
            self.paytimesheetTable.setRowHidden(row, False)

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
                    self.paytimesheetTable.setItem(i, list(column_names.keys()).index(field_name), item)
                else:
                    logging.warning(f"Column '{field_name}' not found in data.")
            logging.info(f"Adding row {i}: {row}")

    def createPayTrans(self, checked=False):
        from_date = self.lblFrom.text()
        to_date = self.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.paytimesheetTable.rowCount()):
            emp_no_item = self.paytimesheetTable.item(row, 0)
            bio_num_item = self.paytimesheetTable.item(row, 1)
            emp_name_item = self.paytimesheetTable.item(row, 2)
            present_days_item = self.paytimesheetTable.item(row, 5)
            ordinary_day_ot_item = self.paytimesheetTable.item(row, 13)

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
            self.window = PayTrans(from_date, to_date, selected_data)
            self.main_window.open_dialogs.append(self.window)
            self.window.show()
            self.close()
        except Exception as e:
            logging.error(f"Failed to create PayTrans window: {e}")
            print(f"Failed to create PayTrans window: {e}")

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
