from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.user_session import UserSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

            # Print the employee IDs being processed
            for bio_no in self.data['bio_no']:
                print(f'Processing Bio No: {bio_no}')

            # Determine the schedule based on code values
            self.data['sched'] = self.data.apply(
                lambda row: self.determine_schedule(str(row['code_1']), str(row['code_2']), str(row['code_3'])), axis=1
            )

            self.data = self.combineTimeInOut()  # Combine Time IN and Time OUT
        except Exception as e:
            self.error.emit(f"Error processing content: {e}")

    def determine_schedule(self, code_1, code_2, code_3):
        """Determines the schedule type based on code values."""
        if code_1 == '0' and code_2 in ['0', '1'] and code_3 == '0':
            return 'Time IN'
        elif code_1 in ['1', '5'] and code_2 in ['0', '1'] and code_3 == '0':
            return 'Time OUT'
        else:
            return 'Unknown'

    def combineTimeInOut(self):
        """Combines Time IN and Time OUT entries, removing duplicates if CheckOut times are too close."""
        combined_data = []
        self.data = self.data.sort_values(['bio_no', 'date', 'time'])

        for bio_no, group in self.data.groupby('bio_no'):
            time_entries = group.to_dict('records')
            current_time_in = None
            current_time_out = None

            for i, entry in enumerate(time_entries):
                current_date = entry['date']
                current_time = entry['time']

                if entry['sched'] == 'Time IN':
                    # Handle duplicate Time IN entries: replace previous one if no Time OUT occurred yet
                    current_time_in = entry  # Always take the latest Time IN
                    current_time_out = None  # Clear any potential earlier Time OUT, as we have a new IN

                elif entry['sched'] == 'Time OUT':
                    # Handle duplicate Time OUT on the same day
                    if current_time_in:
                        # We have a valid Time IN, so now we can pair it with this Time OUT
                        if current_date != current_time_in['date']:
                            # If Time OUT is on a different day, split the records
                            combined_data.append([
                                bio_no,
                                current_time_in['date'],
                                current_time_in['mach_code'],
                                current_time_in['time'],
                                '00:00:00'
                            ])
                            combined_data.append([
                                bio_no,
                                current_date,
                                entry['mach_code'],
                                '00:00:00',
                                current_time
                            ])
                        else:
                            # Time IN and Time OUT on the same day, check for duplicate Time OUT
                            if current_time_out:
                                # Compare Time OUTs: keep the latest one (or the more accurate one)
                                previous_time_out = datetime.strptime(current_time_out['time'], '%H:%M:%S')
                                new_time_out = datetime.strptime(current_time, '%H:%M:%S')
                                time_diff = abs((new_time_out - previous_time_out).total_seconds())

                                # If the time difference between Time OUTs is small, consider them duplicates
                                if time_diff < 5:  # e.g., 5 seconds difference
                                    continue  # Skip the duplicate Time OUT
                                else:
                                    # Replace with the latest Time OUT if not considered a duplicate
                                    current_time_out = entry
                            else:
                                current_time_out = entry

                            # After resolving duplicates, append the valid Time IN and Time OUT
                            combined_data.append([
                                bio_no,
                                current_date,
                                current_time_in['mach_code'],
                                current_time_in['time'],
                                current_time
                            ])
                            current_time_in = None  # Clear Time IN after pairing
                            current_time_out = None  # Clear Time OUT after use

            # Handle remaining unmatched Time IN or OUT entries
            if current_time_in:
                # If we still have an unpaired Time IN, add it with a default Time OUT of 00:00:00
                combined_data.append([
                    bio_no,
                    current_time_in['date'],
                    current_time_in['mach_code'],
                    current_time_in['time'],
                    '00:00:00'
                ])
            elif current_time_out:
                # If we have a Time OUT with no Time IN, record it with default Time IN of 00:00:00
                combined_data.append([
                    bio_no,
                    current_time_out['date'],
                    current_time_out['mach_code'],
                    '00:00:00',
                    current_time_out['time']
                ])

        # Return the combined data as a DataFrame
        combined_df = pd.DataFrame(combined_data, columns=['bio_no', 'date', 'mach_code', 'time_in', 'time_out'])
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

        try:
            with connection.cursor() as cursor:
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
                        UNIQUE KEY unique_entry (bioNum, date, machCode, time_in)
                    )
                """
                cursor.execute(create_table_query)
                connection.commit()

                # Read chunk data from the file
                chunk_data = pd.read_csv(chunk_file, sep='\t', header=None, na_values=['N/A'], keep_default_na=False)
                chunk_data = chunk_data.fillna('N/A')

                unique_bio_nums = set()  # To track all unique bioNum entries

                for _, entry in chunk_data.iterrows():
                    bio_num_cleaned = str(entry[0]).strip() if entry[0] is not None else None
                    date_cleaned = str(entry[1]).strip() if entry[1] is not None else None
                    mach_code_cleaned = str(entry[2]).strip() if entry[2] is not None else None
                    time_in_cleaned = str(entry[3]).strip() if entry[3] is not None else None
                    time_out_cleaned = str(entry[4]).strip() if entry[4] is not None else None

                    # Track unique bioNum values
                    if bio_num_cleaned:
                        unique_bio_nums.add(bio_num_cleaned)

                    # Ensure bio_num_cleaned is not empty or whitespace
                    if not bio_num_cleaned:
                        print("Skipping empty bioNum entry.")
                        continue

                    # Convert bio_num to int if possible
                    try:
                        bio_num_cleaned = int(bio_num_cleaned)
                    except ValueError:
                        self.error.emit(f"Invalid bioNum: {bio_num_cleaned}")
                        continue

                    if not date_cleaned or not mach_code_cleaned:
                        self.error.emit(
                            f"Invalid data for insertion: bioNum={bio_num_cleaned}, date={date_cleaned}, machCode={mach_code_cleaned}, time_in={time_in_cleaned}, time_out={time_out_cleaned}"
                        )
                        continue

                    print(
                        f"Inserting: {bio_num_cleaned}, {date_cleaned}, {mach_code_cleaned}, {time_in_cleaned}, {time_out_cleaned}")

                    insert_query = f"""
                        INSERT INTO {table_name} (bioNum, date, machCode, time_in, time_out)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        machCode = VALUES(machCode), time_in = VALUES(time_in), time_out = VALUES(time_out)
                    """
                    cursor.execute(insert_query, (
                        bio_num_cleaned, date_cleaned, mach_code_cleaned, time_in_cleaned, time_out_cleaned))
                    connection.commit()

                    print(
                        f"Inserted: {bio_num_cleaned}, {date_cleaned}, {mach_code_cleaned}, {time_in_cleaned}, {time_out_cleaned}")

                # After processing all entries, print unique bioNum values
                print("Unique bioNum values processed:", unique_bio_nums)

        except Error as e:
            self.error.emit(f"Error inserting data: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()

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