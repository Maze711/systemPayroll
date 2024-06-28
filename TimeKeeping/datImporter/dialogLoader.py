import sys
import os
import logging

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from TimeKeeping.timeLogger.timeLog import timelogger  # Import timelogger class

# Configure the logger
#logging.basicConfig(level=logging.INFO, filename='TimeKeeping/file_import.log',
                    #format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        #loadUi(os.path.join(os.path.dirname(__file__), 'dialogImporter.ui'), self)
        ui_file = (resource_path("TimeKeeping\\datImporter\\dialogImporter.ui"))
        loadUi(ui_file, self)
        self.importBTN.clicked.connect(self.importTxt)

    def importTxt(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    content = file.read()
                    #logging.info(f"File {fileName} content:\n{content}")
                    self.showData(content)
                    self.close()
            except Exception as e:
                logging.error(f"Failed to read file {fileName}: {e}")

    def showData(self, content):
        self.time_logger = timelogger(content)  # Pass the content to timelogger
        self.time_logger.show()