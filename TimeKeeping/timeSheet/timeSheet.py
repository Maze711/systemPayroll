import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem, \
    QHeaderView
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeSheet()
    window.show()
    sys.exit(app.exec_())