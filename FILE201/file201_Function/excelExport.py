import logging
import pandas as pd

from mysql.connector import Error
from FILE201.Database_Connection.DBConnection import create_connection

logger = logging.getLogger(__name__)

def fetch_personal_information():
    query = """
    SELECT empID, lastName, firstName, middleName, street, barangay, city, province, zip,
           phoneNum, height, weight, civilStatus, dateOfBirth, placeOfBirth, gender
    FROM personal_information
    """
    try:
        connection = create_connection()
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return []

        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]
        return results, columns

    except Error as e:
        logger.error(f"Error fetching personal information: {e}")
        return [], []

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def export_to_excel(data, columns, file_name="personal_information.xlsx"):
    try:
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(file_name, index=False)
        print(f"Data exported successfully to {file_name}")
    except Exception as e:
        logger.error(f"Error exporting data to Excel: {e}")
        print(f"Error: {e}")
