import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from FILE201.Employee_List.employeeList import EmployeeList
from TimeKeeping.datImporter.dialogLoader import dialogModal
from FILE201.fontLoader import load_fonts

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ui_file = os.path.join(os.path.dirname(__file__), 'Main.ui')
        loadUi(ui_file, self)

        self.functions = self

        # Window Connections
        self.btnEmployeeList.clicked.connect(self.employeeWindow)
        self.btnTimeKeeping.clicked.connect(self.dialogWindow)

    def employeeWindow(self):
        self.employee_list_window = EmployeeList()
        self.employee_list_window.show()

    def dialogWindow(self):
        self.timekeeping_window = dialogModal()
        self.timekeeping_window.show()

def main():
    app = QApplication(sys.argv)
    load_fonts()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
