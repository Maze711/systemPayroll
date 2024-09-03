import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.Database_Connection.DBConnection import create_connection

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

class StoringDeductionProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data

        self.user_session = UserSession().getALLSessionData()

    def processStoringDeduction(self):
        """  Main processing method that handles the entire workflow. """
        connection = create_connection('NTP_STORED_DEDUCTIONS')
        if connection is None:
            logging.error("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            self.error.emit("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            return

        cursor = connection.cursor()

        """ Creates a table in the database """
        table_name = "deductions"

        create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        ID INT AUTO_INCREMENT PRIMARY KEY, 
                        empNum INT(11),
                        bioNum INT(11),
                        empName VARCHAR(225),
                        payDed1 INT(11),
                        payDed2 INT(11),
                        payDed3 INT(11),
                        payDed4 INT(11),
                        payDed5 INT(11),
                        payDed6 INT(11),
                        payDed7 INT(11),
                        payDed8 INT(11),
                        payDed9 INT(11),
                        payDed10 INT(11),
                        payDed11 INT(11),
                        payDed12 INT(11),
                        payDed13 INT(11),
                        payDed14 INT(11),
                        deduction_placed_by VARCHAR(225),
                        deduction_placed_date DATETIME,
                        UNIQUE KEY unique_entry (empNum, bioNum, empName)
                    )
                """
        try:
            cursor.execute(create_table_query)
            connection.commit()
        except Error as e:
            logging.error(f"Error creating table {table_name}: {e}")
            self.error.emit(f"Error creating table {table_name}: {e}")
            return

        try:
            deduction_data = self.data
            total_deduction_data = len(deduction_data)
            user = self.user_session['user_name']

            for i, each_data in enumerate(deduction_data):
                """ Insertion of each data in the table """
                try:
                    values = (
                        each_data.get('Emp Number', 0),  # Default to 0 if not present
                        each_data.get('Bio Num', 0),
                        each_data.get('Employee Name', ""),
                        each_data.get('Late/Absent', 0),
                        each_data.get('SSS_Loan', 0),
                        each_data.get('Pag_Ibig_Loan', 0),
                        each_data.get('Cash_Advance', 0),
                        each_data.get('Canteen', 0),
                        each_data.get('Tax', 0),
                        each_data.get('SSS', 0),
                        each_data.get('Medicare/PhilHealth', 0),
                        each_data.get('PAGIBIG', 0),
                        each_data.get('Clinic', 0),
                        each_data.get('Arayata_Annual', 0),
                        each_data.get('HMI', 0),
                        each_data.get('Funeral', 0),
                        each_data.get('Voluntary', 0),
                        user
                    )

                    insert_query = f"""
                                   INSERT INTO {table_name} (
                                    empNum, bioNum, empName, payDed1, payDed2, payDed3, payDed4, 
                                    payDed5, payDed6, payDed7, payDed8, payDed9, payDed10, 
                                    payDed11, payDed12, payDed13, payDed14, deduction_placed_by, deduction_placed_date
                                ) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()) 
                                ON DUPLICATE KEY UPDATE 
                                    payDed1 = VALUES(payDed1), payDed2 = VALUES(payDed2), payDed3 = VALUES(payDed3),
                                    payDed4 = VALUES(payDed4), payDed5 = VALUES(payDed5), payDed6 = VALUES(payDed6),
                                    payDed7 = VALUES(payDed7), payDed8 = VALUES(payDed8), payDed9 = VALUES(payDed9),
                                    payDed10 = VALUES(payDed10), payDed11 = VALUES(payDed11), payDed12 = VALUES(payDed12), 
                                    payDed13 = VALUES(payDed13), payDed14 = VALUES(payDed14), 
                                    deduction_placed_by = VALUES(deduction_placed_by), deduction_placed_date = NOW()
                            """

                    cursor.execute(insert_query, values)
                    connection.commit()
                    progress = int(((i + 1) / total_deduction_data) * 100)
                    print(f"Emitting progress: {progress}")
                    self.progressChanged.emit(progress)

                except KeyError as e:
                    logging.error(f"KeyError for employee data: Missing key {e} in {each_data}")
                    self.error.emit(f"KeyError: Missing key {e} in {each_data}")
                except Error as e:
                    logging.error(f"Error inserting data for row {each_data.get('Employee Name')}: {e}")
                    self.error.emit(f"Error inserting data for row {each_data.get('Employee Name')}: {e}")

            self.finished.emit("Deduction Data has been successfully stored in the database")
        except Error as e:
            logging.error(f"Error fetching or processing deduction data: {e}")
            self.error.emit(f"Error fetching or processing deduction data: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

class StoreDeductionLoader(QDialog):
    def __init__(self, data, paytimeSheet_window):
        super(StoreDeductionLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        self.data = data

        self.paytimeSheet_window = paytimeSheet_window

        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = StoringDeductionProcessor(self.data)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.storingProcessingFinished)
        self.worker.error.connect(self.storingProcessingError)
        self.thread.started.connect(self.worker.processStoringDeduction)
        self.thread.start()

        self.move_to_bottom_right()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def storingProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.information(self.paytimeSheet_window, "Successfully Stored",
                                "Deduction Data has been successfully stored in the database")
        self.close()

    def storingProcessingError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.paytimeSheet_window, "Storing Deduction Error",
                             f"An unexpected error occurred while sending emails:\n{error}")
        self.close()

    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)