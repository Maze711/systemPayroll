import sys
import os



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.TimeKeeping.timeCardMaker.timeCard import timecard
from MainFrame.systemFunctions import globalFunction, single_function_logger
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.notificationMaker import notificationLoader

class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        self.data = pd.DataFrame()  # Initialize as an empty DataFrame
        self.temp_folder = os.path.join(os.path.dirname(self.fileName), "temp_chunks")

    @single_function_logger.log_function
    def process(self):
        """Main processing method that handles the entire workflow."""
        try:
            self.processContent()

            # Create a temporary folder if it does not exist
            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

            # Chunk data into months and process each chunk
            chunks = self.chunkDataByMonth()
            total_chunks = len(chunks)
            for i, (chunk_name, chunk_data) in enumerate(chunks.items()):
                chunk_file = os.path.join(self.temp_folder, f"{chunk_name}.csv")
                chunk_data.to_csv(chunk_file, sep='\t', index=False, header=False)
                self.importChunkToDatabase(chunk_file, chunk_name)
                progress = int(((i + 1) / total_chunks) * 100)
                self.progressChanged.emit(progress)
                QThread.msleep(1)

            self.finished.emit("Data imported successfully.")
        except Exception as e:
            logging.error(f"Error in process method: {e}")
            self.error.emit(f"Error in process method: {e}")

    def processContent(self):
        """Reads and processes the content of the input file."""
        try:
            self.data = pd.read_csv(
                self.fileName, sep='\t', header=None,
                names=['bio_no', 'date_time', 'mach_code', 'code_1', 'code_2', 'code_3']
            )
            # Split 'date_time' into 'date' and 'time'
            self.data['date'] = self.data['date_time'].str.split(' ').str[0]
            self.data['time'] = self.data['date_time'].str.split(' ').str[1]
            # Determine the schedule based on code values
            self.data['sched'] = self.data.apply(
                lambda row: self.determine_schedule(str(row['code_1']), str(row['code_2']), str(row['code_3'])), axis=1
            )
            self.data = self.combineTimeInOut()  # Combine Time IN and Time OUT
        except Exception as e:
            logging.error(f"Error processing content: {e}")
            self.error.emit(f"Error processing content: {e}")

    def determine_schedule(self, code_1, code_2, code_3):
        """Determines the schedule type based on code values."""
        if code_1 == '0' and code_2 == '1' and code_3 == '0':
            return 'Time IN'
        elif code_1 in ['1', '5'] and code_2 == '1' and code_3 == '0':
            return 'Time OUT'
        else:
            return 'Unknown'

    def combineTimeInOut(self):
        """Combines Time IN and Time OUT into a single DataFrame."""
        # Separate Time IN and Time OUT entries
        time_in_data = self.data[self.data['sched'] == 'Time IN']
        time_out_data = self.data[self.data['sched'] == 'Time OUT']

        # Merge Time IN with the latest Time OUT on the same date
        combined_data = []
        for _, time_in_row in time_in_data.iterrows():
            matching_out = time_out_data[
                (time_out_data['bio_no'] == time_in_row['bio_no']) &
                (time_out_data['date'] == time_in_row['date'])
            ]
            if not matching_out.empty:
                # Take the last Time OUT entry
                last_out_row = matching_out.sort_values(by='time', ascending=False).iloc[0]
                combined_data.append([
                    time_in_row['bio_no'],
                    time_in_row['date'],
                    time_in_row['mach_code'],
                    time_in_row['time'],
                    last_out_row['time']
                ])

        combined_df = pd.DataFrame(combined_data, columns=['bio_no', 'date', 'mach_code', 'time_in', 'time_out'])
        return combined_df

    def chunkDataByMonth(self):
        """Chunks the data into months."""
        start_date = datetime.strptime(self.data['date'].min(), '%Y-%m-%d')
        end_date = datetime.strptime(self.data['date'].max(), '%Y-%m-%d')

        chunks = {}
        current_start = start_date

        while current_start <= end_date:
            year_month = current_start.strftime('%Y_%m')
            next_month_start = (current_start + timedelta(days=31)).replace(day=1)
            chunk_name = f"Table_{year_month}"
            chunk_data = self.data[
                (self.data['date'] >= current_start.strftime('%Y-%m-%d')) &
                (self.data['date'] < next_month_start.strftime('%Y-%m-%d'))
            ]
            chunks[chunk_name] = chunk_data
            current_start = next_month_start

        return chunks

    def importChunkToDatabase(self, chunk_file, chunk_name):
        """Imports the chunk data into the database."""
        connection = create_connection('LIST_LOG_IMPORT')
        if connection is None:
            self.error.emit("Failed to connect to LIST_LOG_IMPORT database.")
            return

        cursor = connection.cursor()

        # Create table name based on chunk name
        table_name = chunk_name  # No need to replace '-' with '_'

        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                ID INT AUTO_INCREMENT PRIMARY KEY, 
                bioNum INT,
                date DATE,
                machCode VARCHAR(225),
                time_in TIME,
                time_out TIME,
                edited_by VARCHAR(225),
                edited_by_when DATETIME,
                UNIQUE KEY unique_entry (bioNum, date, machCode)
            )
        """
        try:
            cursor.execute(create_table_query)
            connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        except Error as e:
            logging.error(f"Error creating table: {e}")
            self.error.emit(f"Error creating table: {e}")
            return

        try:
            chunk_data = pd.read_csv(chunk_file, sep='\t', header=None)
            for _, entry in chunk_data.iterrows():
                insert_query = f"""
                    INSERT INTO {table_name} (bioNum, date, machCode, time_in, time_out)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        time_in = VALUES(time_in),
                        time_out = VALUES(time_out),
                        machCode = VALUES(machCode),
                        edited_by = '',
                        edited_by_when = NOW()
                """
                cursor.execute(insert_query, (entry[0], entry[1], entry[2], entry[3], entry[4]))
                connection.commit()
        except Error as e:
            logging.error(f"Error inserting data: {e}")
            self.error.emit(f"Error inserting data: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed.")

            # Delete the chunk file after processing
            try:
                os.remove(chunk_file)
                logging.info(f"Chunk file {chunk_file} deleted successfully.")
            except OSError as e:
                logging.error(f"Error deleting chunk file: {chunk_file}, {e}")



@single_function_logger.log_function
class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        logging.info("Initializing dialogModal...")
        self.setFixedSize(418, 392)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)
        logging.info("UI loaded successfully.")

        self.user_session = UserSession().getALLSessionData()

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

        self.current_time_set = datetime.now().strftime('%H:%M:%S')
        self.user_name_set = str(self.user_session.get("user_name", ""))
        self.user_role_set = str(self.user_session.get("user_role", ""))

    @single_function_logger.log_function
    def importTxt(self, *args):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            self.thread = QThread()
            self.worker = FileProcessor(fileName)
            self.worker.moveToThread(self.thread)
            self.worker.progressChanged.connect(self.updateProgressBar)
            self.worker.finished.connect(self.fileProcessingFinished)
            self.worker.error.connect(self.fileProcessingError)
            self.thread.started.connect(self.worker.process)
            self.thread.start()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fileProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        # Insert notification into the database
        self.insertNotification(f"File processed successfully: {os.path.basename(self.worker.fileName)}")

        QMessageBox.information(self, "Success", message)

        # Open notificationLoader dialog
        self.openNotificationLoader()

        QTimer.singleShot(2000, self.openTimeCard)  # Delay to ensure dialog is visible

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        # Insert error notification into the database
        self.insertNotification(f"Failed to process file: {os.path.basename(self.worker.fileName)}")

        QMessageBox.critical(self, "Error", f"Failed to process file: {error}")

    def insertNotification(self, message):
        """Inserts a notification into the send_notification table."""
        connection = create_connection('SYSTEM_NOTIFICATION')
        if connection is None:
            logging.error("Failed to connect to system_notification database.")
            return

        cursor = connection.cursor()
        try:
            insert_query = """
                INSERT INTO send_notification (time, message, user_name, from_role)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (self.current_time_set, message, self.user_name_set, self.user_role_set))
            connection.commit()
            logging.info("Notification inserted successfully.")
        except Error as e:
            logging.error(f"Error inserting notification: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def openNotificationLoader(self):
        """Opens the notificationLoader dialog."""
        try:
            self.notificationLoaderDialog = notificationLoader()
            self.notificationLoaderDialog.exec_()
        except Exception as e:
            logging.error(f"Failed to open notificationLoader dialog: {e}")

    def openTimeCard(self):
        self.timeCardDialog = timecard()
        self.close()
        self.timeCardDialog.exec_()