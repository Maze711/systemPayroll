import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class payAddEmployee(QDialog):
    def __init__(self):
        super(payAddEmployee, self).__init__()
        self.setFixedSize(1065, 506)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList_Accountant.ui")
        loadUi(ui_file, self)