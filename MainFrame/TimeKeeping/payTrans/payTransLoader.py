import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
from MainFrame.TimeKeeping.payroll_functions.payTransFunctions import PayTransFunctions
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PayTrans(QMainWindow):
    def __init__(self, from_date, to_date, data):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytrans.ui")
        loadUi(ui_file, self)

        self.data = data
        self.original_data = data  # Store original data
        self.from_date = from_date
        self.to_date = to_date

        self.functions = PayTransFunctions(self)

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.functions.populatePayTransTable(self.data)
        self.btnPayTrans.clicked.connect(self.functions.export_to_excel)
        self.btnSendToEmail.clicked.connect(self.functions.openEmailLoader)
        self.btnInsertDeduction.clicked.connect(self.functions.insertDeductionToTable)