import sys
import os
import logging

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QProgressBar
from PyQt5.uic import loadUi
from TimeKeeping.timeLogger.timeLog import timelogger  # Import timelogger class

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='TimeKeeping/file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def process(self):
        try:
            temp_folder = "temp_folder"
            os.makedirs(temp_folder, exist_ok=True)

            with open(self.fileName, 'r') as file:
                lines = file.readlines()

            total_lines = len(lines)
            chunk_size = 100
            chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]

            for i, chunk in enumerate(chunks):
                chunk_file = os.path.join(temp_folder, f"chunk_{i}.txt")
                with open(chunk_file, 'w') as cf:
                    cf.writelines(chunk)
                self.progressChanged.emit(int(((i + 1) / len(chunks)) * 100))

            self.finished.emit(temp_folder)
        except Exception as e:
            self.error.emit(str(e))

class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        ui_file = resource_path("TimeKeeping\\datImporter\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

    def importTxt(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            self.thread = QThread()
            self.worker = FileProcessor(fileName)
            self.worker.moveToThread(self.thread)
            self.worker.progressChanged.connect(self.updateProgressBar)
            self.worker.finished.connect(self.fileProcessingFinished)
            self.worker.error.connect(self.fileProcessingError)
            self.thread.started.connect(self.worker.process)
            self.thread.start()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def fileProcessingFinished(self, temp_folder):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        self.processChunks(temp_folder)

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

    def processChunks(self, temp_folder):
        content = ""
        for file_name in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, file_name)
            with open(file_path, 'r') as file:
                content += file.read()
        self.showData(content)

    def showData(self, content):
        self.time_logger = timelogger(content)  # Pass the content to timelogger
        self.time_logger.show()