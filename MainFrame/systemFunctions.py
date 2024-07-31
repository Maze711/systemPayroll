import sys
import os
import logging

from functools import wraps
from mysql.connector import Error

from MainFrame.Database_Connection.DBConnection import create_connection

class SingleFunctionLogger:
    def __init__(self, log_file='file_import.log'):
        self.log_file = log_file
        self.logger = logging.getLogger('SingleFunctionLogger')
        self.logger.setLevel(logging.INFO)
        self.file_handler = None

    def _setup_logger(self):
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)

        # Overwrite the log file each time a new function is logged
        self.file_handler = logging.FileHandler(self.log_file, mode='w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

    def log_function(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self._setup_logger()
            self.logger.info(f"Executing function: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"Function {func.__name__} completed successfully")
                return result
            except Exception as e:
                self.logger.error(f"Error in function {func.__name__}: {str(e)}")
                raise
        return wrapper

# Create an instance of the SingleFunctionLogger
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


class timekeepingFunction():
    def __init__(self):
        super(timekeepingFunction, self).__init__()

    @single_function_logger.log_function
    def getTypeOfDate(trans_date):
        logger = logging.getLogger('SingleFunctionLogger')
        try:
            connection = create_connection('TIMEKEEPING')
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
        search_text = instance.searchBioNum.text().strip()
        if not search_text:
            if hasattr(instance, 'populateTimeSheet'):
                instance.populateTimeSheet(instance.data)
            elif hasattr(instance, 'populateTimeList'):
                instance.populateTimeList(instance.filtered_data)
            return

        filtered_data = [row for row in instance.filtered_data if row['BioNum'].startswith(search_text)]
        if hasattr(instance, 'populateTimeSheet'):
            instance.populateTimeSheet(filtered_data)
        elif hasattr(instance, 'populateTimeList'):
            instance.populateTimeList(filtered_data)