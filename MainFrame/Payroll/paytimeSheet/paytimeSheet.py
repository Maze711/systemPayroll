import sys
import os
import threading

import requests

from MainFrame.Database_Connection.notification_listener import NotificationService

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.Payroll.payroll_functions.deductionFunctions import DeductionFunctions
from MainFrame.systemFunctions import globalFunction
from MainFrame.Payroll.payroll_functions.paytimeSheetFunctions import PaytimeSheetFunctions
from MainFrame.systemFunctions import timekeepingFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PaytimeSheet(QMainWindow):
    def __init__(self, main_window, content, user_role):
        super(PaytimeSheet, self).__init__()
        self.setFixedSize(1700, 665)

        # Initialize NotificationService and start it in a background thread
        self.notification_service = NotificationService()
        self.notification_thread = threading.Thread(target=self.notification_service.run)
        self.notification_thread.start()

        time.sleep(6)

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
            self.payTimeFunctions = PaytimeSheetFunctions(self)
            self.populatePaytimeSheetTable = self.payTimeFunctions.populatePaytimeSheetTable
            self.setupPayTimeSheetUI()
        elif user_role == "Pay Master 2":
            self.deductionFunctions = DeductionFunctions(self)
            self.populatePaytimeSheetTable = self.deductionFunctions.populatePaytimeSheetTable
            self.setupDeductionUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_indication_lbl)
        self.timer.start(2000)  # Update every 2 seconds

    def setupPayTimeSheetUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)

            self.btnPayTrans.clicked.connect(self.payTimeFunctions.createPayTrans)
            self.btnNotification.clicked.connect(self.payTimeFunctions.showNewListEmployee)

            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))

            self.populatePaytimeSheetTable(self.original_data)

            # Initially set the indication label
            self.update_indication_lbl()

        except Exception as e:
            logging.error(f"Error in setupPayTimeSheetUI: {e}")

    def setupDeductionUI(self):
        try:
            self.paytimesheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.paytimesheetTable.horizontalHeader().setStretchLastSection(True)
            self.paytimesheetTable.cellDoubleClicked.connect(self.deductionFunctions.showDeductionUI)

            self.btnEdit.clicked.connect(self.deductionFunctions.showDeductionUI)

            self.btnStore.clicked.connect(self.deductionFunctions.showStoreDeductionLoader)

            self.searchBioNum.textChanged.connect(self.deductionFunctions.filterTable)

            self.populatePaytimeSheetTable(self.original_data)
        except Exception as e:
            logging.error(f"Error in setupDeductionUI: {e}")

    def update_indication_lbl(self):
        # Fetch the last checked ID from NotificationService
        last_checked = self.notification_service.get_last_checked()
        self.indicationLbl.setText(str(last_checked))