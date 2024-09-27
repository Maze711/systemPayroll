from MainFrame.Resources.lib import *
from MainFrame.notificationMaker import notificationLoader
from MainFrame.Database_Connection.DBConnection import create_connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def import_dat_file(dialog):
    fileName, _ = QFileDialog.getOpenFileName(dialog, "Open DAT File", "", "DAT Files (*.DAT)")
    if fileName:
        QTimer.singleShot(2, dialog.openTimeCard)

        notification_dialog = notificationLoader(fileName)
        notification_dialog.exec_()
    else:
        QMessageBox.information(dialog, "No File Selected", "Please select a DAT file to import.")
        return


def check_if_table_exists(dialog):
    connection = create_connection('NTP_LOG_IMPORTS')
    if connection is None:
        QMessageBox.critical(dialog, "Database Error", "Failed to connect to the LIST_LOG_IMPORT database.")
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        return len(tables) > 0
    except Exception as e:
        QMessageBox.critical(dialog, "Database Error", f"An error occurred: {e}")
        return False
    finally:
        cursor.close()
        connection.close()