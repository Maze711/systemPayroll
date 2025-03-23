import logging
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem, QApplication, QDialog
from PyQt5.QtCore import QThread, Qt
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, FileProcessor
from MainFrame.Payroll.payTrans.payTransLoader import PayTrans
from MainFrame.Payroll.payroll_functions.payComputations import PayComputation
from MainFrame.Payroll.paymaster_Employee.payaddEmployee import payAddEmployee

# Configure logging
logging.basicConfig(filename='paytimeSheet.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PaytimeSheetFunctions:
    def __init__(self, parent):
        self.parent = parent

    def readRatesFromExcel(self, file_path):
        bio_num_to_rate = {}

        try:
            workbook = xlrd.open_workbook(file_path, encoding_override='latin-1')
            sheet = workbook.sheet_by_index(0)  # Use the first sheet

            headers = [sheet.cell_value(0, col_idx).strip().lower() for col_idx in range(sheet.ncols)]
            empl_id_index = headers.index('empl_id') if 'empl_id' in headers else None
            rate_index = headers.index('rate') if 'rate' in headers else None

            if empl_id_index is None or rate_index is None:
                logging.error("Required columns 'empl_id' or 'rate' not found in the Excel file.")
                return bio_num_to_rate

            for row_idx in range(1, sheet.nrows):  # Skip the header row
                empl_id_value = str(sheet.cell_value(row_idx, empl_id_index))
                rate_value = str(sheet.cell_value(row_idx, rate_index))

                # Remove trailing '.0' from empl_id_value, if present
                if empl_id_value.endswith('.0'):
                    empl_id_value = empl_id_value[:-2]

                bio_num_to_rate[empl_id_value] = rate_value

            logging.info(f"Processed {sheet.nrows - 1} rows from Excel file.")

        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            QMessageBox.critical(self.parent, "Error Reading File", f"Error reading Excel file: {e}")

        return bio_num_to_rate

    def createPayTrans(self, checked=False):
        try:
            from_date = self.parent.lblFrom.text()
            to_date = self.parent.lblTo.text()

            print(f"Creating PayTrans from {from_date} to {to_date}")

            # Collect selected data from the table
            selected_data = []

            for row in range(self.parent.paytimesheetTable.rowCount()):
                try:
                    bio_num_item = self.parent.paytimesheetTable.item(row, 0)
                    emp_no_item = self.parent.paytimesheetTable.item(row, 1)
                    emp_name_item = self.parent.paytimesheetTable.item(row, 2)
                    present_days_item = self.parent.paytimesheetTable.item(row, 5)

                    late_item = self.parent.paytimesheetTable.item(row, 7)
                    undertime_item = self.parent.paytimesheetTable.item(row, 8)

                    ord_day_item = self.parent.paytimesheetTable.item(row, 9)
                    ord_day_ot_item = self.parent.paytimesheetTable.item(row, 10)
                    ord_day_nd_item = self.parent.paytimesheetTable.item(row, 11)
                    ord_day_ndot_item = self.parent.paytimesheetTable.item(row, 12)

                    rest_day_item = self.parent.paytimesheetTable.item(row, 13)
                    rest_day_ot_item = self.parent.paytimesheetTable.item(row, 14)
                    rest_day_nd_item = self.parent.paytimesheetTable.item(row, 15)
                    rest_day_ndot_item = self.parent.paytimesheetTable.item(row, 16)

                    #SplHlyday_hrs list might be added right here

                    reg_hldy_item = self.parent.paytimesheetTable.item(row, 21)
                    reg_hldy_ot_item = self.parent.paytimesheetTable.item(row, 22)
                    reg_hldy_nd_item = self.parent.paytimesheetTable.item(row, 23)
                    reg_hldy_ndot_item = self.parent.paytimesheetTable.item(row, 24)

                    #SplHldyRD_hrs list might be added right here

                    rest_holi_item = self.parent.paytimesheetTable.item(row, 29)
                    rest_holi_ot_item = self.parent.paytimesheetTable.item(row, 30)
                    rest_holi_nd_item = self.parent.paytimesheetTable.item(row, 31)
                    rest_holi_ndot_item = self.parent.paytimesheetTable.item(row, 32)

                    # absent_item = self.parent.paytimesheetTable.item(row, 33)

                    # Check for None values
                    if bio_num_item is None or emp_no_item is None or emp_name_item is None:
                        logging.warning(
                            f"Row {row}: Missing essential items (Bio_No, Emp_Number, or Emp_Name). Skipping this row.")
                        continue

                    bio_num = bio_num_item.text()[3:] if bio_num_item and bio_num_item.text() else ""

                    # Print the collected data for debugging
                    print(
                        f"Row {row}: BioNum={bio_num}, Emp_Number={emp_no_item.text()}, EmpName={emp_name_item.text()}")

                    # Ensure numeric fields are not None before converting to float
                    def safe_float(value):
                        if value is None:
                            return 0.0
                        return float(value.strip()) if value else 0.0

                    selected_data.append({
                        'EmpNo': emp_no_item.text(),
                        'BioNum': bio_num,
                        'EmpName': emp_name_item.text(),
                        'Present Days': safe_float(present_days_item.text()),
                        
                        'Ordinary Day Hours': safe_float(ord_day_item.text()),
                        'Ordinary Day OT Hours': safe_float(ord_day_ot_item.text()),
                        'Ordinary Day Night Diff Hours': safe_float(ord_day_nd_item.text()),
                        'Ordinary Day NDOT Hours': safe_float(ord_day_ndot_item.text()),
                        
                        'Rest Day Hours': safe_float(rest_day_item.text()),
                        'Rest Day OT Hours': safe_float(rest_day_ot_item.text()),
                        'Rest Day Night Diff Hours': safe_float(rest_day_nd_item.text()),
                        'Rest Day Night Diff OT': safe_float(rest_day_ndot_item.text()),

                        'Regular Holiday Hours': safe_float(reg_hldy_item.text()),
                        'Regular Holiday OT Hours': safe_float(reg_hldy_ot_item.text()),
                        'Regular Holiday Night Diff Hours': safe_float(reg_hldy_nd_item.text()),
                        'Regular Holiday Night Diff OT Hours': safe_float(reg_hldy_ndot_item.text()),

                        'Rest Holiday Hours': safe_float(rest_holi_item.text()),
                        'Rest Holiday OT Hours': safe_float(rest_holi_ot_item.text()),
                        'Rest Holiday Night Diff Hours': safe_float(rest_holi_nd_item.text()),
                        'Rest Holiday Night Diff OT Hours': safe_float(rest_holi_ndot_item.text()),

                        'Late': safe_float(late_item.text()),
                        'Undertime': safe_float(undertime_item.text()),

                        # 'Absent': safe_float(absent_item.text())
                    })

                except Exception as e:
                    logging.error(f"Error processing row {row}: {e}")

            print(f"Selected data length: {len(selected_data)}")

            bio_num_to_rate = self.readRatesFromExcel('MainFrame\\Files Testers\\file201.xls')

            print("Rates read from Excel.")

            # Update selected_data with rate
            for item in selected_data:
                item['Rate'] = bio_num_to_rate.get(item['BioNum'], "Missing")

            print("Rates updated in selected data.")

            # Perform automated calculations
            pay_computation = PayComputation(selected_data)
            print("Starting pay computation...")

            pay_computation.basicComputation()
            pay_computation.regularDayEarnComputation()
            pay_computation.overtimeComputation()
            pay_computation.regularDayNightDiffComputation()
            pay_computation.regularDayNightDiffOTComputation()
            pay_computation.lateComputation()
            pay_computation.undertimeComputation()
            pay_computation.restDayComputation()
            pay_computation.regularHolidayComputation()
            pay_computation.restDayOTComputation()
            pay_computation.regularHolidayOTComputation()
            pay_computation.restDayNightDiffComputation()
            pay_computation.regularHolidayNightDiffComputation()
            pay_computation.restDayNightDiffOTComputation()
            pay_computation.regularHolidayNightDiffOTComputation()
            pay_computation.restDayHolidayComputation()
            pay_computation.restDayHolidayOTComputation()
            pay_computation.restDayHolidayNDComputation()
            pay_computation.restDayHolidayNDOTComputation()

            pay_computation.calculateGrossIncome()
            print("Pay computation completed.")

            print("Selected Data: ", selected_data[0])

            try:

                # If there's no selected data to be inserted, throw an error
                if len(selected_data) == 0:
                    QMessageBox.warning(self.parent, "Error",
                                        "Please import the timesheet first, before creating Paytrans.")
                    return

                self.parent.window = PayTrans(from_date, to_date, selected_data)
                self.parent.main_window.open_dialogs.append(self.parent.window)
                self.parent.window.show()
                self.parent.close()
            except Exception as e:
                logging.error(f"Failed to create PayTrans window: {e}")
                QMessageBox.critical(self.parent, "Error", f"Failed to create PayTrans window: {e}")

        except Exception as e:
            logging.error(f"Error in createPayTrans: {e}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred: {e}")

    def showNewListEmployee(self):
        try:
            payAddEmployee_dialog = payAddEmployee()
            payAddEmployee_dialog.exec_()
        except Exception as e:
            logging.error(f"Error in showNewListEmployee: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to show employee list: {e}")

    def buttonImport(self):
        try:
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

        except Exception as e:
            logging.error(f"Error in buttonImport: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to import file: {e}")

    def updateProgressBar(self, value):
        try:
            if self.import_dialog:
                self.import_dialog.progressBar.setValue(value)
                QApplication.processEvents()
        except Exception as e:
            logging.error(f"Error in updateProgressBar: {e}")

    def importFinished(self, content):
        try:
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
        except Exception as e:
            logging.error(f"Error in importFinished: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to finish import: {e}")

    def importError(self, error_message):
        try:
            self.thread.quit()
            self.thread.wait()
            if self.import_dialog:
                self.import_dialog.close()
            QMessageBox.critical(self.parent, "Import Error", f"An error occurred during import:\n{error_message}")
        except Exception as e:
            logging.error(f"Error in importError: {e}")

    def populatePaytimeSheetTable(self, data):
        try:
            # Ensure data is not empty and contains at least a header and one row of data
            if not data or len(data) < 2:
                logging.error("No data or insufficient data to populate the table.")
                QMessageBox.critical(self.parent, "Error", "No data available to populate the table.")
                return

            # Define column names in the Excel file
            column_names = {
                'Bio_No.': ('Bio_No.', 0),
                'Emp_Number': ('Emp_Number', 1),
                'Emp_Name': ('Emp_Name', 2),
                'Cost_Center': ('Cost_Center', 3),
                'Days_Work': ('Days_Work', 4),
                'Days_Present': ('Days_Present', 5),
                'Hours_Work': ('Hours_Work', 6),
                'Late': ('Late', 7),
                'Undertime': ('Undertime', 8),
                'OrdDay_Hrs': ('OrdDay_Hrs', 9),
                'OrdDayOT_Hrs': ('OrdDayOT_Hrs', 10),
                'OrdDayND_Hrs': ('OrdDayND_Hrs', 11),
                'OrdDayNDOT_Hrs': ('OrdDayNDOT_Hrs', 12),
                'RstDay_Hrs': ('RstDay_Hrs', 13),
                'RstDayOT_Hrs': ('RstDayOT_Hrs', 14),
                'RstDayND_Hrs': ('RstDayND_Hrs', 15),
                'RstDayNDOT_Hrs': ('RstDayNDOT_Hrs', 16),
                'RegHlyday_Hrs': ('RegHlyday_Hrs', 17),
                'RegHlydayOT_Hrs': ('RegHlydayOT_Hrs', 18),
                'RegHlydayND_Hrs': ('RegHlydayND_Hrs', 19),
                'RegHlydayNDOT_Hrs': ('RegHlydayNDOT_Hrs', 20),
                'RegHldyRD_Hrs': ('RegHldyRD_Hrs', 21),
                'RegHldyRDOT_Hrs': ('RegHldyRDOT_Hrs', 28),
                'RegHldyRDND_Hrs': ('RegHldyRDND_Hrs', 29),
                'RegHldyRDNDOT_Hrs': ('RegHldyRDNDOT_Hrs', 30),
                'SplHlyday_Hrs': ('SplHlyday_Hrs', 31),
                'SplHlydayOT_Hrs': ('SplHlydayOT_Hrs', 32),
                'SplHlydayND_Hrs': ('SplHlydayND_Hrs', 33),
                'SplHlydayNDOT_Hrs': ('SplHlydayNDOT_Hrs', 34)
            }

            # Extract the header row
            headers = data[0]
            col_indices = {}
            for name, (xls_col_name, widget_col_idx) in column_names.items():
                if xls_col_name in headers:
                    col_indices[name] = headers.index(xls_col_name)

            # Check for missing columns
            if len(col_indices) < len(column_names):
                logging.error("No matching columns found in headers.")
                QMessageBox.critical(self.parent, "Error", "No matching columns found in headers.")
                return

            # Set the row count based on the number of data rows (excluding header)
            row_data = data[1:]  # Remaining rows with actual data
            self.parent.paytimesheetTable.setRowCount(len(row_data))

            # Populate the table with data
            for row_index, row in enumerate(row_data):
                for col_name, col_index in col_indices.items():
                    # Ensure the column index is valid
                    if col_index < len(row):
                        value = row[col_index]
                        item = QTableWidgetItem(str(value) if value is not None else 'unknown')
                        item.setTextAlignment(Qt.AlignCenter)

                        self.parent.paytimesheetTable.setItem(row_index, col_indices[col_name], item)
                    else:
                        # Handle cases where the data row may have fewer columns than expected
                        self.parent.paytimesheetTable.setItem(row_index, col_indices[col_name], QTableWidgetItem('unknown'))

        except Exception as e:
            logging.error(f"Error in populatePaytimeSheetTable: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to populate table: {e}")

    def filterTable(self):
        try:
            search_text = self.parent.searchBioNum.text().strip().lower()

            for row in range(self.parent.paytimesheetTable.rowCount()):
                item = self.parent.paytimesheetTable.item(row, 1)  # Bio Num column at index 1
                if item and search_text in item.text().lower():
                    self.parent.paytimesheetTable.showRow(row)
                else:
                    self.parent.paytimesheetTable.hideRow(row)
        except Exception as e:
            logging.error(f"Error in filterTable: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to filter table: {e}")