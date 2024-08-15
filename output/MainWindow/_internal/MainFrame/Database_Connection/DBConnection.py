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
        # host = os.getenv(f'DB_HOST_{db_key}', '192.168.1.95')
        host = os.getenv(f'DB_HOST_{db_key}', 'localhost')
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

def test_databases_connection():
    """Test Databases Connection (for Debugging)"""
    file201_connection = create_connection('FILE201')
    timekeeping_connection = create_connection('TIMEKEEPING')
    listlogimport_connection = create_connection('LIST_LOG_IMPORT')
    systemAuthentication_connection = create_connection('SYSTEM_AUTHENTICATION')
    systemNotification_connection = create_connection('SYSTEM_NOTIFICATION')

    connections = {
        'FILE201': file201_connection,
        'TIMEKEEPING': timekeeping_connection,
        'LIST_LOG_IMPORT': listlogimport_connection,
        'SYSTEM_AUTHENTICATION': systemAuthentication_connection,
        'SYSTEM_NOTIFICATION': systemNotification_connection
    }

    for db_key, db_connection in connections.items():
        if db_connection is None or not db_connection.is_connected():
            msg = QMessageBox(None)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Failed to connect to database server. The application will exit.")
            msg.setWindowTitle("Database Connection Error")
            msg.setWindowFlag(Qt.WindowStaysOnTopHint) # Ensures the message box stays on top
            msg.exec_()

            sys.exit(1)

        if db_connection.is_connected():
            db_connection.close()
            logging.info(f"{db_key} database connection closed")