from MainFrame.Resources.lib import *

from TimeKeeping.timeLogger.timeLog import timelogger
from MainFrame.systemFunctions import globalFunction, single_function_logger


class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    @single_function_logger.log_function
    def process(self):
        try:
            temp_folder = "temp_folder"
            os.makedirs(temp_folder, exist_ok=True)

            with open(self.fileName, 'r') as file:
                lines = file.readlines()

            total_lines = len(lines)
            chunk_size = 200
            chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]

            for i, chunk in enumerate(chunks):
                chunk_file = os.path.join(temp_folder, f"chunk_{i}.txt")
                with open(chunk_file, 'w') as cf:
                    cf.writelines(chunk)
                self.progressChanged.emit(int(((i + 1) / len(chunks)) * 100))
                QThread.msleep(1)

            self.finished.emit(temp_folder)
        except Exception as e:
            self.error.emit(str(e))

class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

    @single_function_logger.log_function
    def importTxt(self, *args):
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
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fileProcessingFinished(self, temp_folder):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        self.processChunks(temp_folder)
        self.deleteChunkFiles(temp_folder)

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

    def deleteChunkFiles(self, temp_folder):
        for file_name in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Failed to delete file {file_path}: {e}")

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
        self.close()