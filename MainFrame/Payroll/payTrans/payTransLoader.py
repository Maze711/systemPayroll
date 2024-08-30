import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
from MainFrame.Payroll.payroll_functions.payTransFunctions import PayTransFunctions
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
        self.populatePayTransTable = self.functions.populatePayTransTable

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')

        self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))

        self.populatePayTransTable(self.data)
        self.btnInsertDeduction.installEventFilter(self)
        self.btnPayTrans.clicked.connect(self.functions.export_to_excel)
        self.btnSendToEmail.clicked.connect(self.functions.openEmailLoader)

    def eventFilter(self, source, event):
        if source == self.btnInsertDeduction and not source.isEnabled():
            return False
        if source == self.btnInsertDeduction:
            if event.type() == QEvent.Enter:
                self.functions.showButtonsContainer()
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.functions.checkAndHideAdditionalButtons)
        elif self.functions.additional_buttons_container and source in self.functions.additional_buttons_container.children():
            if event.type() == QEvent.HoverEnter:
                source.setStyleSheet("background-color: #344273; color: white; font-family: Poppins; font-size: 10pt;"
                                     "font-weight: bold;")
            elif event.type() == QEvent.HoverLeave:
                source.setStyleSheet("background-color: white; font-family: Poppins; font-size: 10pt;"
                                     "font-weight: bold;")
            if event.type() == QEvent.Enter:
                return True
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.functions.checkAndHideAdditionalButtons)

        return super().eventFilter(source, event)