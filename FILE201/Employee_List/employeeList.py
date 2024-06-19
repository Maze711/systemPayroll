from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from FILE201.file201_Function.listFunction import ListFunction
import os

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = os.path.join(os.path.dirname(__file__), 'employeeList.ui')
        loadUi(ui_file, self)

        self.functions = ListFunction(self)

        # Calls the timeClock recursively every 1 second
        self.timer = QTimer()
        self.timer.timeout.connect(self.functions.timeClock)
        self.timer.start(1)

