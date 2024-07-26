import sys
import os

from mysql.connector import Error

from MainFrame.Database_Connection.DBConnection import create_connection
from Logger_config import get_logger

logging = get_logger()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def getTypeOfDate(trans_date):
    try:
        connection = create_connection('TIMEKEEPING')
        if connection is None:
            logging.error("Error: Could not establish database connection.")
            return "Ordinary Day"  # Return default value on connection failure


        cursor = connection.cursor()

        fetch_type_of_date = "SELECT dateType FROM type_of_dates WHERE date = %s"
        cursor.execute(fetch_type_of_date, (trans_date,))

        result = cursor.fetchone()
        if result:
            return result[0]  # Return the dateType if found

        return "Ordinary Day"  # Default to Ordinary Day if no match found

    except Error as e:
        logging.error(f"Error fetching type of date: {e}")
        return "Ordinary Day"  # Return default value on error

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Database connection closed")

def appendDate(fromCalendar, toCalendar, data):
    from_date = fromCalendar.date().toString("yyyy-MM-dd")
    to_date = toCalendar.date().toString("yyyy-MM-dd")

    filtered_data = [
        row for row in data
        if from_date <= row['trans_date'] <= to_date
    ]
    return filtered_data, from_date, to_date