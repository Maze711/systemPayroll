import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.Payroll.payroll_functions.deductionFunctions import DeductionUI
from MainFrame.systemFunctions import globalFunction
from MainFrame.Payroll.payroll_functions.paytimeSheetFunctions import PaytimeSheetUI
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
        self.original_data = content  # Store original data
        self.data = content
        self.user_role = user_role

        self.searchBioNum = self.txtSearch

        if user_role == "Pay Master 1":
            self.payTimeFunctions = PaytimeSheetUI(self)
            self.populatePaytimeSheetTable = self.payTimeFunctions.populatePaytimeSheetTable
            self.setupPayTimeSheetUI()
        elif user_role == "Pay Master 2":
            self.deductionFunctions = DeductionUI(self)
            self.populatePaytimeSheetTable = self.deductionFunctions.populatePaytimeSheetTable
            self.setupDeductionUI()

    def setupPayTimeSheetUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

            self.btnPayTrans.clicked.connect(self.payTimeFunctions.createPayTrans)

            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))

            self.populatePaytimeSheetTable(self.original_data)
            logging.info("Table populated with data.")

        except Exception as e:
            logging.error(f"Error in setupPayTimeSheetUI: {e}")


    def setupDeductionUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

            self.btnEdit.clicked.connect(self.deductionFunctions.showDeductionUI)

            self.btnStore.clicked.connect(self.deductionFunctions.showStoreDeductionLoader)

            self.searchBioNum.textChanged.connect(self.deductionFunctions.filterTable)

            self.populatePaytimeSheetTable(self.original_data)
        except Exception as e:
            logging.error(f"Error in setupDeductionUI: {e}")