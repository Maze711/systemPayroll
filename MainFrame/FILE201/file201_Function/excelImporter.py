import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.DBConnection import create_connection


def convert_to_24hour(time_str):
    try:
        if isinstance(time_str, str):
            if ':' in time_str:
                in_time = datetime.strptime(time_str, "%I:%M %p")
            else:
                in_time = datetime.strptime(time_str, "%I%p")
            return in_time.strftime("%H:%M")
        return None
    except ValueError:
        logging.warning(f"Unable to convert time: {time_str}")
        return None


def split_schedule(sche_name):
    if isinstance(sche_name, str) and '-' in sche_name:
        parts = sche_name.split('-')
        if len(parts) == 2:
            sched_in = convert_to_24hour(parts[0].strip())
            sched_out = convert_to_24hour(parts[1].strip().replace("sched", "").strip())
            return sched_in, sched_out
    return None, None


def split_empl_name(empl_name):
    if isinstance(empl_name, str):
        parts = empl_name.replace('.', '').split(',')
        surname = parts[0].strip() if len(parts) > 0 else ''
        firstname_parts = parts[1].strip().split() if len(parts) > 1 else []
        firstname = firstname_parts[0] if len(firstname_parts) > 0 else ''
        mi = firstname_parts[1] if len(firstname_parts) > 1 else ''
        return surname, firstname, mi
    return '', '', ''


def remove_dashes_in_id(id_number):
    id_number_without_dashes = id_number.replace("-", "")
    return id_number_without_dashes


def importIntoDB(parent, display_employees_callback):
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            parent, "Select Excel File", "", "Excel Files (*.xlsx)", options=options)
        if not file_name:
            QMessageBox.information(parent, "No File Selected", "Please select an Excel file to import.")
            return

        # Create and show the progress dialog
        excelImporterLoader = ExcelImporterLoader(parent, file_name, display_employees_callback)
        excelImporterLoader.exec_()
    except Exception as e:
        print(f"Error importing data from Excel: {e}")

def get_empl_ids_from_db():
    """
    Fetch `empl_id` values from the database tables and return as a set of integers.
    """
    try:
        with create_connection('FILE201') as connection:
            if connection is None:
                logging.error("Failed to connect to the FILE201 database.")
                return set()

            cursor = connection.cursor()

            # Query to fetch empl_id from all relevant tables
            queries = [
                "SELECT empl_id FROM emp_info",
                "SELECT empl_id FROM emp_list_id",
                "SELECT empl_id FROM emp_posnsched",
                "SELECT empl_id FROM emp_rate",
                "SELECT empl_id FROM emp_status",
                "SELECT empl_id FROM vacn_sick_count"
            ]

            empl_ids = set()
            for query in queries:
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    empl_ids.add(int(row[0]))  # Convert empl_id to int and add to the set

            return empl_ids

    except Exception as e:
        logging.error(f"An error occurred while fetching empl_ids: {str(e)}", exc_info=True)
        return set()


def compare_empl_id_with_excel(parent):
    """
    Compare `empl_id` from database with `empno` from the Excel file and print matches.
    """
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)", options=options)
        if not file_name:
            return

        workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
        sheet = workbook.sheet_by_index(0)

        # Fetch empl_ids from the database
        db_empl_ids = get_empl_ids_from_db()
        if not db_empl_ids:
            logging.error("No empl_ids found in the database.")
            return

        matched_empl_ids = set()

        # Iterate over rows in the Excel file
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        empno_col = headers.index('empno')

        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            empno_str = str(row[empno_col]).strip()
            try:
                empno = int(empno_str)  # Convert empno to int
                if empno in db_empl_ids:
                    matched_empl_ids.add(empno)
            except ValueError:
                logging.warning(f"Invalid empno value: {empno_str}. Skipping this row.")

        # Print the number of matches
        num_matches = len(matched_empl_ids)
        logging.info(f"Number of matched empno values: {num_matches}")
        QMessageBox.information(parent, "Comparison Result", f"Number of matched empno values: {num_matches}")

    except Exception as e:
        logging.error(f"An error occurred during comparison: {str(e)}", exc_info=True)
        QMessageBox.critical(parent, "Comparison Error", f"An error occurred while comparing data: {str(e)}")


def update_db_for_missing_row_columns(parent):
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)", options=options)
        if not file_name:
            return

        workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
        sheet = workbook.sheet_by_index(0)

        with create_connection('FILE201') as connection:
            if connection is None:
                logging.error("Failed to connect to the FILE201 database.")
                return
            logging.debug("Database connection established successfully.")

            cursor = connection.cursor()

            # Define mappings and queries
            emergency_list_mapping = {
                'empl_id': 'empno', 'emer_name': 'emer_name'
            }
            emp_info_column_mapping = {
                'empl_id': 'empno', 'empid': 'emp_id', 'status': 'civil_stat', 'sex': 'gender',
                'height': 'height', 'weight': 'weight', 'mobile': 'mobile', 'blood_type': 'blood_type', 'email': 'email'
            }
            list_column_mapping = {
                'empl_id': 'empno', 'sss': 'sssno',
                'tin': 'tin', 'pagibig': 'pagibig', 'philhealth': 'philhealth', 'bank_code': 'bank_code'
            }
            posnsched_column_mapping = {
                'empl_id': 'empno', 'pos_descr': 'pos_descr', 'dept_name': 'dept_name', 'sche_name': 'sche_name',
                'empid': 'emp_id'
            }
            status_column_mapping = {
                'empl_id': 'empno', 'position': 'pos_descr'
            }
            vacnsick_column_mapping = {
                'empl_id': 'empno', 'max_vacn': 'max_vacn', 'max_sick': 'max_sick'
            }

            update_emergency_query = """
                UPDATE emergency_list SET emer_name = %s WHERE empl_id = %s
            """
            update_personal_query = """
                UPDATE emp_info SET empid = %s, status = %s, sex = %s, height = %s, weight = %s, mobile = %s, 
                blood_type = %s, email = %s WHERE empl_id = %s
            """
            update_list_query = """
                UPDATE emp_list_id SET sss = %s, tin = %s, pagibig = %s, philhealth = %s, bank_code = %s WHERE empl_id = %s
            """
            update_posnsched_query = """
                UPDATE emp_posnsched SET empid = %s, pos_descr = %s, sched_in = %s, sched_out = %s, dept_name = %s WHERE empl_id = %s
            """
            update_status_query = """
                UPDATE emp_status SET position = %s WHERE empl_id = %s
            """
            update_vacnsick_query = """
                UPDATE vacn_sick_count SET max_vacn = %s, max_sick = %s WHERE empl_id = %s
            """

            # Collect rows for batch insertion
            emergency_data, emp_info_data, list_data, posnsched_data, status_data, vacnsick_data = [], [], [], [], [], []

            headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
            empno_col = headers.index('empno')

            # Fetch empl_ids from the database
            db_empl_ids = get_empl_ids_from_db()
            if not db_empl_ids:
                logging.error("No empl_ids found in the database.")
                return

            matched_empl_ids = set()

            for row_idx in range(1, sheet.nrows):
                row = sheet.row_values(row_idx)
                empno_str = str(row[empno_col]).strip()
                try:
                    empno = int(empno_str)  # Convert empno to int
                    if empno in db_empl_ids:
                        matched_empl_ids.add(empno)
                except ValueError:
                    logging.warning(f"Invalid empno value: {empno_str}. Skipping this row.")

            list_of_matched_empl_ids = list(matched_empl_ids)  # Convert set of matched_empl_id to list

            for row_idx in range(1, sheet.nrows):
                row = sheet.row_values(row_idx)
                empno_str = str(row[headers.index('empno')]).strip()
                empno = int(empno_str)  # Convert empno to int

                if empno not in list_of_matched_empl_ids:
                    continue  # Skip rows that don't match

                # Emergency List
                emergency_row = (
                    str(row[headers.index(emergency_list_mapping['emer_name'])]),
                    empno
                )
                emergency_data.append(emergency_row)

                # Employee Info
                info_row = (
                    str(row[headers.index(emp_info_column_mapping['empid'])]),
                    str(row[headers.index(emp_info_column_mapping['status'])]),
                    str(row[headers.index(emp_info_column_mapping['sex'])]),
                    str(row[headers.index(emp_info_column_mapping['height'])]),
                    str(row[headers.index(emp_info_column_mapping['weight'])]),
                    str(row[headers.index(emp_info_column_mapping['mobile'])]),
                    str(row[headers.index(emp_info_column_mapping['blood_type'])]),
                    str(row[headers.index(emp_info_column_mapping['email'])]),
                    empno
                )
                emp_info_data.append(info_row)

                # List Info
                list_row = (
                    remove_dashes_in_id(str(row[headers.index(list_column_mapping['sss'])])),
                    remove_dashes_in_id(str(row[headers.index(list_column_mapping['tin'])])),
                    remove_dashes_in_id(str(row[headers.index(list_column_mapping['pagibig'])])),
                    remove_dashes_in_id(str(row[headers.index(list_column_mapping['philhealth'])])),
                    row[headers.index(list_column_mapping['bank_code'])],
                    empno
                )
                list_data.append(list_row)

                # Position Schedule
                sched_in, sched_out = split_schedule(str(row[headers.index(posnsched_column_mapping['sche_name'])]))
                posnsched_row = (
                    row[headers.index(posnsched_column_mapping['empid'])],
                    str(row[headers.index(posnsched_column_mapping['pos_descr'])]).upper(),
                    sched_in,
                    sched_out,
                    str(row[headers.index(posnsched_column_mapping['dept_name'])]),
                    empno

                )
                posnsched_data.append(posnsched_row)

                # Status Info
                status_row = (
                    str(row[headers.index(status_column_mapping['position'])]).upper(),
                    empno
                )
                status_data.append(status_row)

                # Vacation & Sick Count
                vacnsick_row = (
                    str(row[headers.index(vacnsick_column_mapping['max_vacn'])]),
                    str(row[headers.index(vacnsick_column_mapping['max_sick'])]),
                    empno
                )
                vacnsick_data.append(vacnsick_row)

            # Batch Insert Data
            cursor.executemany(update_emergency_query, emergency_data)
            cursor.executemany(update_personal_query, emp_info_data)
            cursor.executemany(update_list_query, list_data)
            cursor.executemany(update_posnsched_query, posnsched_data)
            cursor.executemany(update_status_query, status_data)
            cursor.executemany(update_vacnsick_query, vacnsick_data)

            connection.commit()

            QMessageBox.information(parent, "Updated Successful", "Updated Successfully")
            logging.info("Data successfully updated into the database.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        QMessageBox.critical(parent, "Updating import Error", f"An error occurred while updating data: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

class ImportProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def process_import(self):
        """ Processes importing data from an Excel file with progress updates. """
        connection = None
        cursor = None

        try:
            # Read the entire Excel file
            df = pd.read_excel(self.file_name, sheet_name=None)  # Load all sheets into a dictionary of DataFrames
            sheet = df[list(df.keys())[0]]  # Get the first sheet

            # Fetch the headers from the DataFrame
            headers = sheet.columns.tolist()

            required_columns = {
                'personal': [
                    'empl_no', 'empl_id', 'idnum', 'empid', 'surname', 'firstname', 'mi', 'street', 'city', 'zipcode',
                    'birthday',
                    'birthplace', 'religion', 'status', 'sex', 'height', 'weight', 'mobile', 'blood_type', 'email'
                ],
                'emergency': ['empl_no', 'empl_id', 'idnum', 'emer_name'],
                'list': ['empl_no', 'empl_id', 'idnum', 'taxstat', 'sss', 'tin', 'pagibig', 'philhealth', 'bank_code',
                         'cola'],
                'posnsched': ['empl_no', 'empl_id', 'empid', 'idnum', 'pos_descr', 'sched_in', 'sched_out',
                              'dept_name'],
                'rate': ['empl_no', 'empl_id', 'idnum', 'rph', 'rate', 'mth_salary', 'dailyallow', 'mntlyallow'],
                'status': ['empl_no', 'empl_id', 'idnum', 'compcode', 'dept_code', 'position', 'emp_stat', 'date_hired',
                           'resigned', 'dtresign'],
                'vacnsick': ['empl_no', 'empl_id', 'idnum', 'max_vacn', 'max_sick']
            }

            # Check for missing columns
            missing_columns = [col for section in required_columns.values() for col in section if col not in headers]
            if missing_columns:
                error_message = f"\nMissing required columns: \n{', '.join(missing_columns)}"
                self.error.emit(error_message)
                return

            with create_connection('FILE201') as connection:
                if connection is None:
                    logging.error("Failed to connect to the FILE201 database.")
                    return
                logging.debug("Database connection established successfully.")

                cursor = connection.cursor()

                # Prepare queries
                insert_queries = {
                    'emergency': """
                        INSERT IGNORE INTO emergency_list (empl_no, empl_id, idnum, emer_name)
                        VALUES (%s, %s, %s, %s)
                    """,
                    'personal': """
                        INSERT IGNORE INTO emp_info (empl_no, empl_id, idnum, empid, surname, firstname, mi, street, city, zipcode, birthday,
                        birthplace, religion, status, sex, height, weight, mobile, blood_type, email)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    'list': """
                        INSERT IGNORE INTO emp_list_id (empl_no, empl_id, idnum, taxstat, sss, tin, pagibig, philhealth, bank_code, cola)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    'posnsched': """
                        INSERT IGNORE INTO emp_posnsched (empl_no, empl_id, empid, idnum, pos_descr, sched_in, sched_out, dept_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    'rate': """
                        INSERT IGNORE INTO emp_rate (empl_no, empl_id, idnum, rph, rate, mth_salary, dailyallow, mntlyallow)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    'status': """
                        INSERT IGNORE INTO emp_status (empl_no, empl_id, idnum, compcode, dept_code, position, emp_stat, date_hired, resigned, dtresign)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    'vacnsick': """
                        INSERT IGNORE INTO vacn_sick_count (empl_no, empl_id, idnum, max_vacn, max_sick)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                }

                data = {
                    'emergency': [],
                    'personal': [],
                    'list': [],
                    'posnsched': [],
                    'rate': [],
                    'status': [],
                    'vacnsick': []
                }

                # Manually split data into chunks
                chunk_size = 1000  # Adjust chunk size based on your needs
                num_chunks = (len(sheet) + chunk_size - 1) // chunk_size

                for chunk_idx in range(num_chunks):
                    chunk_start = chunk_idx * chunk_size
                    chunk_end = min(chunk_start + chunk_size, len(sheet))
                    chunk_df = sheet.iloc[chunk_start:chunk_end]

                    # Process each row in the chunk
                    for row_idx, row in chunk_df.iterrows():
                        empl_no = str(row['empl_no']).strip()
                        surname = str(row['surname']).strip()
                        firstname = str(row['firstname']).strip()

                        if not empl_no:
                            continue  # Skip rows without an employee number

                        try:
                            for section in data.keys():
                                row_data = tuple(str(row[col]).strip() for col in required_columns[section])
                                data[section].append(row_data)
                                logging.debug(f"{section} data length: {len(row_data)}")
                        except Exception as e:
                            logging.error(f"Error processing row {row_idx}: {e}")
                            continue

                    # Batch Insert Data
                    for section, insert_query in insert_queries.items():
                        if data[section]:
                            cursor.executemany(insert_query, data[section])
                            logging.debug(f"Inserted {len(data[section])} rows into {section}.")
                            data[section] = []  # Clear data for next chunk

                    # Navigate current progress
                    progress = int(((chunk_idx + 1) / num_chunks) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)

                connection.commit()
                self.finished.emit("Data imported successfully.")

        except Exception as e:
            print(f"Error in importIntoDB: {str(e)}")
            logging.error(f"Error in importIntoDB: {str(e)}")
            self.error.emit(str(e))
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

class ExcelImporterLoader(QDialog):
    def __init__(self, hr_window, file_name, display_employees_callback):
        super(ExcelImporterLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        self.file_name = file_name
        self.hr_window = hr_window
        self.display_employees_callback = display_employees_callback

        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = ImportProcessor(self.file_name)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.importProcessingFinished)
        self.worker.error.connect(self.importProcessingError)
        self.thread.started.connect(self.worker.process_import)
        self.thread.start()

        self.move_to_bottom_right()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def importProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.display_employees_callback()
        QMessageBox.information(self.hr_window, "Success", message)
        self.close()

    def importProcessingError(self, error):
        try:
            self.progressBar.setVisible(False)
            self.thread.quit()
            self.thread.wait()

            QMessageBox.critical(self.hr_window, "Import Error",
                                 f"An unexpected error occurred while importing data:\n{error}")
            self.close()
        except Exception as e:
            print("Error in importProcessingError: ", e)

    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)