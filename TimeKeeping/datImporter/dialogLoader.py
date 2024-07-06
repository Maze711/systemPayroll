import sys
import os
import logging

from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QProgressBar
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
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

    def importTxt(self):
        self.progressBar.setVisible(True)
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            try:
                file_size = os.path.getsize(fileName)
                chunk_size = 1024  # Read in chunks of 1KB
                progress = 0
                with open(fileName, 'r') as file:
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            break
                        progress += len(chunk)
                        self.progressBar.setValue(int(progress / file_size * 100))
                        QApplication.processEvents()  # Allow UI updates
                    file.seek(0)
                    content = file.read()
                    #logging.info(f"File {fileName} content:\n{content}")
                    self.showData(content)
                    self.close()
            except Exception as e:
                logging.error(f"Failed to read file {fileName}: {e}")
        self.progressBar.setVisible(False)

    def showData(self, content):
        self.time_logger = timelogger(content)  # Pass the content to timelogger
        self.time_logger.show()

