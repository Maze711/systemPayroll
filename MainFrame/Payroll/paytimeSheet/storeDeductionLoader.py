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
                        late_absent INT(11),
                        sss_loan INT(11),
                        pag_ibig_loan INT(11),
                        cash_advance INT(11),
                        canteen INT(11),
                        tax INT(11),
                        sss INT(11),
                        medicare_philhealth INT(11),
                        pag_ibig INT(11),
                        clinic INT(11),
                        arayata_manual INT(11),
                        hmi INT(11),
                        funeral INT(11),
                        voluntary INT(11),
                        
                        tyls INT(11),
                        osallow INT(11),
                        cbaallow INT(11),
                        hazpay INT(11),
                        pa INT(11),
                        holearnsund INT(11),
                        backpay INT(11),
                        
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
                        each_data.get('TYLS', 0),
                        each_data.get('OS_Allowance', 0),
                        each_data.get('CBA_Allowance', 0),
                        each_data.get('Hazard_Pay', 0),
                        each_data.get('PA', 0),
                        each_data.get('HolEarn_SunND', 0),
                        each_data.get('Backpay', 0),
                        user
                    )

                    logging.info(f"Inserting values: {values}")

                    insert_query = f"""
                        INSERT INTO {table_name} (
                            empNum, bioNum, empName, late_absent, sss_loan, pag_ibig_loan, cash_advance, 
                            canteen, tax, sss, medicare_philhealth, pag_ibig, clinic, 
                            arayata_manual, hmi, funeral, voluntary, TYLS, osallow, cbaallow,
                            hazpay, pa, holearnsund, backpay, deduction_placed_by, deduction_placed_date
                        ) 
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, NOW()
                        ) 
                        ON DUPLICATE KEY UPDATE 
                            late_absent = VALUES(late_absent), 
                            sss_loan = VALUES(sss_loan), 
                            pag_ibig_loan = VALUES(pag_ibig_loan),
                            cash_advance = VALUES(cash_advance), 
                            canteen = VALUES(canteen), 
                            tax = VALUES(tax),
                            sss = VALUES(sss), 
                            medicare_philhealth = VALUES(medicare_philhealth), 
                            pag_ibig = VALUES(pag_ibig),
                            clinic = VALUES(clinic), 
                            arayata_manual = VALUES(arayata_manual), 
                            hmi = VALUES(hmi), 
                            funeral = VALUES(funeral), 
                            voluntary = VALUES(voluntary), 
                            TYLS = VALUES(TYLS),
                            osallow = VALUES(osallow), 
                            cbaallow = VALUES(cbaallow), 
                            hazpay = VALUES(hazpay), 
                            holearnsund = VALUES(holearnsund), 
                            backpay = VALUES(backpay), 
                            deduction_placed_by = VALUES(deduction_placed_by), 
                            deduction_placed_date = NOW()
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
