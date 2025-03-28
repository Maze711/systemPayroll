from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SingleFunctionLogger:
    pass

#     def __init__(self, log_file='file_import.log'):
#         self.log_file = log_file
#         self.logger = logging.getLogger('SingleFunctionLogger')
#         self.logger.setLevel(logging.DEBUG)  # Capture all log levels
#         self.file_handler = None
#         self._setup_logger()
#
#     def _setup_logger(self):
#         if self.file_handler:
#             self.logger.removeHandler(self.file_handler)
#
#         # Overwrite the log file each time a new function is logged
#         self.file_handler = logging.FileHandler(self.log_file, mode='w')
#         formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#         self.file_handler.setFormatter(formatter)
#         self.logger.addHandler(self.file_handler)
#
#         # Remove all other handlers to prevent double logging
#         for handler in self.logger.handlers[:]:
#             if handler != self.file_handler:
#                 self.logger.removeHandler(handler)
#
#     def log_function(self, func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             self._setup_logger()
#             start_time = time.time()
#             self.logger.info(f"Starting execution of function: {func.__name__}")
#             try:
#                 result = func(*args, **kwargs)
#                 end_time = time.time()
#                 duration = end_time - start_time
#                 self.logger.info(f"Function {func.__name__} completed successfully in {duration:.2f} seconds")
#                 return result
#             except Exception as e:
#                 end_time = time.time()
#                 duration = end_time - start_time
#                 error_message = f"Error in function {func.__name__}: {str(e)} (Execution time: {duration:.2f} seconds)"
#                 self.logger.exception(error_message)  # logs the full traceback
#                 raise
#
#         return wrapper
#
# # Modify the root logger to use this file handler as well
# root_logger = logging.getLogger()
# root_logger.setLevel(logging.DEBUG)
# root_logger.addHandler(SingleFunctionLogger().file_handler)

single_function_logger = SingleFunctionLogger()


class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        self.column_mapping = {
            'Bio_No.': ['Bio_No.'],
            'Emp_Number': ['Emp_Number'],
            'Emp_Name': ['Emp_Name'],
            'Cost_Center': ['Cost_Center'],
            'Days_Work': ['Days_Work'],
            'Days_Present': ['Days_Present'],
            'Hours_Work': ['Hours_Work'],
            'Late': ['Late'],
            'Undertime': ['Undertime'],
            'OrdDay_Hrs': ['OrdDay_Hrs'],
            'OrdDayOT_Hrs': ['OrdDayOT_Hrs'],
            'OrdDayND_Hrs': ['OrdDayND_Hrs'],
            'OrdDayNDOT_Hrs': ['OrdDayNDOT_Hrs'],
            'RstDay_Hrs': ['RstDay_Hrs'],
            'RstDayOT_Hrs': ['RstDayOT_Hrs'],
            'RstDayND_Hrs': ['RstDayND_Hrs'],
            'RstDayNDOT_Hrs': ['RstDayNDOT_Hrs'],
            'SplHlyday_Hrs': ['SplHlyday_Hrs'],
            'SplHlydayOT_Hrs': ['SplHlydayOT_Hrs'],
            'SplHlydayND_Hrs': ['SplHlydayND_Hrs'],
            'SplHlydayNDOT_Hrs': ['SplHlydayNDOT_Hrs'],
            'RegHlyday_Hrs': ['RegHlyday_Hrs'],
            'RegHlydayOT_Hrs': ['RegHlydayOT_Hrs'],
            'RegHlydayND_Hrs': ['RegHlydayND_Hrs'],
            'RegHlydayNDOT_Hrs': ['RegHlydayNDOT_Hrs'],
            'SplHldyRD_Hrs': ['SplHldyRD_Hrs'],
            'SplHldyRDOT_Hrs': ['SplHldyRDOT_Hrs'],
            'SplHldyRDND_Hrs': ['SplHldyRDND_Hrs'],
            'SplHldyRDNDOT_Hrs': ['SplHldyRDNDOT_Hrs'],
            'RegHldyRD_Hrs': ['RegHldyRD_Hrs'],
            'RegHldyRDOT_Hrs': ['RegHldyRDOT_Hrs'],
            'RegHldyRDND_Hrs': ['RegHldyRDND_Hrs'],
            'RegHldyRDNDOT_Hrs': ['RegHldyRDNDOT_Hrs'],
        }
        self.required_columns = list(self.column_mapping.keys())

    def process(self):
        try:
            content = []
            file_ext = self.fileName.lower()

            if file_ext.endswith('.xlsx'):
                workbook = openpyxl.load_workbook(self.fileName, data_only=True)
                sheet = workbook.active
                headers = [cell.value for cell in sheet[1]]  # Read headers
                total_rows = sheet.max_row

                # Include headers and data
                for row_idx in range(1, total_rows + 1):  # Start from 1 to include header
                    row = [sheet.cell(row=row_idx, column=col_idx).value for col_idx in range(1, sheet.max_column + 1)]
                    content.append(row)
                    progress = int((row_idx / total_rows) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)  # Simulate work being done

            elif file_ext.endswith('.xls'):
                workbook = xlrd.open_workbook(self.fileName, encoding_override="cp1252")
                sheet = workbook.sheet_by_index(0)
                headers = sheet.row_values(0)  # Read headers
                total_rows = sheet.nrows

                # Include headers and data
                for row_idx in range(total_rows):  # Start from 0 to include header
                    row = sheet.row_values(row_idx)
                    content.append(row)
                    progress = int((row_idx / total_rows) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)  # Simulate work being done
            else:
                raise ValueError(f"Unsupported file format: {file_ext.split('.')[-1]}")

            # Validate required columns directly from headers
            missing_columns = [col for col in self.required_columns if col not in headers]

            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            self.finished.emit(content)

        except ValueError as ve:
            self.error.emit(str(ve))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")

    def standardize_headers(self, headers):
        standardized = []
        for header in headers:
            header_lower = header.strip().lower() if header else ''
            for std_name, variations in self.column_mapping.items():
                if header_lower in variations:
                    standardized.append(std_name)
                    break
            else:
                standardized.append(header_lower)  # Keep original if no match found
        return standardized


class globalFunction():
    def __init__(self):
        super(globalFunction, self).__init__()

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def export_to_excel(data, file_name):
        try:
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError("Data should be a list of dictionaries or a DataFrame")

            df.to_excel(file_name, index=False, engine='openpyxl')
            QMessageBox.information(None, "Success", f"Data successfully exported to {file_name}")

        except Exception as e:
            QMessageBox.critical(None, "Export Failed",
                                 f"Failed to export data to Excel: {str(e)}. Please try again or check your data.")
            raise


class DatabaseConnectionError(Exception):
    """Custom Exception Handler for Database Connection Errors"""
    pass


class timekeepingFunction():
    def __init__(self):
        super(timekeepingFunction, self).__init__()

    def getTypeOfDate(trans_date):
        try:
            connection = create_connection('NTP_HOLIDAY_LIST')
            if connection is None:
                return "Ordinary Day"  # Return default value on connection failure

            cursor = connection.cursor()

            fetch_type_of_date = "SELECT dateType FROM type_of_dates WHERE date = %s"
            cursor.execute(fetch_type_of_date, (trans_date,))

            result = cursor.fetchone()
            if result:
                return result[0]  # Return the dateType if found

            return "Ordinary Day"  # Default to Ordinary Day if no match found

        except Error as e:
            return "Ordinary Day"  # Return default value on error

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def appendDate(fromCalendar, toCalendar, data):
        from_date = fromCalendar.date().toString("yyyy-MM-dd")
        to_date = toCalendar.date().toString("yyyy-MM-dd")

        filtered_data = [
            row for row in data
            if from_date <= row['trans_date'] <= to_date
        ]
        return filtered_data, from_date, to_date

    @staticmethod
    def searchBioNumFunction(instance):
        try:
            search_text = instance.searchBioNum.text().strip().lower()
            logging.info(f"Search text: '{search_text}'")

            # Restore original data if no search term is provided
            if not search_text:
                if hasattr(instance, 'original_data'):
                    if hasattr(instance, 'paytimesheetTable'):
                        instance.populatePaytimeSheetTable(instance.original_data)
                    elif hasattr(instance, 'paytransTable'):
                        instance.populatePayTransTable(instance.original_data)
                    elif hasattr(instance, 'bankregisterTable'):
                        instance.functions.populateBankRegisterTable(instance.original_data)
                    elif hasattr(instance, 'timeListTable'):
                        instance.populateTimeList(instance.original_data)
                else:
                    if hasattr(instance, 'TimeSheetTable'):
                        instance.populateTimeSheet(instance.data)
                return

            # Clear the table before populating it with filtered data
            if hasattr(instance, 'TimeSheetTable'):
                instance.TimeSheetTable.clearContents()

            # Search logic for PaytimeSheet, PayTrans, BankRegister, TimeSheet, or TimeList
            if hasattr(instance, 'paytimesheetTable'):
                for row in range(instance.paytimesheetTable.rowCount()):
                    item = instance.paytimesheetTable.item(row, 1)  # Bio Num column at index 1
                    if item and search_text in item.text().lower():
                        instance.paytimesheetTable.setRowHidden(row, False)
                    else:
                        instance.paytimesheetTable.setRowHidden(row, True)
            elif hasattr(instance, 'paytransTable'):
                for row in range(instance.paytransTable.rowCount()):
                    item = instance.paytransTable.item(row, 1)  # Bio Num column at index 1
                    if item and search_text in item.text().lower():
                        instance.paytransTable.setRowHidden(row, False)
                    else:
                        instance.paytransTable.setRowHidden(row, True)
            elif hasattr(instance, 'bankregisterTable'):
                for row in range(instance.bankregisterTable.rowCount()):
                    item = instance.bankregisterTable.item(row, 1)  # Bio Num column at index 1
                    if item and search_text in item.text().lower():
                        instance.bankregisterTable.setRowHidden(row, False)
                    else:
                        instance.bankregisterTable.setRowHidden(row, True)
            elif hasattr(instance, 'filtered_data'):
                filtered_data = [row for row in instance.filtered_data if row['BioNum'].startswith(search_text)]
                if hasattr(instance, 'populateTimeSheet'):
                    instance.populateTimeSheet(filtered_data)
                elif hasattr(instance, 'populateTimeList'):
                    instance.populateTimeList(filtered_data)
                elif hasattr(instance, 'populatePaytimeSheetTable'):
                    instance.populatePaytimeSheetTable(filtered_data)
                elif hasattr(instance, 'populatePayTransTable'):
                    instance.populatePayTransTable(filtered_data)

            elif hasattr(instance, 'data'):
                # Filter data based on BioNum for TimeSheet
                filtered_data = [row for row in instance.data if search_text in row['BioNum'].lower()]
                if hasattr(instance, 'populateTimeSheet'):
                    instance.populateTimeSheet(filtered_data)
        except Exception as e:
            print('Error searching bio num: ', e)


class ValidInteger:
    def __init__(self):
        self.int_validator = QIntValidator()

    def set_validators(self, *text_fields):
        """Sets integer validators for provided text fields."""
        for field in text_fields:
            field.setValidator(self.int_validator)