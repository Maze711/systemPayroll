import sys
import os
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QMainWindow
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PayTrans(QMainWindow):
    def __init__(self, from_date, to_date, selected_data):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = resource_path("TimeKeeping\\payTrans\\paytrans.ui")
        loadUi(ui_file, self)

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.lblFrom.setText(from_date)
        self.lblTo.setText(to_date)

        # Store the selected data
        self.selected_data = selected_data

        print(f"Received Data: {self.selected_data}")
        logging.info(f"Received Data: {self.selected_data}")

        self.populatePayTransTable(self.selected_data)

    def populatePayTransTable(self, data):
        self.paytransTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(row['EmpNo'])
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            present_days_item = QTableWidgetItem(row['Present Days'])

            emp_name_item.setToolTip(row['EmpName'])

            # Centers all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, present_days_item]:
                item.setTextAlignment(Qt.AlignCenter)

            # Logging the row data being added
            logging.info(f"Adding row {i}: {row}")

            self.paytransTable.setItem(i, 0, emp_no_item)
            self.paytransTable.setItem(i, 1, bio_num_item)
            self.paytransTable.setItem(i, 2, emp_name_item)
            self.paytransTable.setItem(i, 5, present_days_item)