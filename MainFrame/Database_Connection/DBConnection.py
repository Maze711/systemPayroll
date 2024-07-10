import sys
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)

# Load environment variables from .env file if it exists
dotenv_path = resource_path("MainFrame\\Database_Connection\\.env")
load_dotenv(dotenv_path)

def create_connection(db_key):
    try:
        host = os.getenv(f'DB_HOST_{db_key}', '127.0.0.1')
        database = os.getenv(f'DB_DATABASE_{db_key}')
        user = os.getenv(f'DB_USER_{db_key}')
        password = os.getenv(f'DB_PASSWORD_{db_key}')
        port = int(os.getenv('DB_PORT', 3306))  # Default MySQL port is 3306

        if not user or not database:
            raise ValueError("Database user and name must be provided")

        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            print(f"Connection to {database} database was successful")
            return connection
        else:
            print(f"Failed to connect to {database} database")
            return None
    except Error as e:
        print(f"Error while connecting to MySQL {database}:", e)
        return None
    except ValueError as ve:
        print("Configuration error:", ve)
        return None

# Connect to the FILE201 database
file201_connection = create_connection('FILE201')

# Connect to the TIMEKEEPING database
timekeeping_connection = create_connection('TIMEKEEPING')

if file201_connection and file201_connection.is_connected():
    file201_connection.close()
    print("FILE201 database connection closed")

if timekeeping_connection and timekeeping_connection.is_connected():
    timekeeping_connection.close()
    print("TIMEKEEPING database connection closed")
