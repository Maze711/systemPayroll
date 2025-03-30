from MainFrame.Payroll.payroll_functions.payViewListFunctions import viewListFunctions
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class paytimesheetViewList(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1070, 670)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList_Rate.ui")
        loadUi(ui_file, self)
        self.btnExportRateList = self.findChild(QPushButton, "btnExportRateList")

        self.functions = viewListFunctions(self)

        # Store original data before any filtering
        self.original_data = self.functions.data.copy() if self.functions.data else []

        self.functions.populateEmpSalaryList()

        if self.btnExportRateList:
            self.btnExportRateList.clicked.connect(self.functions.exportEmpRateList)
        else:
            print("btnExportRateList not found!")

        if hasattr(self, 'searchBioNum'):
            self.searchBioNum.textChanged.connect(self.handleSearch)
        else:
            print("searchBioNum not found!")

    def handleSearch(self):
        # Ensure we have original data stored
        if not hasattr(self, 'original_data') and hasattr(self.functions, 'data'):
            self.original_data = self.functions.data.copy()
        timekeepingFunction.searchBioNumFunction(self)
