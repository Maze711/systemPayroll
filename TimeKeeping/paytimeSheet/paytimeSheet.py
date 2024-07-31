from MainFrame.Resources.lib import *

from TimeKeeping.payTrans.payTransLoader import PayTrans
from MainFrame.systemFunctions import globalFunction


class PaytimeSheet(QMainWindow):
    def __init__(self, content):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytimesheet.ui")
        loadUi(ui_file, self)

        self.data = content

        self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.payTransBtn = self.findChild(QPushButton, 'btnPayTrans')
        self.payTransBtn.clicked.connect(self.createPayTrans)

        self.populatePaytimeSheetTable(self.data)

    def populatePaytimeSheetTable(self, data):
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

    def createPayTrans(self):
        from_date = self.lblFrom.text()
        to_date = self.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.paytimesheetTable.rowCount()):
            emp_no_item = self.paytimesheetTable.item(row, 0)
            bio_num_item = self.paytimesheetTable.item(row, 1)
            emp_name_item = self.paytimesheetTable.item(row, 2)
            present_days_item = self.paytimesheetTable.item(row, 5)  # DaysPresent

            selected_data.append({
                'EmpNo': emp_no_item.text(),
                'BioNum': bio_num_item.text(),
                'EmpName': emp_name_item.text(),
                'Present Days': present_days_item.text()
            })

        bio_num_to_rate = {}

        try:
            workbook = xlrd.open_workbook('Files Testers\\file201.xls', encoding_override='latin-1')
            sheet = workbook.sheet_by_index(0)  # Use the first sheet

            # Find indices for 'empl_id' and 'rate' columns
            headers = [sheet.cell_value(0, col_idx).strip().lower() for col_idx in range(sheet.ncols)]
            empl_id_index = headers.index('empl_id') if 'empl_id' in headers else None
            rate_index = headers.index('rate') if 'rate' in headers else None

            if empl_id_index is None or rate_index is None:
                logging.error("Required columns 'empl_id' or 'rate' not found in the Excel file.")
                return

            for row_idx in range(1, sheet.nrows):  # Skip header row
                empl_id = sheet.cell_value(row_idx, empl_id_index)
                rate = sheet.cell_value(row_idx, rate_index)

                # Process empl_id and update bio_num_to_rate
                processed_empl_id = empl_id[2:] if isinstance(empl_id, str) and len(empl_id) > 2 else empl_id
                bio_num_to_rate[processed_empl_id] = str(rate)

            logging.info(f"Processed Employee IDs and Rates from Excel file: {bio_num_to_rate}")

        except Exception as e:
            logging.error(f"Error reading or processing Excel file: {e}")
            return

        # Update selected_data with rate
        for item in selected_data:
            item['Rate'] = bio_num_to_rate.get(item['BioNum'], "Missing")

        match_count = sum(1 for item in selected_data if item['BioNum'] in bio_num_to_rate)
        logging.info(f"Total matches of bio_num with processed empl_id: {match_count}")
        print(f"Total matches of bio_num with processed empl_id: {match_count}")

        try:
            self.window = PayTrans(from_date, to_date, selected_data)
            self.window.show()
            self.close()
        except Exception as e:
            logging.error(f"Failed to create PayTrans window: {e}")
            print(f"Failed to create PayTrans window: {e}")