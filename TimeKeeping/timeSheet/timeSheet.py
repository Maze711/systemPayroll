import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.uic import loadUi

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TimeSheet(QMainWindow):
    def __init__(self):
        super(TimeSheet, self).__init__()
        self.setFixedSize(1180, 665)
        ui_file = resource_path("TimeSheet.ui")
        loadUi(ui_file, self)

        self.setupTable()

    def setupTable(self):
        # Ensure the table has the correct number of rows and columns
        self.TimeSheetTable.setColumnCount(10)  # Total columns you have

        # Set headers (if not already set in Designer)
        headers = ["Bio No.", "ID", "Employee", "Hours Worked", "",'', "Night Differential",
                   "OT w/ ND"]
        self.TimeSheetTable.setHorizontalHeaderLabels(headers)

        # Merge cells for "Overtime" header
        self.TimeSheetTable.setSpan(0, 4, 1, 2)  # Merge cells for the "Overtime" header
        self.TimeSheetTable.setItem(0, 4, QTableWidgetItem("Overtime"))

        # Add the subheaders "Regular" and "Holiday"
        self.TimeSheetTable.setItem(1, 4, QTableWidgetItem("Regular"))
        self.TimeSheetTable.setItem(1, 5, QTableWidgetItem("Holiday"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeSheet()
    window.show()
    sys.exit(app.exec_())