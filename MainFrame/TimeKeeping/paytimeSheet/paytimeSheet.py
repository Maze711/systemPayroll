import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.payroll_functions.deductionFunctions import DeductionUI
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.payroll_functions.paytimeSheetFunctions import PaytimeSheetUI

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PaytimeSheet(QMainWindow):
    def __init__(self, main_window, content, user_role):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)

        # Load different UI based on user_role
        if user_role == "Pay Master 2":
            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\payDeduction.ui")
        else:
            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytimesheet.ui")

        loadUi(ui_file, self)

        self.main_window = main_window
        self.data = content
        self.user_role = user_role
        self.original_data = content  # Store original data

        if user_role == "Pay Master 1":
            self.uiHandler = PaytimeSheetUI(self)
            self.uiHandler.setupUI()
        elif user_role == "Pay Master 2":
            self.uiHandler = DeductionUI(self)
            self.uiHandler.setupUI()
