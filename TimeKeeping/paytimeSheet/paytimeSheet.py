import sys
import os
import logging
import xlrd

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.uic import loadUi

from TimeKeeping.payTrans.payTransLoader import PayTrans

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PaytimeSheet(QMainWindow):
    def __init__(self, data, fromDate, toDate):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = resource_path("TimeKeeping\\paytimeSheet\\paytimesheet.ui")
        loadUi(ui_file, self)

        self.data = data

        self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

        self.lblFrom.setText(fromDate)
        self.lblTo.setText(toDate)

        self.payTransBtn = self.findChild(QPushButton, 'btnPayTrans')
        self.payTransBtn.clicked.connect(self.createPayTrans)

        self.populatePaytimeSheetTable(self.data)

    def populatePaytimeSheetTable(self, data):
        self.paytimesheetTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(str(row['EmpNo']))
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            emp_name_item.setToolTip(row['EmpName'])
            present_days_item = QTableWidgetItem(str(row['Present Days']))
            present_holidays_item = QTableWidgetItem(str(row['Present Holidays']))

            # Centers all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, present_days_item, present_holidays_item]:
                item.setTextAlignment(Qt.AlignCenter)

            # Logging the row data being added
            #logging.info(f"Adding row {i}: {row}")

            self.paytimesheetTable.setItem(i, 0, emp_no_item)
            self.paytimesheetTable.setItem(i, 1, bio_num_item)
            self.paytimesheetTable.setItem(i, 2, emp_name_item)
            self.paytimesheetTable.setItem(i, 4, present_days_item)
            self.paytimesheetTable.setItem(i, 7, present_holidays_item)

    def createPayTrans(self):
        from_date = self.lblFrom.text()
        to_date = self.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.paytimesheetTable.rowCount()):
            emp_no_item = self.paytimesheetTable.item(row, 0)
            bio_num_item = self.paytimesheetTable.item(row, 1)
            emp_name_item = self.paytimesheetTable.item(row, 2)
            present_days_item = self.paytimesheetTable.item(row, 4)
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