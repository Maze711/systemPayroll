from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
import sys

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        loadUi("employeeList.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = EmployeeList()
    ui.show()
    app.exec()