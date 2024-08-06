from MainFrame.Resources.lib import *
from TimeKeeping.timeLogger.timeLog import timelogger
from MainFrame.systemFunctions import globalFunction, single_function_logger
from MainFrame.Database_Connection.DBConnection import create_connection


class FileProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        self.data = []
        self.temp_folder = os.path.join(os.path.dirname(self.fileName), "temp_chunks")

    @single_function_logger.log_function
    def process(self):
        try:
            self.processContent()

            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

            total_rows = len(self.data)
            chunks = self.chunkDataByDateRange(15)
            total_chunks = len(chunks)
            rows_processed = 0

            for i, (chunk_name, chunk_data) in enumerate(chunks.items()):
                chunk_file = os.path.join(self.temp_folder, f"{chunk_name}.csv")
                chunk_data.to_csv(chunk_file, sep='\t', index=False, header=False)
                rows_in_chunk = len(chunk_data)
                self.importChunkToDatabase(chunk_file, chunk_name)

                rows_processed += rows_in_chunk
                percentage = int((rows_processed / total_rows) * 100)
                self.progressChanged.emit(percentage)

                QThread.msleep(1)

            self.progressChanged.emit(100)  # Ensure progress reaches 100%
            self.finished.emit("Data imported successfully.")
        except Exception as e:
            logging.error(f"Error in process method: {e}")
            self.error.emit(f"Error in process method: {e}")

    def processContent(self):
        try:
            self.data = pd.read_csv(self.fileName, sep='\t', header=None,
                                    names=['bio_no', 'date_time', 'mach_code', 'code_1', 'code_2', 'code_3'])
            self.data['date_time'] = pd.to_datetime(self.data['date_time'])
            self.data['date'] = self.data['date_time'].dt.date
            self.data['time'] = self.data['date_time'].dt.time
            self.data['sched'] = self.data.apply(
                lambda row: self.determine_schedule(str(row['code_1']), str(row['code_2']), str(row['code_3'])), axis=1)
        except Exception as e:
            logging.error(f"Error processing content: {e}")
            self.error.emit(f"Error processing content: {e}")

    def determine_schedule(self, code_1, code_2, code_3):
        if code_1 == '0' and code_2 == '1' and code_3 == '0':
            return 'Time IN'
        elif code_1 == '1' and code_2 == '1' and code_3 == '0':
            return 'Time OUT'
        else:
            return 'Unknown'

    def chunkDataByDateRange(self, days):
        start_date = self.data['date'].min()
        end_date = self.data['date'].max()
        current_start = start_date

        chunks = {}
        while current_start <= end_date:
            current_end = current_start + timedelta(days=days - 1)
            chunk_name = f"{current_start.strftime('%Y%m%d')}_to_{current_end.strftime('%Y%m%d')}"
            chunk_data = self.data[(self.data['date'] >= current_start) &
                                   (self.data['date'] <= current_end)]
            chunks[chunk_name] = chunk_data
            current_start = current_end + timedelta(days=1)

        return chunks

    def importChunkToDatabase(self, chunk_file, chunk_name):
        connection = create_connection('LIST_LOG_IMPORT')
        if connection is None:
            self.error.emit("Failed to connect to LIST_LOG_IMPORT database.")
            return

        cursor = connection.cursor()
        table_name = f"imported_data_{chunk_name}"

        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        if result:
            logging.info(f"Table {table_name} already exists.")
        else:
            # Create table if it does not exist
            create_table_query = f"""
                CREATE TABLE {table_name} (
                    bioNum INT,
                    date DATE,
                    time TIME,
                    sched VARCHAR(10),
                    PRIMARY KEY (bioNum, date, time)
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

        # Insert or update data
        try:
            chunk_data = pd.read_csv(chunk_file, sep='\t', header=None, names=['bioNum', 'date', 'time', 'sched'])
            for _, entry in chunk_data.iterrows():
                insert_query = f"""
                    INSERT INTO {table_name} (bioNum, date, time, sched)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE sched=VALUES(sched)
                """
                cursor.execute(insert_query, (entry['bioNum'], entry['date'], entry['time'], entry['sched']))
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


class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

        # Store the original window flags
        self.original_flags = self.windowFlags()
        self.close_button_disabled_flags = self.original_flags | Qt.WindowStaysOnTopHint

    def set_buttons_enabled(self, enabled):
        self.importBTN.setEnabled(enabled)
        # Toggle the Close button
        if enabled:
            self.setWindowFlags(self.original_flags)
        else:
            self.setWindowFlags(self.close_button_disabled_flags)
        self.show()  # Ensure changes to window flags are applied

    def closeEvent(self, event):
        if self.importBTN.isEnabled():
            super().closeEvent(event)
        else:
            event.ignore()  # Ignore close event when processing

    @single_function_logger.log_function
    def importTxt(self, *args):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            self.set_buttons_enabled(False)  # Disable buttons while processing
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
        if value < 100:
            self.progressBar.setValue(value)
            self.progressBar.setFormat(f"{value}%")
        else:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fileProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.set_buttons_enabled(True)  # Re-enable buttons after processing
        self.thread.quit()
        self.thread.wait()
        QMessageBox.information(self, "Success", message)

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.set_buttons_enabled(True)  # Re-enable buttons after processing
        self.thread.quit()
        self.thread.wait()
        QMessageBox.critical(self, "Error", f"Failed to process file: {error}")
