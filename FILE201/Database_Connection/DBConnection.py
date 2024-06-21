import mysql.connector
from mysql.connector import Error
import logging
import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_connection():
    try:
        host = os.getenv('DB_HOST', '127.0.0.1')
        database = os.getenv('DB_DATABASE')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        port = int(os.getenv('DB_PORT', 3306))  # Default MySQL port is 3306

        # Print the connection parameters for debugging
        print(f"Connecting to database with host={host}, database={database}, user={user}, port={port}")

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
            logger.info("Connected to MySQL database")
            print("Connection to MySQL database was successful")
            return connection
        else:
            logger.info("Failed to connect to MySQL database")
            print("Failed to connect to MySQL database")
            return None
    except Error as e:
        logger.exception("Error while connecting to MySQL: %s", e)
        print("Error while connecting to MySQL:", e)
        return None
    except ValueError as ve:
        logger.error("Configuration error: %s", ve)
        print("Configuration error:", ve)
        return None

# Example usage
connection = create_connection()
if connection:
    # Perform database operations
    connection.close()