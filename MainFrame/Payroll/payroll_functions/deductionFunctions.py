import sys
import os
from openpyxl.workbook import Workbook

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, FileProcessor, ValidInteger
from MainFrame.Payroll.paytimeSheet.storeDeductionLoader import StoreDeductionLoader
from MainFrame.Database_Connection.DBConnection import create_connection

from MainFrame.Database_Connection.user_session import UserSession

class DeductionFunctions:
    def __init__(self, parent):
        self.parent = parent
        self.user_session = UserSession().getALLSessionData()

    def populatePaytimeSheetTable(self, data):
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)
        for row in range(self.parent.paytimesheetTable.rowCount()):
            self.parent.paytimesheetTable.setRowHidden(row, False)

        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'Late/Absent': 'late_absent',
            'SSS_Loan': 'sss_loan',
            'Pag_Ibig_Loan': 'pag_ibig_loan',
            'Cash_Advance': 'cash_advance',
            'Canteen': 'canteen',
            'Tax': 'tax',
            'SSS': 'sss',
            'Medicare/PhilHealth': 'medicare_philhealth',
            'PAGIBIG': 'pag_ibig',
            'Clinic': 'clinic',
            'Arayata_Annual': 'arayata_manual',
            'HMI': 'hmi',
            'Funeral': 'funeral',
            'Voluntary': 'voluntary'
        }

        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        for i, row in enumerate(data[1:]):
            for field_name, col_name in column_names.items():
                col_idx = col_indices.get(field_name)
                if col_idx is not None:
                    item = QTableWidgetItem(str(row[col_idx]))
                    if field_name in column_names:
                        item.setTextAlignment(Qt.AlignCenter)
                    if field_name == 'Employee Name':
                        item.setToolTip(row[col_idx])
                    self.parent.paytimesheetTable.setItem(i, list(column_names.keys()).index(field_name), item)
                else:
                    logging.warning(f"Column '{field_name}' not found in data.")
            logging.info(f"Adding row {i}: {row}")

    def filterTable(self):
        search_text = self.parent.txtSearch.text().strip().lower()
        row_count = self.parent.paytimesheetTable.rowCount()

        for row in range(row_count):
            item = self.parent.paytimesheetTable.item(row, 1)  # Bio Num column is assumed to be index 1
            if item and search_text in item.text().strip().lower():
                self.parent.paytimesheetTable.setRowHidden(row, False)
            else:
                self.parent.paytimesheetTable.setRowHidden(row, True)

    def showDeductionUI(self):
        selected_row = self.parent.paytimesheetTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
            return

        try:
            emp_name_item = self.parent.paytimesheetTable.item(selected_row, 2)
            bio_num_item = self.parent.paytimesheetTable.item(selected_row, 1)

            # Fetch all deductions
            deduction_values_mapping = {
                1: self.parent.paytimesheetTable.item(selected_row, 3).text() if self.parent.paytimesheetTable.item(
                    selected_row, 3) else "",
                2: self.parent.paytimesheetTable.item(selected_row, 4).text() if self.parent.paytimesheetTable.item(
                    selected_row, 4) else "",
                3: self.parent.paytimesheetTable.item(selected_row, 5).text() if self.parent.paytimesheetTable.item(
                    selected_row, 5) else "",
                4: self.parent.paytimesheetTable.item(selected_row, 6).text() if self.parent.paytimesheetTable.item(
                    selected_row, 6) else "",
                5: self.parent.paytimesheetTable.item(selected_row, 7).text() if self.parent.paytimesheetTable.item(
                    selected_row, 7) else "",
                6: self.parent.paytimesheetTable.item(selected_row, 8).text() if self.parent.paytimesheetTable.item(
                    selected_row, 8) else "",
                7: self.parent.paytimesheetTable.item(selected_row, 9).text() if self.parent.paytimesheetTable.item(
                    selected_row, 9) else "",
                8: self.parent.paytimesheetTable.item(selected_row, 10).text() if self.parent.paytimesheetTable.item(
                    selected_row, 10) else "",
                9: self.parent.paytimesheetTable.item(selected_row, 11).text() if self.parent.paytimesheetTable.item(
                    selected_row, 11) else "",
                10: self.parent.paytimesheetTable.item(selected_row, 12).text() if self.parent.paytimesheetTable.item(
                    selected_row, 12) else "",
                11: self.parent.paytimesheetTable.item(selected_row, 13).text() if self.parent.paytimesheetTable.item(
                    selected_row, 13) else "",
                12: self.parent.paytimesheetTable.item(selected_row, 14).text() if self.parent.paytimesheetTable.item(
                    selected_row, 14) else "",
                13: self.parent.paytimesheetTable.item(selected_row, 15).text() if self.parent.paytimesheetTable.item(
                    selected_row, 15) else "",
                14: self.parent.paytimesheetTable.item(selected_row, 16).text() if self.parent.paytimesheetTable.item(
                    selected_row, 16) else ""
            }

            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\deduction.ui")
            self.deductionQDialog = QDialog()
            self.deductionQDialog.setFixedSize(780, 413)
            loadUi(ui_file, self.deductionQDialog)

            empNameTxt = self.deductionQDialog.findChild(QLabel, 'empNameTxt')
            bioNumTxt = self.deductionQDialog.findChild(QLabel, 'bioNumTxt')

            if empNameTxt:
                empNameTxt.setText(emp_name_item.text() if emp_name_item else "")
            if bioNumTxt:
                bioNumTxt.setText(bio_num_item.text() if bio_num_item else "")

            # Set the deduction values to the input fields
            for i in range(1, 15):
                field = self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}')
                if field:
                    field.setText(deduction_values_mapping[i])

            # Now apply the integer validator to the deduction fields
            validator = ValidInteger()
            ded_fields = [self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}') for i in range(1, 15)]
            validator.set_validators(*ded_fields)

            # Connect the placeBTN if exists
            self.placeBTN = self.deductionQDialog.findChild(QPushButton, 'placeBTN')
            if self.placeBTN:
                self.placeBTN.clicked.connect(lambda: self.placeDeductions(self.deductionQDialog))
            else:
                logging.error("Error: placeBTN QPushButton not found in the deduction UI.")

            self.deductionQDialog.show()
            logging.info("Deduction UI loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self.parent, "UI Load Error", f"Failed to load deduction UI: {e}")

    def placeDeductions(self, dialog):
        try:
            selected_row = self.parent.paytimesheetTable.currentRow()
            if selected_row == -1:
                logging.warning("No row selected.")
                QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
                return

            deductions_mapping = {
                1: 'Late/Absent',
                2: 'SSS_Loan',
                3: 'Pag_Ibig_Loan',
                4: 'Cash_Advance',
                5: 'Canteen',
                6: 'Tax',
                7: 'SSS',
                8: 'Medicare/PhilHealth',
                9: 'PAGIBIG',
                10: 'Clinic',
                11: 'Arayata_Annual',
                12: 'HMI',
                13: 'Funeral',
                14: 'Voluntary'
            }

            for i in range(1, 15):
                deduction_field = self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}')

                if deduction_field and deduction_field.text().isdigit():
                    deduction_value = deduction_field.text()
                    deduction_column = self.getColumnIndex(deductions_mapping[i])

                    if deduction_column is not None:
                        item = QTableWidgetItem(deduction_value)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.parent.paytimesheetTable.setItem(selected_row, deduction_column, item)
                        logging.info(
                            f"Updated deduction {deductions_mapping[i]} for row {selected_row} with value {deduction_value}")
                    else:
                        logging.warning(f"Column for {deductions_mapping[i]} not found in the table.")

            QMessageBox.information(dialog, "Added Successfully", "Deduction/s was added successfully")
        except Exception as e:
            QMessageBox.critical(self.parent, "Deductions Error", f"Failed to place deductions: {e}")

    def get_deduction_table_data(self):
        deduction_data = []

        row_count = self.parent.paytimesheetTable.rowCount()
        column_count = self.parent.paytimesheetTable.columnCount()

        deductions_column_mapping = {
            1: 'Late/Absent',
            2: 'SSS_Loan',
            3: 'Pag_Ibig_Loan',
            4: 'Cash_Advance',
            5: 'Canteen',
            6: 'Tax',
            7: 'SSS',
            8: 'Medicare/PhilHealth',
            9: 'PAGIBIG',
            10: 'Clinic',
            11: 'Arayata_Annual',
            12: 'HMI',
            13: 'Funeral',
            14: 'Voluntary'
        }

        for row_index in range(row_count):
            row_data = {}

            for column_index in range(column_count):
                column_name = self.parent.paytimesheetTable.horizontalHeaderItem(column_index).text()
                cell_item = self.parent.paytimesheetTable.item(row_index, column_index)
                cell_data = cell_item.text() if cell_item else None

                if column_name in deductions_column_mapping.values():
                    row_data[column_name] = int(cell_data) if cell_data else 0
                else:
                    row_data[column_name] = cell_data

            deduction_data.append(row_data)

        return deduction_data

    def showStoreDeductionLoader(self):
        message = QMessageBox.question(self.parent, "Storing Deduction into Database",
                                       "Are you sure you want to store all the data into database "
                                       "even though not all data has deductions?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.deduction_data = self.get_deduction_table_data()
            self.storeDeductionLoader = StoreDeductionLoader(self.deduction_data, self.parent)
            self.storeDeductionLoader.show()

    def getColumnIndex(self, column_name):
        header_items = [self.parent.paytimesheetTable.horizontalHeaderItem(i).text()
                        for i in range(self.parent.paytimesheetTable.columnCount())]
        if column_name in header_items:
            return header_items.index(column_name)
        return -1

    def getBioNum(self, row):
        bio_num_item = self.parent.paytimesheetTable.item(row, 1)
        return bio_num_item.text() if bio_num_item else "Unknown"

    def exportDeductionToExcel(self):
        connection = create_connection('NTP_STORED_DEDUCTIONS')
        if connection is None:
            QMessageBox.critical(self.parent, "Connection Error",
                                 "Failed to connect to SYSTEM_STORE_DEDUCTION database.")
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
            file_name, _ = QFileDialog.getSaveFileName(self.parent, "Save File", "",
                                                       "Excel Files (*.xlsx);;All Files (*)")
            if file_name:
                # Ensure the file has the correct extension
                if not file_name.endswith('.xlsx'):
                    file_name += '.xlsx'

                # Save the workbook
                wb.save(file_name)
                QMessageBox.information(self.parent, "Export Successful",
                                        f"Deductions Data was exported successfully to {file_name}!")
                print(f"Data exported successfully to {file_name}")

        except Exception as e:
            print(f"Error fetching or processing deduction data: {e}")
            QMessageBox.critical(self.parent, "Export Failed", f"Failed to export deductions data: {e}")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def buttonImport(self):
        fileName, _ = QFileDialog.getOpenFileName(self.parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")
        if not fileName:
            return

        # Load the showNotification.ui
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        self.import_dialog = QDialog(self.parent)
        loadUi(ui_file, self.import_dialog)

        # Set up and start the file processing
        self.thread = QThread()
        self.file_processor = FileProcessor(fileName)
        self.file_processor.moveToThread(self.thread)
        self.file_processor.progressChanged.connect(self.updateProgressBar)
        self.file_processor.finished.connect(self.importFinished)
        self.file_processor.error.connect(self.importError)
        self.thread.started.connect(self.file_processor.process)

        self.import_dialog.show()
        self.thread.start()

    def updateProgressBar(self, value):
        if self.import_dialog:
            self.import_dialog.progressBar.setValue(value)
            QApplication.processEvents()

    def importFinished(self, content):
        self.thread.quit()
        self.thread.wait()
        if self.import_dialog:
            self.import_dialog.close()

        if content:
            # Update the paytimesheetTable with the new data
            self.populatePaytimeSheetTable(content)
            QMessageBox.information(self.parent, "Import Successful", "Data imported successfully!")
        else:
            QMessageBox.warning(self.parent, "Import Failed", "No data was imported.")

    def importError(self, error_message):
        self.thread.quit()
        self.thread.wait()
        if self.import_dialog:
            self.import_dialog.close()
        QMessageBox.critical(self.parent, "Import Error", f"An error occurred during import:\n{error_message}")
