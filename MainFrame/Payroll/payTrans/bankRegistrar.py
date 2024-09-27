import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class bankRegistrar(QDialog):
    def __init__(self):
        super(bankRegistrar, self).__init__()
        self.setFixedSize(1471, 666)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\bankregistrar.ui")
        loadUi(ui_file, self)

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')
        self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
