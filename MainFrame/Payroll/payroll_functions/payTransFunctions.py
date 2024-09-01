import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Payroll.payTrans.payTransMailer import EmailerLoader
from MainFrame.Database_Connection.DBConnection import create_connection
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

class PayTransFunctions:
    def __init__(self, parent):
        self.parent = parent

        self.additional_buttons_container = None

    def populatePayTransTable(self, data):
        for row in range(self.parent.paytransTable.rowCount()):
            self.parent.paytransTable.setRowHidden(row, False)

        self.parent.paytransTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(row['EmpNo'])
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            basic_item = QTableWidgetItem(str(row['Basic']))
            present_days_item = QTableWidgetItem(row['Present Days'])
            rate_item = QTableWidgetItem(row.get('Rate', 'Missing'))  # Get rate or 'Missing' if not found
            ot_earn_item = QTableWidgetItem(str(row['OT_Earn']))  # Get OT_Earn or '0.00' if not found
            late_earn_item = QTableWidgetItem(str(row['LateUndertime']))
            undertime_earn_item = QTableWidgetItem(str(row['undertime']))

            # Adding deduction items to the table
            pay_ded_items = []
            for j in range(1, 15):
                deduction = row.get(f'Pay Ded {j}', 0)
                pay_ded_items.append(QTableWidgetItem(str(deduction)))

            # Center all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, basic_item, present_days_item, rate_item,
                        ot_earn_item, late_earn_item, undertime_earn_item] + pay_ded_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Set items in the table. Adjust the column indices as needed.
            self.parent.paytransTable.setItem(i, 0, emp_no_item)
            self.parent.paytransTable.setItem(i, 1, bio_num_item)
            self.parent.paytransTable.setItem(i, 2, emp_name_item)
            self.parent.paytransTable.setItem(i, 3, basic_item)  # Basic
            self.parent.paytransTable.setItem(i, 4, rate_item)   # Rate
            self.parent.paytransTable.setItem(i, 5, present_days_item)  # Present Days
            self.parent.paytransTable.setItem(i, 6, ot_earn_item)  # OT Hours (add column index here)
            self.parent.paytransTable.setItem(i, 7, late_earn_item)
            self.parent.paytransTable.setItem(i, 8, undertime_earn_item)

            # Add deduction items to the table in subsequent columns
            for j, pay_ded_item in enumerate(pay_ded_items, start=9): # Pay Ded columns starts at index 9
                self.parent.paytransTable.setItem(i, j, pay_ded_item)

    def export_to_excel(self, checked=False):
        # Define the file name where data will be saved
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self.parent, "Save As", "",
                                                   "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                globalFunction.export_to_excel(self.parent.data, file_name)
                QMessageBox.information(self.parent, "Export Successful", f"Data has been successfully exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {e}")
                logging.error(f"Export error: {e}")
        else:
            QMessageBox.information(self.parent, "No File Selected", "Please export an excel file.")
            return

    def checkIfDeductionTableNotExist(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database. Please check your "
                                                                 "connection or contact the system administrator")
            return

        cursor = connection.cursor()

        try:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if len(tables) > 0:
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return
        finally:
            cursor.close()
            connection.close()

    def insertDeductionToTable(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            self.hideAdditionalButtons()
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database. Please check your "
                                                          "connection or contact the system administrator")
            return

        if self.checkIfDeductionTableNotExist():
            print("Deduction table does not exist in SYSTEM_STORE_DEDUCTION database.")
            self.hideAdditionalButtons()
            QMessageBox.warning(self.parent, "Insert Error", "There are no processed deductions available. "
                                                             "Please contact Pay Master 2")
            return

        message = QMessageBox.question(self.parent, "Importing Deduction",
                                       "Are you sure you want to insert/import deductions in the table?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message != QMessageBox.Yes:
            self.hideAdditionalButtons()
            return

        cursor = connection.cursor()

        try:

            for index, row in enumerate(self.parent.original_data):
                emp_no = row['EmpNo']
                query = f""" SELECT payDed1, payDed2, payDed3, payDed4, payDed5, payDed6, payDed7, payDed8, payDed9, 
                             payDed10, payDed11, payDed12, payDed13, payDed14 FROM deductions WHERE empNum = %s
                """
                cursor.execute(query, (emp_no,))
                result = cursor.fetchone()

                # Adds the deductions to each dictionary
                for i in range(0, 14):
                    row.update({f'Pay Ded {i + 1}': result[i]})

            self.hideAdditionalButtons()

            QMessageBox.information(self.parent, "Insertion Successful", "Deduction has been inserted in the "
                                                                         "table successfully!")
            # repopulate the table with the updated data
            self.populatePayTransTable(self.parent.original_data)

        except Error as e:
            self.hideAdditionalButtons()
            QMessageBox.warning(self.parent, "Insertion Error", f"Error fetching or processing deduction data: {e}")
            print(f"Error fetching or processing deduction data: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def openEmailLoader(self):
        message = QMessageBox.question(self.parent, "Sending Email", "Are you sure you want to send an email?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.emailerLoader = EmailerLoader(self.parent.original_data, self.parent)
            self.emailerLoader.show()

    def showButtonsContainer(self):
        # If the container already exists and is visible, do nothing
        if self.additional_buttons_container and self.additional_buttons_container.isVisible():
            return

        # If the container exists but is hidden, just show it
        if self.additional_buttons_container:
            self.additional_buttons_container.show()
        else:
            # Create the container if it doesn't exist
            button_width = 180
            button_height = 45
            frame_width = button_width + 20
            frame_height = 2 * button_height + 25
            left_offset = self.parent.sideBar.frameGeometry().left() - 195
            top_offset = self.parent.widget_2.frameGeometry().top() + 93

            self.additional_buttons_container = QWidget(self.parent.centralwidget)
            self.additional_buttons_container.setGeometry(left_offset, top_offset, frame_width, frame_height)
            self.additional_buttons_container.setStyleSheet(
                "background-color: #DCE5FE; border: 1px solid gray;")

            additional_button_texts = ["Import from Excel", "Import from Database"]
            for i, text in enumerate(additional_button_texts):
                button = QPushButton(text, self.additional_buttons_container)
                button.setGeometry(10, 10 + i * (button_height + 5), button_width, button_height)
                button.setStyleSheet("background-color: white; font-family: Poppins; font-size: 10pt;"
                                     "font-weight: bold;")
                button.setCursor(Qt.PointingHandCursor)
                button.installEventFilter(self.parent)
                button.clicked.connect(self.button_functions(text))

            self.additional_buttons_container.show()

    def button_functions(self, btn_type):
        functions = {
            'Import from Excel': self.importFromExcel,
            'Import from Database': self.insertDeductionToTable
        }
        return functions.get(btn_type)

    def checkAndHideAdditionalButtons(self):
        cursor_pos = QCursor.pos()
        if not self.parent.btnInsertDeduction.geometry().contains(self.parent.mapFromGlobal(cursor_pos)):
            if self.additional_buttons_container:
                if not self.additional_buttons_container.geometry().contains(self.parent.mapFromGlobal(cursor_pos)):
                    self.hideAdditionalButtons()

    def hideAdditionalButtons(self):
        if self.additional_buttons_container:
            self.additional_buttons_container.hide()

    def importFromExcel(self):
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Select Excel File", "",
                                                   "Excel Files (*.xls *.xlsx)")
        if not file_name:
            self.hideAdditionalButtons()
            QMessageBox.information(self.parent, "No File Selected", "Please select an Excel file to import.")
            return

        self.hideAdditionalButtons()
        self.ImportFromExcelLoader = ImportFromExcelLoader(file_name, self.parent.original_data, self.parent)
        self.ImportFromExcelLoader.show()

class ImportFromExcelLoader(QDialog):
    def __init__(self, file, data, payTrans_window):
        super(ImportFromExcelLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        self.data = data
        self.file = file
        self.payTrans_window = payTrans_window

        self.functions = PayTransFunctions(self.payTrans_window)


        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = FileProcessor(self.file, self.data)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.insertingExcelDeductionFinished)
        self.worker.error.connect(self.insertingExcelDeductionError)
        self.thread.started.connect(self.worker.process)
        self.thread.start()

        self.move_to_bottom_right()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def insertingExcelDeductionFinished(self, data):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        self.functions.populatePayTransTable(data)
        QMessageBox.information(self.payTrans_window, "Insertion Successful", "Deduction has been inserted in "
                                                                              "the table successfully!")
        self.close()

    def insertingExcelDeductionError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.payTrans_window, "Insertion Error", error)
        self.close()

    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)

class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, file_name, data):
        super().__init__()
        self.file_name = file_name
        self.data = data

    def process(self):
        try:
            # Determine the appropriate engine based on the file extension
            if self.file_name.endswith('.xlsx'):
                df = pd.read_excel(self.file_name, sheet_name=None, engine='openpyxl')
            elif self.file_name.endswith('.xls'):
                df = pd.read_excel(self.file_name, sheet_name=None, engine='xlrd')
            else:
                self.error.emit("Unsupported file format")
                raise ValueError("Unsupported file format")

            sheet = df[list(df.keys())[0]]  # Get the first sheet

            # Fetch the headers from the DataFrame
            headers = sheet.columns.tolist()

            required_columns = ['ID', 'empNum', 'bioNum', 'empName'] + [f'payDed{i}' for i in range(1, 15)]

            missing_columns = [col for col in required_columns if
                               col not in headers[:18]]  # excludes the deduction placed by and date

            if missing_columns:
                self.error.emit(f"Missing required columns: {', '.join(missing_columns)}")
                return

            # Convert empNum column to string type
            sheet['empNum'] = sheet['empNum'].astype(str)

            total_rows = sheet.shape[0] - 1 # excluding the header

            print(total_rows)

            # Iterate over the original_data and update payDed keys based on empNum
            for i, row in enumerate(self.data):
                emp_no = str(row['EmpNo'])

                # Check if this EmpNo is in the imported sheet
                matching_rows = sheet[sheet['empNum'] == emp_no]

                if not matching_rows.empty:
                    # Update the Pay Ded keys for this EmpNo
                    for j in range(1, 15):
                        row[f'Pay Ded {j}'] = int(matching_rows.iloc[0][f'payDed{j}'])

                # Navigates the current progress
                progress = int(((i + 1) / total_rows) * 100)
                self.progressChanged.emit(progress)
                QThread.msleep(1)  # Simulate work being done

            self.finished.emit(self.data)
        except Exception as e:
            self.error.emit(f"Failed to process .xlsx file: {e}")