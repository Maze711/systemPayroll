import logging
import os
import atexit

log_file = 'file_import.log'

def setup_logging():
    # Clear the contents of the log file at the start
    with open(log_file, 'w'):
        pass

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        filename=log_file,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Log the start of a new session
    logger.info("New logging session started")

    return logger

def delete_log_file():
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"Log file {log_file} deleted.")

# Register the delete_log_file function to run at exit
atexit.register(delete_log_file)

# Create a global logger instance
logger = setup_logging()

def get_logger():
    return logger
