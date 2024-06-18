from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
import os

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = os.path.join(os.path.dirname(__file__), 'employeeList.ui')
        loadUi(ui_file, self)
