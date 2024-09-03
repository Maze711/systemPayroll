import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection


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


class globalFunction():
    def __init__(self):
        super(globalFunction, self).__init__()

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
            logging.info(f"Data successfully exported to {file_name}")
        except Exception as e:
            logging.error(f"Failed to export data to Excel: {e}")
            raise

class DatabaseConnectionError(Exception):
    """Custom Exception Handler for Database Connection Errors"""
    pass

class timekeepingFunction():
    def __init__(self):
        super(timekeepingFunction, self).__init__()

    def getTypeOfDate(trans_date):
        logger = logging.getLogger('SingleFunctionLogger')
        try:
            connection = create_connection('NTP_HOLIDAY_LIST')
            if connection is None:
                logger.error("Error: Could not establish database connection.")
                return "Ordinary Day"  # Return default value on connection failure

            cursor = connection.cursor()

            fetch_type_of_date = "SELECT dateType FROM type_of_dates WHERE date = %s"
            cursor.execute(fetch_type_of_date, (trans_date,))

            result = cursor.fetchone()
            if result:
                return result[0]  # Return the dateType if found

            return "Ordinary Day"  # Default to Ordinary Day if no match found

        except Error as e:
            logger.error(f"Error fetching type of date: {e}")
            return "Ordinary Day"  # Return default value on error

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logger.info("Database connection closed")

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
        search_text = instance.searchBioNum.text().strip().lower()
        logging.info(f"Search text: '{search_text}'")

        if not search_text:
            # Restore original data based on the instance type
            if hasattr(instance, 'original_data'):
                if hasattr(instance, 'paytimesheetTable'):
                    instance.populatePaytimeSheetTable(instance.original_data)
                elif hasattr(instance, 'paytransTable'):
                    instance.populatePayTransTable(instance.original_data)
                elif hasattr(instance, 'timeSheetTable'):
                    instance.populateTimeSheet(instance.original_data)
                elif hasattr(instance, 'timeListTable'):
                    instance.populateTimeList(instance.original_data)
            return

        # Search logic
        if hasattr(instance, 'paytimesheetTable'):
            # Search for PaytimeSheet
            for row in range(instance.paytimesheetTable.rowCount()):
                item = instance.paytimesheetTable.item(row, 1)  # Bio Num column is at index 1
                if item and search_text in item.text().lower():
                    instance.paytimesheetTable.setRowHidden(row, False)
                else:
                    instance.paytimesheetTable.setRowHidden(row, True)
        elif hasattr(instance, 'paytransTable'):
            # Search for PayTrans
            for row in range(instance.paytransTable.rowCount()):
                item = instance.paytransTable.item(row, 1)  # Bio Num column is at index 1
                if item and search_text in item.text().lower():
                    instance.paytransTable.setRowHidden(row, False)
                else:
                    instance.paytransTable.setRowHidden(row, True)
        elif hasattr(instance, 'filtered_data'):
            # Search for TimeSheet or TimeList
            filtered_data = [row for row in instance.filtered_data if row['BioNum'].startswith(search_text)]
            if hasattr(instance, 'populateTimeSheet'):
                instance.populateTimeSheet(filtered_data)
            elif hasattr(instance, 'populateTimeList'):
                instance.populateTimeList(filtered_data)
            elif hasattr(instance, 'populatePaytimeSheetTable'):
                instance.populatePaytimeSheetTable(filtered_data)
            elif hasattr(instance, 'populatePayTransTable'):
                instance.populatePayTransTable(filtered_data)