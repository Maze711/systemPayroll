import sys
import os

from openpyxl.workbook import Workbook

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Payroll.paytimeSheet.paytimeSheet import PaytimeSheet
from MainFrame.Database_Connection.DBConnection import create_connection

class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        # When using a book1 excel file the daypresent should be dayspresent
        self.required_columns = [
            'bionum', 'empnumber', 'empname', 'costcenter', 'fromdate', 'todate', 'daypresent', 'restday',
            'holiday', 'rsthlyday', 'orddaynite', 'rstdaynite', 'hlydaynite', 'rsthlydayn', 'orddayot',
            'rstdayot', 'hlydayot', 'rsthlydayo', 'orddaynit2', 'rstdaynit2', 'hlydaynit2', 'rsthlyday2',
            'late', 'undertime', 'absent', 'dateposted', 'remarks', 'rstshlyday', 'rstshlyda2', 'rstshlyda3',
            'rstshlyda4', 'empcompany', 'legalholid'
        ]

    def process(self):
        try:
            content = []
            file_ext = self.fileName.lower()

            if file_ext.endswith('.xlsx'):
                workbook = openpyxl.load_workbook(self.fileName, data_only=True)
                sheet = workbook.active
                headers = [cell.value for cell in sheet[1]]
                total_rows = sheet.max_row
                for row_idx in range(2, total_rows + 1):  # Skip header row
                    row = [sheet.cell(row=row_idx, column=col_idx).value for col_idx in range(1, sheet.max_column + 1)]
                    content.append(row)
                    progress = int((row_idx / total_rows) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)  # Simulate work being done
            elif file_ext.endswith('.xls'):
                workbook = xlrd.open_workbook(self.fileName, encoding_override="cp1252")
                sheet = workbook.sheet_by_index(0)
                headers = sheet.row_values(0)
                total_rows = sheet.nrows
                for row_idx in range(1, total_rows):  # Skip header row
                    row = sheet.row_values(row_idx)
                    content.append(row)
                    progress = int((row_idx / total_rows) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)  # Simulate work being done
            else:
                raise ValueError(f"Unsupported file format: {file_ext.split('.')[-1]}")

            # Validate columns
            formatted_headers = [header.strip().lower() if header is not None else '' for header in headers]
            missing_columns = [col for col in self.required_columns if col not in formatted_headers]

            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            content.insert(0, headers)  # Add header row to content
            self.finished.emit(content)
        except ValueError as ve:
            self.error.emit(str(ve))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")

class PayrollImporterFunctions:
    def __init__(self, dialog, user_role):
        self.dialog = dialog
        self.user_role = user_role

    def exportDeductionToExcel(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            return

        cursor = connection.cursor()

        try:
            query = "SELECT * FROM deductions"
            cursor.execute(query)
            result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            # Create a new workbook and select the active worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Deductions"

            # Write column headers
            ws.append(column_names)

            # Write data rows
            for row in result:
                ws.append(row)

            # Prompt the user to choose a file location and name
            file_name, _ = QFileDialog.getSaveFileName(self.dialog, "Save File", "", "Excel Files (*.xlsx);;All Files (*)")
            if file_name:
                # Save the workbook
                wb.save(file_name)
                QMessageBox.information(self.dialog, "Export Successful", "Deductions Data was exported successfully!")
                print(f"Data exported successfully to {file_name}")

        except Error as e:
            print(f"Error fetching or processing deduction data: {e}")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def importTxt(self):
        fileName, _ = QFileDialog.getOpenFileName(self.dialog, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")

        if not fileName:
            QMessageBox.information(self.dialog, "No File Selected", "Please select an Excel file to import.")
            return

        # Use FileProcessor to handle the file reading
        self.dialog.progressBar.setVisible(True)
        self.dialog.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = FileProcessor(fileName)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.fileProcessingFinished)
        self.worker.error.connect(self.fileProcessingError)
        self.thread.started.connect(self.worker.process)
        self.thread.start()

    def updateProgressBar(self, value):
        self.dialog.progressBar.setValue(value)
        if value == 100:
            self.dialog.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fileProcessingFinished(self, content):
        self.dialog.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        # Validate columns and show data
        if content:
            headers = content[0]
            data = content[1:]
            # required_columns = [
            #     'bionum', 'empnumber', 'empname', 'costcenter', 'fromdate', 'todate', 'dayspresent', 'restday',
            #     'holiday', 'rsthlyday', 'orddaynite', 'rstdaynite', 'hlydaynite', 'rsthlydayn', 'orddayot',
            #     'rstdayot', 'hlydayot', 'rsthlydayo', 'orddaynit2', 'rstdaynit2', 'hlydaynit2', 'rsthlyday2',
            #     'late', 'undertime', 'absent', 'dateposted', 'remarks', 'rstshlyday', 'rstshlyda2', 'rstshlyda3',
            #     'rstshlyda4', 'empcompany', 'legalholid'
            # ]

            #When using a XLS this will be the column
            required_columns = [
                'bionum', 'empnumber', 'empname', 'costcenter', 'fromdate', 'todate', 'daypresent', 'restday',
                'holiday', 'rsthlyday', 'orddaynite', 'rstdaynite', 'hlydaynite', 'rsthlydayn', 'orddayot',
                'rstdayot', 'hlydayot', 'rsthlydayo', 'orddaynit2', 'rstdaynit2', 'hlydaynit2', 'rsthlyday2',
                'late', 'undertime', 'absent', 'dateposted', 'remarks', 'rstshlyday', 'rstshlyda2', 'rstshlyda3',
                'rstshlyda4', 'empcompany', 'legalholid'
            ]

            # Check for None and safely strip and lower case headers
            formatted_headers = [header.strip().lower() if header is not None else '' for header in headers]

            missing_columns = [col for col in required_columns if col not in formatted_headers]

            if missing_columns:
                error_message = f"Missing required columns: {', '.join(missing_columns)}"
                QMessageBox.warning(self, "Missing Columns", error_message)
                return

            self.showData(content, self.user_role)

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.dialog.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.dialog, "File Processing Error", f"An error occurred while processing the file:\n{error}")
        self.dialog.close()

    def showData(self, content, user_role):
        self.paytimesheet = PaytimeSheet(self.dialog.main_window, content, user_role)  # Pass user_role
        self.dialog.main_window.open_dialogs.append(self.paytimesheet)
        print(content)
        self.paytimesheet.show()
        self.dialog.close()