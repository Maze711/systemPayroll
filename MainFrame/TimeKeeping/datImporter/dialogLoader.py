from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.timeCardMaker.timeCard import timecard
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.timekeeper_functions.dialogFunctions import import_dat_file, check_if_table_exists

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 215)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(lambda: import_dat_file(self))
        self.btnProcessTimeCard.clicked.connect(lambda: self.validateToOpen())

        if hasattr(self, 'progressBar'):
            self.progressBar.setVisible(False)

        if hasattr(self, 'btnExportToExcel'):
            self.btnExportToExcel.setVisible(False)

    def openTimeCard(self):
        self.timeCardDialog = timecard()
        self.close()
        self.timeCardDialog.exec_()

    def validateToOpen(self):
        if check_if_table_exists(self):
            self.timeCardDialog = timecard()
            self.close()
            self.timeCardDialog.exec_()
        else:
            QMessageBox.information(self, "No DAT Found", "No DAT found, please import a DAT first.")