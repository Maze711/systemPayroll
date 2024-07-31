from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection

# Configure Logging
logger = logging.getLogger(__name__)


def getAllFetchEmployees():
    try:
        connection = create_connection('FILE201')
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return None

        cursor = connection.cursor()

        # Fetches all the employees in personal_information table
        fetch_all_employees = "SELECT empl_id, surname, firstname, mi FROM emp_info"

        cursor.execute(fetch_all_employees)
        result = cursor.fetchall()
        logger.info("Fetched all employees successfully")

        return result

    except Error as e:
        logger.error(f"Error fetching all employees: {e}")
        return None

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")
