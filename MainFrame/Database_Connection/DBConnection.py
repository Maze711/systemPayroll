import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *

# Configure the logger
# logging.basicConfig(
#     filename='db_error.log',
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load environment variables from .env file
#dotenv_path = resource_path("C:/Users/Maze/Desktop/systemPayroll/MainFrame/Database_Connection/.env")
dotenv_path = resource_path("MainFrame\\Database_Connection\\.env")
#logging.info(f"Loading .env file from: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    #logging.info("Environment variables loaded.")


#else:
#logging.error(f".env file not found at: {dotenv_path}")

def create_connection(db_key):
    try:
        host = os.getenv(f'DB_HOST_{db_key}', '192.168.1.2')
        database = os.getenv(f'DB_DATABASE_{db_key}')
        user = os.getenv(f'DB_USER_{db_key}', 'root')
        password = os.getenv(f'DB_PASSWORD_{db_key}', '')
        port = int(os.getenv(f'DB_PORT_{db_key}', 3306))

        logging.info(f"Host: {host}, Database: {database}, User: {user}, Port: {port}")

        if database is None:
            logging.error(f"Database name is not specified in the .env file for key {db_key}")
            return None

        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            logging.info(f"Connection to {database} database was successful")
            return connection
        else:
            logging.warning(f"Failed to connect to {database} database")
            return None
    except Error as e:
        logging.error(f"Error while connecting to MySQL {database}: {e}")
        return None


# Test connections (for debugging)
file201_connection = create_connection('FILE201')
timekeeping_connection = create_connection('TIMEKEEPING')
listlogimport_connection = create_connection('LIST_LOG_IMPORT')
systemAuthentication_connection = create_connection('SYSTEM_AUTHENTICATION')

if file201_connection and file201_connection.is_connected():
    file201_connection.close()
    logging.info("FILE201 database connection closed")

if timekeeping_connection and timekeeping_connection.is_connected():
    timekeeping_connection.close()
    logging.info("TIMEKEEPING database connection closed")

if listlogimport_connection and listlogimport_connection.is_connected():
    listlogimport_connection.close()
    logging.info("List Log Import database connection closed")

if systemAuthentication_connection and systemAuthentication_connection.is_connected():
    systemAuthentication_connection.close()
    logging.info("System Authentication database connection closed")
