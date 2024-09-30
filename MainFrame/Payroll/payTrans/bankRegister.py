import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
from MainFrame.Payroll.payroll_functions.bankRegisterFunctions import BankRegisterFunctions
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class bankRegister(QDialog):
    def __init__(self, from_date, to_date, data):
        super(bankRegister, self).__init__()
        self.setFixedSize(1070, 666)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\bankregister.ui")
        loadUi(ui_file, self)

        self.from_date = from_date
        self.to_date = to_date
        self.original_data = data
        self.data = data

        self.functions = BankRegisterFunctions(self, self.data)

        self.functions.populateBankRegisterTable(self.data)

        self.grandTotal.setText(format(self.functions.getGrandTotal(self.data), ','))

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')
        self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))

        self.btnExportBankRegister.clicked.connect(self.functions.exportBankRegisterToExcel)