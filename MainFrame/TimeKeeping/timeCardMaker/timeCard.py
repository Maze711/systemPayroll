import sys
import os

from MainFrame.TimeKeeping.schedValidator.checkSched import chkSched
from MainFrame.TimeKeeping.timeSheet.timeSheet import TimeSheet
from MainFrame.TimeKeeping.timeCardMaker.filter import filter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import globalFunction, timekeepingFunction, single_function_logger
import re


class timecard(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1442, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\timecard.ui")
        loadUi(ui_file, self)

        # Set up table
        self.TimeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeListTable.horizontalHeader().setStretchLastSection(True)

        # Get UI elements
        self.yearCC = self.findChild(QComboBox, 'yearCC')
        self.dateFromCC = self.findChild(QComboBox, 'dateFromCC')
        self.dateToCC = self.findChild(QComboBox, 'dateToCC')
        self.timeSheetButton = self.findChild(QPushButton, 'btnTimeSheet')

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')

        # Initialize the year combo box
        self.populate_year_combo_box()

        # Connect signals to slots
        self.yearCC.currentTextChanged.connect(self.populate_date_combo_boxes)
        self.dateFromCC.currentTextChanged.connect(self.populate_time_list_table)
        self.dateToCC.currentTextChanged.connect(self.populate_time_list_table)
        self.timeSheetButton.clicked.connect(self.createTimeSheet)

        self.searchBioNum.textChanged.connect(self.search_bioNum)
        self.btnCheckSched = self.findChild(QPushButton, 'btnCheckSched')
        self.btnCheckSched.clicked.connect(self.CheckSched)

        self.btnFilter = self.findChild(QPushButton, 'btnFilter')
        self.btnFilter.clicked.connect(self.filterModal)

        self.original_data = []
        filtered_data = []  # Initialized properly
        self.original_data = filtered_data.copy()

    def populate_year_combo_box(self):
        """Populate the year combo box with available year-month combinations from table names."""
        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # Extract year-month combinations from table names
            year_months = set()
            year_month_pattern = re.compile(r'table_(\d{4})_(\d{2})')

            for (table_name,) in tables:
                match = year_month_pattern.search(table_name)
                if match:
                    year_month = f"{match.group(1)}_{match.group(2)}"
                    year_months.add(year_month)

            # Add year-month combinations to the combo box
            self.yearCC.addItems(sorted(year_months))

        except Exception as e:
            logging.error(f"Error populating year combo box: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_date_combo_boxes(self):
        """Populate the date combo boxes based on the selected year-month."""
        selected_year_month = self.yearCC.currentText()
        if not selected_year_month:
            return

        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            table_name = f"table_{selected_year_month}"

            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                return

            # Extract days from the records in the selected year-month table
            days_from_set = set()
            days_to_set = set()

            cursor.execute(f"""
                SELECT DISTINCT DATE_FORMAT(date, '%d') AS day
                FROM `{table_name}`
            """)
            days = cursor.fetchall()

            for (day,) in days:
                days_from_set.add(day)
                days_to_set.add(day)

            # Update date combo boxes
            self.dateFromCC.clear()  # Clear previous items
            self.dateToCC.clear()  # Clear previous items
            self.dateFromCC.addItems(sorted(days_from_set))
            self.dateToCC.addItems(sorted(days_to_set))

        except Exception as e:
            logging.error(f"Error populating date combo boxes: {e}")

        finally:
            cursor.close()
            connection.close()

    @single_function_logger.log_function
    @single_function_logger.log_function
    def populate_time_list_table(self, checked=False):
        """Populate the time list table with check-in and check-out times, machCode, and employee data."""
        selected_year_month = self.yearCC.currentText()
        from_day = self.dateFromCC.currentText()
        to_day = self.dateToCC.currentText()

        if not selected_year_month or not from_day or not to_day:
            return

        logging.info(f"Populating time list table for: {selected_year_month}, from {from_day} to {to_day}")

        # Construct full dates
        from_date = f"{selected_year_month}-{from_day.zfill(2)}"
        to_date = f"{selected_year_month}-{to_day.zfill(2)}"

        # Construct table name
        table_name = f"table_{selected_year_month.replace('-', '_')}"

        connection_list_log = create_connection('LIST_LOG_IMPORT')
        connection_file201 = create_connection('FILE201')
        if not connection_list_log or not connection_file201:
            return

        try:
            cursor_list_log = connection_list_log.cursor()
            cursor_file201 = connection_file201.cursor()

            # Check if the table exists
            cursor_list_log.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor_list_log.fetchone():
                logging.error(f"Error: Table does not exist: {table_name}")
                return

            # Query to fetch time records including machCode from LIST_LOG_IMPORT
            query_list_log = f"""
                SELECT bioNum, date, time_in, time_out, machCode
                FROM `{table_name}`
                WHERE date BETWEEN '{from_date}' AND '{to_date}'
                ORDER BY bioNum, date, time_in
            """
            cursor_list_log.execute(query_list_log)
            records = cursor_list_log.fetchall()

            self.TimeListTable.setRowCount(0)
            time_data = {}

            for bioNum, trans_date, time_in, time_out, mach_code in records:
                if bioNum not in time_data:
                    time_data[bioNum] = {"Check_In": None, "Check_Out": None}

                if time_in:  # Consider `time_in` as Check_In
                    time_data[bioNum]["Check_In"] = (trans_date, str(time_in))
                if time_out:  # Consider `time_out` as Check_Out
                    time_data[bioNum]["Check_Out"] = (trans_date, str(time_out))

                # Query to get employee information and schedule from FILE201
                employee_query = (
                    "SELECT pi.surname, pi.firstname, pi.mi, ps.sched_in, ps.sched_out "
                    "FROM emp_info pi "
                    "JOIN emp_posnsched ps ON pi.empid = ps.empl_id "
                    f"WHERE pi.empid = {bioNum}"
                )

                logging.error(f"Executing query for bioNum: {bioNum}")
                logging.error(f"Query: {employee_query}")

                try:
                    # Fetch employee data and schedule info
                    cursor_file201.execute(employee_query)
                    employee_data = cursor_file201.fetchone()
                    if employee_data:
                        emp_name = f"{employee_data[0]}, {employee_data[1]} {employee_data[2]}"
                        sched_in = employee_data[3]
                        sched_out = employee_data[4]
                        schedule = f"{sched_in} - {sched_out}" if sched_in and sched_out else "N/A"
                        logging.error(
                            f"Found data for bioNum {bioNum}: {emp_name}, MachCode: {mach_code}, Schedule: {schedule}")
                    else:
                        logging.error(f"No data found for bioNum {bioNum}")
                        emp_name = "Unknown"
                        schedule = "N/A"
                except Exception as e:
                    logging.error(f"Error fetching employee data for bioNum {bioNum}: {e}")
                    emp_name = "Error"
                    mach_code = "Error"
                    schedule = "Error"

                if time_data[bioNum]["Check_In"] or time_data[bioNum]["Check_Out"]:
                    row_position = self.TimeListTable.rowCount()
                    self.TimeListTable.insertRow(row_position)

                    def create_centered_item(text):
                        item = QTableWidgetItem(str(text))
                        item.setTextAlignment(Qt.AlignCenter)
                        return item

                    check_in_time = time_data[bioNum]["Check_In"][1] if time_data[bioNum]["Check_In"] else "Missing"
                    check_out_time = time_data[bioNum]["Check_Out"][1] if time_data[bioNum][
                        "Check_Out"] else "Missing"

                    self.TimeListTable.setItem(row_position, 0, create_centered_item(str(bioNum)))
                    self.TimeListTable.setItem(row_position, 1, create_centered_item(emp_name))
                    self.TimeListTable.setItem(row_position, 2, create_centered_item(str(trans_date)))
                    self.TimeListTable.setItem(row_position, 3, create_centered_item(mach_code))  # Set machCode
                    self.TimeListTable.setItem(row_position, 4, create_centered_item(check_in_time))
                    self.TimeListTable.setItem(row_position, 5, create_centered_item(check_out_time))
                    self.TimeListTable.setItem(row_position, 6, create_centered_item(schedule))

                    time_data[bioNum] = {"Check_In": None, "Check_Out": None}

            logging.info("Time list table populated successfully.")

        except Exception as e:
            logging.error(f"Error populating time list table: {e}")

        finally:
            self.original_data = self.get_table_data()
            cursor_list_log.close()
            cursor_file201.close()
            connection_list_log.close()
            connection_file201.close()

    @single_function_logger.log_function
    def createTimeSheet(self, checked=False):
        dataMerge = []

        for row in range(self.TimeListTable.rowCount()):
            # Fetch data from the table for each row
            bioNum = self.TimeListTable.item(row, 0).text()
            trans_date = self.TimeListTable.item(row, 2).text()
            check_in = self.TimeListTable.item(row, 4).text()
            check_out = self.TimeListTable.item(row, 5).text()

            # Calculate hours worked
            try:
                hoursWorked = self.getTotalHoursWorked(check_in, check_out)
            except AttributeError as e:
                logging.error(f"Error: {e} - Please make sure getTotalHoursWorked is defined.")
                hoursWorked = 'Unknown'

            workHours = 'N/A'
            difference = ''
            regularOT = ''
            specialOT = ''

            # Check the type of the date
            dateType = timekeepingFunction.getTypeOfDate(trans_date)
            if dateType == "Ordinary Day" and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    difference = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {bioNum}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Difference: {difference:.2f}")
                except ValueError:
                    logging.error(f"Error calculating difference for BioNum: {bioNum}")
                    difference = 'N/A'

            if dateType == "Regular Holiday" and hoursWorked != 'Unknown':
                try:
                    regularOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {bioNum}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Regular Holiday Overtime: {regularOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating regular holiday for BioNum: {bioNum}")
                    regularOT = 'N/A'

            if dateType == "Special Holiday" and hoursWorked != 'Unknown':
                try:
                    specialOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {bioNum}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Special Holiday Overtime: {specialOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating special holiday for BioNum: {bioNum}")
                    specialOT = 'N/A'

            # Append the data to the dataMerge list
            dataMerge.append({
                'BioNum': bioNum,
                'Check_In': check_in,
                'Check_Out': check_out,
                'Hours_Worked': str(hoursWorked),
                'Difference': difference,
                'Regular Holiday Overtime': regularOT,
                'Special Holiday Overtime': specialOT
            })

        for data in dataMerge:
            logging.info(data)

        # Now pass the dataMerge into the TimeSheet dialog
        try:
            dialog = TimeSheet(dataMerge)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error opening TimeSheet dialog: {e}")

    def get_table_data(self):
        data = []
        for row in range(self.TimeListTable.rowCount()):
            row_data = []
            for col in range(self.TimeListTable.columnCount()):
                item = self.TimeListTable.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def search_bioNum(self):
        search_text = self.searchBioNum.text().strip().lower()

        if not search_text:
            # Restore original data
            self.populate_table_with_data(self.original_data)
            return

        filtered_data = [row for row in self.original_data if search_text in row[0].lower()]
        self.populate_table_with_data(filtered_data)

    def populate_table_with_data(self, data):
        self.TimeListTable.setRowCount(0)
        for row_data in data:
            row_position = self.TimeListTable.rowCount()
            self.TimeListTable.insertRow(row_position)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.TimeListTable.setItem(row_position, col, item)

    @single_function_logger.log_function
    def getTotalHoursWorked(self, time_start, time_end):
        if time_start == 'Missing' or time_end == 'Missing':
            return "Unknown"

        timeIn = QTime.fromString(time_start, "HH:mm:ss")
        timeOut = QTime.fromString(time_end, "HH:mm:ss")

        # Converting time into seconds
        seconds_in_a_day = 24 * 60 * 60
        time_in_seconds = (timeIn.hour() * 3600) + (timeIn.minute() * 60) + timeIn.second()
        time_out_seconds = (timeOut.hour() * 3600) + (timeOut.minute() * 60) + timeOut.second()

        # Handle crossing midnight
        if time_out_seconds < time_in_seconds:
            time_out_seconds += seconds_in_a_day

        time_difference = time_out_seconds - time_in_seconds

        # Convert the difference to hours
        work_duration_in_hours = time_difference / 3600

        return round(work_duration_in_hours, 2)

    @single_function_logger.log_function
    def CheckSched(self, checked=False):
        selected_row = self.TimeListTable.currentRow()

        if selected_row != -1:
            bioNum = self.TimeListTable.item(selected_row, 0).text() if self.TimeListTable.item(selected_row,
                                                                                                0) else "N/A"
            empName = self.TimeListTable.item(selected_row, 1).text() if self.TimeListTable.item(selected_row,
                                                                                                 1) else "N/A"
            trans_date = self.TimeListTable.item(selected_row, 2).text() if self.TimeListTable.item(selected_row,
                                                                                                    2) else "N/A"
            checkIn = self.TimeListTable.item(selected_row, 4).text() if self.TimeListTable.item(selected_row,
                                                                                                 4) else "Missing"
            checkOut = self.TimeListTable.item(selected_row, 5).text() if self.TimeListTable.item(selected_row,
                                                                                                  5) else "Missing"
            sched = self.TimeListTable.item(selected_row, 6).text() if self.TimeListTable.item(selected_row,
                                                                                               6) else "N/A"

            total_hours = self.getTotalHoursWorked(checkIn, checkOut)

            empNum = "DefaultEmpNum"
            data = [empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours]

            if len(data) == 8:
                dialog = chkSched(data)
                dialog.exec_()
            else:
                QMessageBox.warning(
                    self,
                    "Data Error",
                    "Insufficient data to process. Please check the row data."
                )
        else:
            QMessageBox.warning(
                self,
                "No Row Selected",
                "Please select a row from the table first!"
            )

    @single_function_logger.log_function
    def apply_filter(self, filter_values):
        try:
            filtered = []
            for row in self.original_data:
                check_in_time = row[2]  # assuming index 2 for check-in
                check_out_time = row[3]  # assuming index 3 for check-out

                if filter_values['show_missing']:
                    if check_in_time == 'Missing' or check_out_time == 'Missing':
                        filtered.append(row)
                else:
                    if check_in_time != 'Missing' and check_out_time != 'Missing':
                        # apply other filter logic...
                        filtered.append(row)

            self.filtered_data = filtered
            self.populate_table_with_data(self.filtered_data)
        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while applying the filter: {str(e)}")

    @single_function_logger.log_function
    def filterModal(self, checked=False):
        try:
            filter_dialog = filter(self)
            if filter_dialog.exec_() == QDialog.Accepted:
                filter_values = filter_dialog.get_filter_values()
                logging.info(f"Filter values received in timecard: {filter_values}")
                self.apply_filter(filter_values)
        except Exception as e:
            logging.error(f"Error in filterModal: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    @single_function_logger.log_function
    def clear_filter(self):
        self.filtered_data = self.original_data.copy()
        logging.info("Filter cleared, reset to original data")
        self.populateTimeList(self.filtered_data)

    @single_function_logger.log_function
    def show_missing_entries(self):
        missing_entries = [row for row in self.original_data if
                           row['Check_In'] == 'Missing' or row['Check_Out'] == 'Missing']
        self.filtered_data = missing_entries
        logging.info(f"Showing {len(missing_entries)} missing entries")
        self.populateTimeList(self.filtered_data)
