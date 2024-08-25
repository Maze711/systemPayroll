import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.Payroll.payroll_functions.payrollImporterFunctions import PayrollImporterFunctions


class PayrollDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # self.setFixedSize(418, 339)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.user_session = UserSession().getALLSessionData()
        self.user_role = str(self.user_session.get("user_role", ""))

        self.importerFunctions = PayrollImporterFunctions(self, self.user_role)

        self.configureButtons(self.user_role)

        self.importBTN.clicked.connect(self.importerFunctions.importTxt)
        self.importBTN.setText("Import Excel")

        self.btnExportToExcel.clicked.connect(self.importerFunctions.exportDeductionToExcel)

        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

    def configureButtons(self, user_role):
        """Configure button visibility based on the user role."""
        if user_role == "Pay Master 1":
            if hasattr(self, 'btnProcessTimeCard'):
                self.btnProcessTimeCard.setVisible(False)
            if hasattr(self, 'btnExportToExcel'):
                self.btnExportToExcel.setVisible(False)
        elif user_role == "Pay Master 2":
            if hasattr(self, 'btnProcessTimeCard'):
                self.btnProcessTimeCard.setVisible(False)
            if hasattr(self, 'btnExportToExcel'):
                self.btnExportToExcel.setVisible(True)