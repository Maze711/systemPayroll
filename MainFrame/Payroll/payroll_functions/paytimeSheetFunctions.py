import sys
import os

from MainFrame.systemFunctions import globalFunction, FileProcessor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.Payroll.payTrans.payTransLoader import PayTrans
from MainFrame.Payroll.payroll_functions.payComputations import PayComputation
from MainFrame.Payroll.paymaster_Employee.payaddEmployee import payAddEmployee

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
            QMessageBox.critical(self.parent, "Error Reading File", f"Error reading Excel file: {e}")
            print(f"Error reading Excel file: {e}")

        return bio_num_to_rate

    def createPayTrans(self, checked=False):
        from_date = self.parent.lblFrom.text()
        to_date = self.parent.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.parent.paytimesheetTable.rowCount()):
            emp_no_item = self.parent.paytimesheetTable.item(row, 0)
            bio_num_item = self.parent.paytimesheetTable.item(row, 1)
            emp_name_item = self.parent.paytimesheetTable.item(row, 2)
            present_days_item = self.parent.paytimesheetTable.item(row, 5)
            rest_day_item = self.parent.paytimesheetTable.item(row, 6)
            holiday_item = self.parent.paytimesheetTable.item(row, 7)
            restholiday_item = self.parent.paytimesheetTable.item(row, 8)
            reg_day_night_diff_item = self.parent.paytimesheetTable.item(row, 9)
            reg_day_night_diff_ot_item = self.parent.paytimesheetTable.item(row, 10)
            rest_day_night_item = self.parent.paytimesheetTable.item(row, 11)
            holiday_night_item = self.parent.paytimesheetTable.item(row, 12)
            rest_holiday_night_item = self.parent.paytimesheetTable.item(row, 13)
            ordinary_day_ot_item = self.parent.paytimesheetTable.item(row, 14)
            rest_day_ot_item = self.parent.paytimesheetTable.item(row, 15)
            holiday_ot_item = self.parent.paytimesheetTable.item(row, 16)
            restholiday_ot_item = self.parent.paytimesheetTable.item(row, 17)
            late_item = self.parent.paytimesheetTable.item(row, 18)
            undertime_item = self.parent.paytimesheetTable.item(row, 19)

            if bio_num_item and bio_num_item.text():
                bio_num = bio_num_item.text()[3:]
            else:
                bio_num = ""

            selected_data.append({
                'EmpNo': emp_no_item.text(),
                'BioNum': bio_num,
                'EmpName': emp_name_item.text(),
                'Present Days': present_days_item.text(),
                'Rest Day Hours': rest_day_item.text(),
                'Holiday Hours': holiday_item.text(),
                'Regular Day Night Diff': reg_day_night_diff_item.text(),
                'Regular Day Night Diff OT': reg_day_night_diff_ot_item.text(),
                'Rest Day Night Diff Hours': rest_day_night_item.text(),
                'Holiday Night Diff Hours': holiday_night_item.text(),
                'OrdinaryDayOT': ordinary_day_ot_item.text(),
                'Rest Day OT Hours': rest_day_ot_item.text(),
                'Holiday OT Hours': holiday_ot_item.text(),
                'Late': late_item.text(),
                'Undertime': undertime_item.text()
            })

        bio_num_to_rate = self.readRatesFromExcel('MainFrame\\Files Testers\\file201.xls')

        # Update selected_data with rate
        for item in selected_data:
            item['Rate'] = bio_num_to_rate.get(item['BioNum'], "Missing")

        # Perform automated calculations
        pay_computation = PayComputation(selected_data)
        pay_computation.basicComputation()
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

        print("Data with new computation: \n\t", selected_data)

        try:
            self.parent.window = PayTrans(from_date, to_date, selected_data)
            self.parent.main_window.open_dialogs.append(self.parent.window)
            self.parent.window.show()
            self.parent.close()
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to create PayTrans window: {e}")
            print(f"Failed to create PayTrans window: {e}")

    def showNewListEmployee(self):
        payAddEmployee_dialog = payAddEmployee()
        payAddEmployee_dialog.exec_()

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

    def populatePaytimeSheetTable(self, data):
        # Ensure data is not empty and contains at least a header and one row of data
        if not data or len(data) < 2:
            logging.error("No data or insufficient data to populate the table.")
            QMessageBox.critical(self.parent, "Error", "No data available to populate the table.")
            return

        # Define column names in the Excel file
        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'CostCenter': 'costcenter',
            'DaysWork': 'dayswork',
            'DaysPresent': 'daypresent',
            'RestDay': 'restday',
            'Holiday': 'holiday',
            'RestHoliday': 'rsthlyday',
            'OrdinaryDayNight': 'orddaynite',
            'OrdinaryDayNightOT': 'orddaynit2',
            'RestDayNight': 'rstdaynite',
            'HolidayNight': 'hlydaynite',
            'RestHolidayNight': 'rsthlydayn',
            'OrdinaryDayOT': 'orddayot',
            'RestDayOT': 'rstdayot',
            'HolidayOT': 'hlydayot',
            'RestHolidayOT': 'rsthlydayo',
            'Late': 'late',
            'Undertime': 'undertime',
            'Absent': 'absent',
            'DatePosted': 'dateposted',
            'Remarks': 'remarks',
            'EmpCompany': 'empcompany',
            'LegalHoliday': 'legalholid'
        }

        # Extract column indices from the header row
        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]  # Handle None values
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        # Exclude header row
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)

        try:
            for i, row in enumerate(data[1:]):  # Skip header row
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
                        logging.warning(f"Column '{field_name}' not found in data for row {i + 1}")
                logging.info(f"Added row {i + 1}: {row}")

            QMessageBox.information(self.parent, "Success", "Paytime sheet table populated successfully.")
        except Exception as e:
            logging.error(f"Error populating paytime sheet table: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to populate paytime sheet table: {e}")