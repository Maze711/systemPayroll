from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, FileProcessor
from MainFrame.Payroll.payTrans.payTransLoader import PayTrans
from MainFrame.Payroll.payroll_functions.payComputations import PayComputation
from MainFrame.Payroll.paymaster_Employee.payaddEmployee import payAddEmployee

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
            QMessageBox.critical(self.parent, "Error Reading File", f"Error reading Excel file: {e}")
            print(f"Error reading Excel file: {e}")

        return bio_num_to_rate

    def createPayTrans(self, checked=False):
        from_date = self.parent.lblFrom.text()
        to_date = self.parent.lblTo.text()

        # Collect selected data from the table
        selected_data = []
        for row in range(self.parent.paytimesheetTable.rowCount()):
            bio_num_item = self.parent.paytimesheetTable.item(row, 0)
            emp_no_item = self.parent.paytimesheetTable.item(row, 1)
            emp_name_item = self.parent.paytimesheetTable.item(row, 2)
            present_days_item = self.parent.paytimesheetTable.item(row, 5)
            ordinary_day_ot_item = self.parent.paytimesheetTable.item(row, 8)
            reg_day_night_diff_item = self.parent.paytimesheetTable.item(row, 9)
            reg_day_night_diff_ot_item = self.parent.paytimesheetTable.item(row, 10)
            rest_day_item = self.parent.paytimesheetTable.item(row, 11)
            rest_day_ot_item = self.parent.paytimesheetTable.item(row, 12)
            rest_day_night_item = self.parent.paytimesheetTable.item(row, 13)
            rest_day_night_diff_ot_item = self.parent.paytimesheetTable.item(row, 14)
            holiday_item = self.parent.paytimesheetTable.item(row, 19)
            holiday_ot_item = self.parent.paytimesheetTable.item(row, 20)
            holiday_night_item = self.parent.paytimesheetTable.item(row, 21)
            holiday_night_ot_item = self.parent.paytimesheetTable.item(row, 22)
            rest_holiday_item = self.parent.paytimesheetTable.item(row, 27)
            rest_holiday_ot_item = self.parent.paytimesheetTable.item(row, 28)
            rest_holiday_night_item = self.parent.paytimesheetTable.item(row, 29)
            rest_holiday_night_diff_ot_item = self.parent.paytimesheetTable.item(row, 30)
            late_item = self.parent.paytimesheetTable.item(row, 31)
            undertime_item = self.parent.paytimesheetTable.item(row, 32)

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
                'Rest Holiday Hours': rest_holiday_item.text(),
                'Regular Day Night Diff': reg_day_night_diff_item.text(),
                'Rest Day Night Diff Hours': rest_day_night_item.text(),
                'Holiday Night Diff Hours': holiday_night_item.text(),
                'Rest Holiday Night Diff Hours': rest_holiday_night_item.text(),
                'OrdinaryDayOT': ordinary_day_ot_item.text(),
                'Rest Day OT Hours': rest_day_ot_item.text(),
                'Holiday OT Hours': holiday_ot_item.text(),
                'Rest Holiday OT Hours': rest_holiday_ot_item.text(),
                'Regular Day Night Diff OT': reg_day_night_diff_ot_item.text(),
                'Rest Day Night Diff OT': rest_day_night_diff_ot_item.text(),
                'Holiday Night Diff OT': holiday_night_ot_item.text(),
                'Rest Holiday Night Diff OT': rest_holiday_night_diff_ot_item.text(),
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
            'Bio_No.': ('empnumber', 0),
            'Emp_Num': ('empnumber', 1),
            'Emp_Name': ('empname', 2),
            'Cost_Center': ('costcenter', 3),
            'Days_Work': ('dayswork', 4),
            'Days_Present': ('daypresent', 5),
            'OrdDayOT_Hrs': ('orddayot', 8),
            'OrdDayND_Hrs': ('orddaynite', 9),
            'OrdDayNDOT_Hrs': ('orddaynit2', 10),
            'RstDay_Hrs': ('restday', 11),
            'RstDayOT_Hrs': ('rstdayot', 12),
            'RstDayND_Hrs': ('rstdaynite', 13),
            'RstDayNDOT_Hrs': ('rstdaynit2', 14),
            'RegHlyday_Hrs': ('holiday', 19),
            'RegHlydayOT_Hrs': ('hlydayot', 20),
            'RegHlydayND_Hrs': ('hlydaynite', 21),
            'RegHlydayNDOT_Hrs': ('hlydaynit2', 22),
            'RegHldyRD_Hrs': ('rsthlyday', 27),
            'RegHldyRDOT_Hrs': ('rsthlydayo', 28),
            'RegHldyRDND_Hrs': ('rsthlydayn', 29),
            'RegHldyRDNDOT_Hrs': ('rsthlyday2', 30),
            'Late': ('late', 31),
            'Undertime': ('undertime', 32),
            'Absent': ('absent', 33),
            'Date_Posted': ('dateposted', 34),
            'Remarks': ('remarks', 35),
            'Emp_Company': ('empcompany', 36),
            'Legal_Holiday': ('legalholid', 37)
        }

        # Extract column indices from the header row
        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]  # Handle None values
        col_indices = {name: headers.index(xls_col_name) for name, (xls_col_name, widget_col_idx)
                       in column_names.items() if xls_col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        # Exclude header row
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)

        try:
            for i, row in enumerate(data[1:]):  # Skip header row
                for field_name, (xls_col_name, widget_col_idx) in column_names.items():
                    col_idx = col_indices.get(field_name)
                    if col_idx is not None:
                        item = QTableWidgetItem(str(row[col_idx]))
                        if field_name in column_names:
                            item.setTextAlignment(Qt.AlignCenter)
                        if field_name == 'Emp_Name':
                            item.setToolTip(row[col_idx])
                        self.parent.paytimesheetTable.setItem(i, widget_col_idx, item)
                    else:
                        logging.warning(f"Column '{field_name}' not found in data for row {i + 1}")
                logging.info(f"Added row {i + 1}: {row}")

        except Exception as e:
            logging.error(f"Error populating paytime sheet table: {e}")
            QMessageBox.critical(self.parent, "Error", f"Failed to populate paytime sheet table: {e}")

    def filterTable(self):
        search_text = self.parent.searchBioNum.text().strip().lower()

        for row in range(self.parent.paytimesheetTable.rowCount()):
            item = self.parent.paytimesheetTable.item(row, 1)  # Bio Num column at index 1
            if item and search_text in item.text().lower():
                self.parent.paytimesheetTable.showRow(row)
            else:
                self.parent.paytimesheetTable.hideRow(row)