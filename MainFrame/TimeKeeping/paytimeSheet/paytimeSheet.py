import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.payTrans.payTransLoader import PayTrans
from MainFrame.systemFunctions import globalFunction, single_function_logger, timekeepingFunction


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

            # Round the overtime value to the nearest two decimal places
            overtime_value_rounded = round(overtime_value, 2)

            item['OT_Earn'] = overtime_value_rounded
            logging.info(f"Calculated overtime for EmpNo {item['EmpNo']}: {overtime_value_rounded}")


class PaytimeSheet(QMainWindow):
    def __init__(self, main_window, content):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytimesheet.ui")
        loadUi(ui_file, self)

        self.main_window = main_window

        self.data = content
        self.original_data = content  # Store original data

        self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.payTransBtn = self.findChild(QPushButton, 'btnPayTrans')
        self.payTransBtn.clicked.connect(self.createPayTrans)

        self.searchBioNum = self.findChild(QLineEdit, 'txtSearch')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.populatePaytimeSheetTable(self.data)

    @single_function_logger.log_function
    def populatePaytimeSheetTable(self, data):
        for row in range(self.paytimesheetTable.rowCount()):
            self.paytimesheetTable.setRowHidden(row, False)

        # Define column names in the Excel file
        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'CostCenter': 'costcenter',
            'DaysWork': 'dayswork',
            'DaysPresent': 'daypresent',
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
        headers = [col.lower() for col in data[0]]  # Convert headers to lowercase
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        self.paytimesheetTable.setRowCount(len(data) - 1)  # Exclude header row

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

            # Logging the row data being added
            logging.info(f"Adding row {i}: {row}")

    @single_function_logger.log_function
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
                bio_num = bio_num_item.text()[3:]
            else:
                bio_num = ""

            selected_data.append({
                'EmpNo': emp_no_item.text(),
                'BioNum': bio_num,
                'EmpName': emp_name_item.text(),
                'Present Days': present_days_item.text(),
                'OrdinaryDayOT': ordinary_day_ot_item.text()
            })

        bio_num_to_rate = self.readRatesFromExcel('Files Testers\\file201.xls')

        # Update selected_data with rate
        for item in selected_data:
            item['Rate'] = bio_num_to_rate.get(item['BioNum'], "Missing")

        # Perform automated calculations
        pay_computation = PayComputation(selected_data)
        pay_computation.basicComputation()
        pay_computation.overtimeComputation()  # Call the new method for overtime computation

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

            # Find indices for 'empl_id' and 'rate' columns
            headers = [sheet.cell_value(0, col_idx).strip().lower() for col_idx in range(sheet.ncols)]
            empl_id_index = headers.index('empl_id') if 'empl_id' in headers else None
            rate_index = headers.index('rate') if 'rate' in headers else None

            if empl_id_index is None or rate_index is None:
                logging.error("Required columns 'empl_id' or 'rate' not found in the Excel file.")
                return bio_num_to_rate

            for row_idx in range(1, sheet.nrows):  # Skip header row
                empl_id = sheet.cell_value(row_idx, empl_id_index)
                rate = sheet.cell_value(row_idx, rate_index)

                # Update bio_num_to_rate
                bio_num_to_rate[empl_id] = str(int(float(rate)))  # Convert rate to integer

            logging.info(f"Processed Employee IDs and Rates from Excel file: {bio_num_to_rate}")

        except Exception as e:
            logging.error(f"Error reading or processing Excel file: {e}")

        return bio_num_to_rate
