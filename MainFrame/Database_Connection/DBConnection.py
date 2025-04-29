from MainFrame.Resources.lib import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load environment variables from .env file
dotenv_path = resource_path("MainFrame\\Database_Connection\\.env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def create_connection(db_key):
    try:
        # host = os.getenv(f'DB_HOST_{db_key}', 'localhost')
        host = os.getenv(f'DB_HOST_{db_key}', '192.168.68.51')
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
        logging.warning(f"Error while connecting to MySQL {database}: {str(e)}")
        return None


def test_databases_connection():
    """Test Databases Connection (for Debugging)"""
    file201_connection = create_connection('NTP_EMP_LIST')
    timekeeping_connection = create_connection('NTP_HOLIDAY_LIST')
    listlogimport_connection = create_connection('NTP_LOG_IMPORTS')
    systemAuthentication_connection = create_connection('NTP_EMP_AUTH')
    systemNotification_connection = create_connection('NTP_ACCOUNTANT_NOTIFICATION')
    systemStoreDeduction_connection = create_connection('NTP_STORED_DEDUCTIONS')

    connections = {
        'NTP_EMP_LIST': file201_connection,
        'NTP_HOLIDAY_LIST': timekeeping_connection,
        'NTP_LOG_IMPORTS': listlogimport_connection,
        'NTP_EMP_AUTH': systemAuthentication_connection,
        'NTP_ACCOUNTANT_NOTIFICATION': systemNotification_connection,
        'NTP_STORED_DEDUCTIONS': systemStoreDeduction_connection
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