from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class schedChanger(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1070, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\SLVL.ui")
        loadUi(ui_file, self)