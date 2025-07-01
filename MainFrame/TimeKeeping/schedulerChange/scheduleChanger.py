from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.timekeeper_functions.timecardFunctions import populateList
from MainFrame.TimeKeeping.schedulerChange.employeeDataHandler import EmployeeDataHandler
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class schedChanger(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1597, 666)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\SLVL.ui")
        loadUi(ui_file, self)

        # Initialize employee data handler
        self.employee_data_handler = EmployeeDataHandler(self)

        # Department combo
        self.populateComboBox = populateList(self)
        self.populateComboBox.populateCostCenterBox()

        # Table appearance
        self.bankregisterTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.bankregisterTable.horizontalHeader().setStretchLastSection(True)
        self.bankregisterTable.setEditTriggers(QAbstractItemView.AllEditTriggers)

        # Load employees
        self.load_employee_data()

    def load_employee_data(self):
        """Load employee data"""
        self.employee_data_handler.load_employee_data()
