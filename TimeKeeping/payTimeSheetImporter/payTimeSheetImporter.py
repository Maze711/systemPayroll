from MainFrame.Resources.lib import *

from TimeKeeping.paytimeSheet.paytimeSheet import PaytimeSheet
from MainFrame.systemFunctions import globalFunction, single_function_logger


class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def process(self):
        try:
            workbook = xlrd.open_workbook(self.fileName, encoding_override="cp1252")
            sheet = workbook.sheet_by_index(0)

            total_rows = sheet.nrows
            content = []

            # Read the header row separately
            headers = sheet.row_values(0)  # Read header row
            content.append(headers)  # Add header row to content

            for row_idx in range(1, total_rows):  # Skip header row
                row = sheet.row_values(row_idx)
                content.append(row)
                progress = int((row_idx / total_rows) * 100)
                self.progressChanged.emit(progress)
                QThread.msleep(1)  # Simulate work being done

            self.finished.emit(content)
        except Exception as e:
            self.error.emit(str(e))


class PayrollDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

    def importTxt(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")

        if not fileName:
            return

        # Use FileProcessor to handle the file reading
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

    @single_function_logger.log_function
    def fileProcessingFinished(self, content):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        # Validate columns and show data
        if content:
            headers = content[0]
            data = content[1:]
            required_columns = [
                'bionum', 'empnumber', 'empname', 'costcenter', 'fromdate', 'todate', 'dayswork', 'restday',
                'holiday', 'rsthlyday', 'orddaynite', 'rstdaynite', 'hlydaynite', 'rsthlydayn', 'orddayot',
                'rstdayot', 'hlydayot', 'rsthlydayo', 'orddaynit2', 'rstdaynit2', 'hlydaynit2', 'rsthlyday2',
                'late', 'undertime', 'absent', 'dateposted', 'remarks', 'rstshlyday', 'rstshlyda2', 'rstshlyda3',
                'rstshlyda4', 'empcompany', 'legalholid'
            ]

            missing_columns = [col for col in required_columns if
                               col not in [header.strip().lower() for header in headers]]

            if missing_columns:
                error_message = f"Missing required columns: {', '.join(missing_columns)}"
                QMessageBox.warning(self, "Missing Columns", error_message)
                return

            self.showData(content)

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

    def showData(self, content):
        self.paytimesheet = PaytimeSheet(content)
        self.paytimesheet.show()
        self.close()
