from MainFrame.Resources.lib import *
from PyQt5.QtWidgets import QApplication
from MainFrame.MainWindow import MainWindow, duration_logger  # Adjust the import path if necessary
from MainFrame.fontLoader import load_fonts


def main():
    start_time = time.time()
    logging.debug("Starting application")

    try:
        app = QApplication(sys.argv)
        load_fonts()
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error("Error occurred while loading application: %s", str(e))
        print(f"Error occurred: {e}")
        sys.exit(1)
    finally:
        end_time = time.time()
        duration = end_time - start_time
        duration_logger.info(f"Application loaded in {duration:.2f} seconds")
        print(f"Application loaded in {duration:.2f} seconds")


if __name__ == "__main__":
    main()
