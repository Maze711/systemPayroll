import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.timeCardMaker.timeCard import timecard
from MainFrame.systemFunctions import globalFunction
from MainFrame.notificationMaker import notificationLoader
from MainFrame.Database_Connection.DBConnection import create_connection

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 215)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.btnProcessTimeCard.clicked.connect(self.validateToOpen)

        if hasattr(self, 'progressBar'):
            self.progressBar.setVisible(False)

        if hasattr(self, 'btnViewDeduction'):
            self.btnViewDeduction.setVisible(False)

    def importTxt(self, *args):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open DAT File", "", "DAT Files (*.DAT)")
        if fileName:
            QTimer.singleShot(2, self.openTimeCard)

            notification_dialog = notificationLoader(fileName)
            notification_dialog.exec_()
        else:
            QMessageBox.information(self, "No File Selected", "Please select a DAT file to import.")
            return

    def openTimeCard(self):
        self.timeCardDialog = timecard()
        self.close()
        self.timeCardDialog.exec_()

    def validateToOpen(self):
        if self.checkIfTableExists():
            self.timeCardDialog = timecard()
            self.close()
            self.timeCardDialog.exec_()
        else:
            QMessageBox.information(self, "No DAT Found", "No DAT found, please import a DAT first.")

    def checkIfTableExists(self):
        connection = create_connection('LIST_LOG_IMPORT')
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the LIST_LOG_IMPORT database.")
            return False

        cursor = connection.cursor()
        try:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            return len(tables) > 0
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return False
        finally:
            cursor.close()
            connection.close()