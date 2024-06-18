import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='file201',
            user='root',
            password=''
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