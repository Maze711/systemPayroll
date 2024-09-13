import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.user_session import UserSession

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        self.data = pd.DataFrame()  # Initialize as an empty DataFrame
        self.temp_folder = os.path.join(os.path.dirname(self.fileName), "temp_chunks")

    def process(self):
        """Main processing method that handles the entire workflow."""
        try:
            self.processContent()

            # Create a temporary folder if it does not exist
            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

            # Chunk data by month and process each chunk
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
        """Combines Time IN and Time OUT into a single DataFrame, using '00:00:00' for missing entries."""
        combined_data = []

        for bio_no, group in self.data.groupby(['bio_no', 'date']):
            time_in_data = group[group['sched'] == 'Time IN']
            time_out_data = group[group['sched'] == 'Time OUT']

            # Get the last Time IN and last Time OUT for the day
            last_time_in = time_in_data.sort_values(by='time').iloc[-1] if not time_in_data.empty else None
            last_time_out = time_out_data.sort_values(by='time').iloc[-1] if not time_out_data.empty else None

            if last_time_in is not None or last_time_out is not None:
                combined_data.append([
                    last_time_in['bio_no'] if last_time_in is not None else last_time_out['bio_no'],
                    last_time_in['date'] if last_time_in is not None else last_time_out['date'],
                    last_time_in['mach_code'] if last_time_in is not None else last_time_out['mach_code'],
                    last_time_in['time'] if last_time_in is not None else '00:00:00',
                    last_time_out['time'] if last_time_out is not None else '00:00:00'
                ])

        combined_df = pd.DataFrame(combined_data, columns=['bio_no', 'date', 'mach_code', 'time_in', 'time_out'])
        # Replace NaN values with '00:00:00'
        combined_df = combined_df.fillna('00:00:00')
        return combined_df

    def chunkDataByMonth(self):
        """Chunks the data by YYYY_MM."""
        chunks = {}

        for month, group in self.data.groupby(self.data['date'].str[:7]):
            chunk_name = f"Table_{month.replace('-', '_')}"
            if chunk_name not in chunks:
                chunks[chunk_name] = group
            else:
                chunks[chunk_name] = pd.concat([chunks[chunk_name], group])

        return chunks

    def importChunkToDatabase(self, chunk_file, chunk_name):
        """Imports the chunk data into the database, handling 'N/A' values."""
        connection = create_connection('NTP_LOG_IMPORTS')
        if connection is None:
            self.error.emit("Failed to connect to LIST_LOG_IMPORT database.")
            return

        cursor = connection.cursor()

        # Create table name based on chunk name
        table_name = chunk_name

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
        except Error as e:
            self.error.emit(f"Error creating table: {e}")
            return

        try:
            chunk_data = pd.read_csv(chunk_file, sep='\t', header=None, na_values=['N/A'], keep_default_na=False)
            chunk_data = chunk_data.fillna('N/A')
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
            self.error.emit(f"Error inserting data: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

            # Delete the chunk file after processing
            try:
                os.remove(chunk_file)
            except OSError as e:
                self.error.emit(f"Error deleting chunk file: {chunk_file}, {e}")


class notificationLoader(QDialog):
    importSuccessful = pyqtSignal()  # New signal for successful import

    def __init__(self, fileName):
        super(notificationLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

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

        self.move_to_bottom_right()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fileProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.information(self, "File Processing Complete", "The file has been successfully imported.")
        self.importSuccessful.emit()  # Emit the signal when import is successful
        self.close()

    def fileProcessingError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self, "File Processing Error", f"An error occurred while processing the file:\n{error}")
        self.close()

    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)