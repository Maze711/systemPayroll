import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.payroll_functions.deductionFunctions import DeductionUI
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.payroll_functions.paytimeSheetFunctions import PaytimeSheetUI
from MainFrame.systemFunctions import timekeepingFunction

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
            self.payTimeFunctions = PaytimeSheetUI(self)
            self.setupPayTimeSheetUI()
        elif user_role == "Pay Master 2":
            self.deductionFunctions = DeductionUI(self)
            self.setupDeductionUI()

    def setupPayTimeSheetUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

            self.btnPayTrans.clicked.connect(self.payTimeFunctions.createPayTrans)

            if self.txtSearch is not None:
                self.txtSearch.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
            else:
                logging.error("Error: searchBioNum QLineEdit not found in the UI.")

            self.payTimeFunctions.populatePaytimeSheetTable(self.data)
            logging.info("Table populated with data.")

        except Exception as e:
            logging.error(f"Error in setupPayTimeSheetUI: {e}")


    def setupDeductionUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

            self.btnEdit = self.findChild(QPushButton, 'btnEdit')
            self.placeBTN = self.findChild(QPushButton, 'placeBTN')
            self.btnStore = self.findChild(QPushButton, 'btnStore')
            self.txtSearch = self.findChild(QLineEdit, 'txtSearch')

            if self.btnEdit:
                self.btnEdit.clicked.connect(self.deductionFunctions.showDeductionUI)
            else:
                logging.error("Error: btnEdit QPushButton not found in the UI.")

            if self.btnStore:
                self.btnStore.clicked.connect(self.deductionFunctions.showStoreDeductionLoader)
            else:
                logging.error("Error: btnStore QPushButton not found in the UI.")

            if self.txtSearch:
                self.txtSearch.textChanged.connect(self.deductionFunctions.filterTable)
            else:
                logging.error("Error: txtSearch QLineEdit not found in the UI.")

            self.deductionFunctions.populatePaytimeSheetTable(self.data)
        except Exception as e:
            logging.error(f"Error in setupDeductionUI: {e}")