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

    @single_function_logger.log_function
    def process(self):
        try:
            self.processContent()

            connection = create_connection('LIST_LOG_IMPORT')
            if connection is None:
                self.error.emit("Failed to connect to LIST_LOG_IMPORT database.")
                return

            cursor = connection.cursor()

            table_name = f"imported_data_{datetime.now().strftime('%Y%m%d%H%M%S')}"
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

            total_lines = len(self.data)
            for i, entry in enumerate(self.data):
                insert_query = f"""
                    INSERT INTO {table_name} (bioNum, date, time, sched)
                    VALUES (%s, %s, %s, %s)
                """
                try:
                    cursor.execute(insert_query, (entry['bio_no'], entry['trans_date'], entry['time'], entry['sched']))
                    connection.commit()
                except Error as e:
                    logging.error(f"Error inserting data: {e}")
                    self.error.emit(f"Error inserting data: {e}")
                    continue

                self.progressChanged.emit(int(((i + 1) / total_lines) * 100))
                QThread.msleep(1)

            self.finished.emit(table_name)
        except Exception as e:
            logging.error(f"Error in process method: {e}")
            self.error.emit(f"Error in process method: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed.")

    def processContent(self):
        try:
            with open(self.fileName, 'r') as file:
                rows = file.readlines()

            self.data = []
            for row in rows:
                columns = row.strip().split('\t')  # Adjusted to use tab split if needed
                if len(columns) < 6:
                    logging.error(f"Row has missing columns: {row}")
                    continue

                try:
                    bio_no, date_time, mach_code, code_1, code_2, code_3 = columns[:6]

                    # Validate date_time split
                    date_time_parts = date_time.split(' ')
                    if len(date_time_parts) != 2:
                        logging.error(f"DateTime split error for row: {row}, Split parts: {date_time_parts}")
                        continue

                    trans_date, time_value = date_time_parts

                except ValueError as e:
                    logging.error(f"Error parsing row: {row}, Error: {e}")
                    continue

                # Determine sched based on code_1, code_2, code_3 values
                if code_1 == '0' and code_2 == '1' and code_3 == '0':
                    sched = 'Time IN'
                elif code_1 == '1' and code_2 == '1' and code_3 == '0':
                    sched = 'Time OUT'
                else:
                    sched = 'Unknown'

                self.data.append({
                    'bio_no': bio_no.strip(),
                    'trans_date': trans_date.strip(),
                    'time': time_value.strip(),
                    'mach_code': mach_code.strip(),
                    'sched': sched
                })
        except Exception as e:
            logging.error(f"Error processing content: {e}")
            self.error.emit(f"Error processing content: {e}")


class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\dialogImporter.ui")
        loadUi(ui_file, self)

        self.importBTN.clicked.connect(self.importTxt)
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(False)

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

    def fileProcessingFinished(self, table_name):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        QMessageBox.information(self, "Success", f"Data imported successfully into table: {table_name}")

    def fileProcessingError(self, error):
        logging.error(f"Failed to read file: {error}")
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        QMessageBox.critical(self, "Error", f"Failed to process file: {error}")