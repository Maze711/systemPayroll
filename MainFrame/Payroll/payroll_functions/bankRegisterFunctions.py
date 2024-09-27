import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.DBConnection import create_connection
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

class BankRegisterFunctions:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

    def populateBankRegisterTable(self, data):
        self.parent.bankregisterTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_num = QTableWidgetItem(row['EmpNum'])
            bio_num = QTableWidgetItem(row['BioNum'])
            emp_name = QTableWidgetItem(row['EmpName'])
            account_num = QTableWidgetItem(str(row['AccountNo']))
            net_pay = QTableWidgetItem(str(row['NetPay']))

            for item in [emp_num, bio_num, emp_name, account_num, net_pay]:
                item.setTextAlignment(Qt.AlignCenter)

            self.parent.bankregisterTable.setItem(i, 0, emp_num)
            self.parent.bankregisterTable.setItem(i, 1, bio_num)
            self.parent.bankregisterTable.setItem(i, 2, emp_name)
            self.parent.bankregisterTable.setItem(i, 3, account_num)
            self.parent.bankregisterTable.setItem(i, 4, net_pay)