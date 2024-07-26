import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMainWindow
from PyQt5.uic import loadUi
from Logger_config import get_logger

logging = get_logger()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PayTrans(QMainWindow):
    def __init__(self, from_date, to_date, data):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = resource_path("TimeKeeping\\payTrans\\paytrans.ui")
        loadUi(ui_file, self)

        self.data = data
        self.from_date = from_date
        self.to_date = to_date

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.populatePayTransTable(self.data)

    def populatePayTransTable(self, data):
        self.paytransTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(row['EmpNo'])
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            present_days_item = QTableWidgetItem(row['Present Days'])
            rate_item = QTableWidgetItem(row.get('Rate', 'Missing'))  # Get rate or 'Missing' if not found

            # Centers all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, present_days_item, rate_item]:
                item.setTextAlignment(Qt.AlignCenter)

            self.paytransTable.setItem(i, 0, emp_no_item)
            self.paytransTable.setItem(i, 1, bio_num_item)
            self.paytransTable.setItem(i, 2, emp_name_item)
            self.paytransTable.setItem(i, 4, rate_item)
            self.paytransTable.setItem(i, 5, present_days_item)