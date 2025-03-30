from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class paytimesheetViewList(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1070, 670)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList_Rate.ui")
        loadUi(ui_file, self)
