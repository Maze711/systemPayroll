from MainFrame.Payroll.payroll_functions.payViewListFunctions import viewListFunctions
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class paytimesheetViewList(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1070, 670)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList_Rate.ui")
        loadUi(ui_file, self)
        self.btnExportRateList = self.findChild(QPushButton, "btnExportRateList")

        self.functions = viewListFunctions(self)

        self.functions.populateEmpSalaryList()
        if self.btnExportRateList:
            self.btnExportRateList.clicked.connect(self.functions.exportEmpRateList)
        else:
            print("btnExportRateList not found!")
