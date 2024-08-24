import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.TimeKeeping.schedValidator.checkSched import chkSched
from MainFrame.TimeKeeping.timeCardMaker.filter import FilterDialog
from MainFrame.TimeKeeping.timeSheet.timeSheet import TimeSheet
from MainFrame.systemFunctions import timekeepingFunction, globalFunction

import re


class populateList:
    def __init__(self, parent):
        self.parent = parent

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
            self.parent.yearCC.addItems(sorted(year_months))
            self.parent.yearCC.setCurrentIndex(-1)

        except Exception as e:
            logging.error(f"Error populating year combo box: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_date_combo_boxes(self):
        """Populate the date combo boxes based on the selected year-month."""
        selected_year_month = self.parent.yearCC.currentText()
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
            self.parent.dateFromCC.clear()  # Clear previous items
            self.parent.dateToCC.clear()  # Clear previous items
            self.parent.dateFromCC.addItems(sorted(days_from_set))
            self.parent.dateToCC.addItems(sorted(days_to_set))

        except Exception as e:
            logging.error(f"Error populating date combo boxes: {e}")

        finally:
            cursor.close()
            connection.close()

    def populateCostCenterBox(self):
        """Populate the costCenterBox with values from the pos_descr column in the emp_posnsched table."""
        connection = create_connection('FILE201')
        if not connection:
            logging.error("Error: Unable to connect to FILE201 database.")
            return

        try:
            cursor = connection.cursor()

            # Query to fetch distinct dept_name values
            query = "SELECT DISTINCT dept_name FROM emp_posnsched ORDER BY dept_name"
            cursor.execute(query)

            # Fetch all results
            pos_descr_list = cursor.fetchall()

            # Clear the current items in the QComboBox
            self.parent.costCenterBox.clear()
            self.parent.costCenterBox.setCurrentIndex(-1)

            # Add items to the QComboBox
            for pos_descr in pos_descr_list:
                self.parent.costCenterBox.addItem(pos_descr[0])  # pos_descr is a tuple, so get the first element

            logging.info("Cost center box populated successfully.")

        except Exception as e:
            logging.error(f"Error populating cost center box: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_time_list_table(self, checked=False):
        """Populate the time list table with check-in and check-out times, machCode, and employee data."""
        selected_year_month = self.parent.yearCC.currentText()
        from_day = self.parent.dateFromCC.currentText()
        to_day = self.parent.dateToCC.currentText()

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

            self.parent.TimeListTable.setRowCount(0)
            time_data = []
            for bioNum, trans_date, time_in, time_out, mach_code in records:
                if bioNum not in time_data:
                    time_data.append(
                        {"bioNum": bioNum, "trans_date": trans_date, "time_in": time_in, "time_out": time_out,
                         "mach_code": mach_code})

                # Query to get employee information and schedule from FILE201
                employee_query = (
                    "SELECT pi.surname, pi.firstname, pi.mi, ps.sched_in, ps.sched_out "
                    "FROM emp_info pi "
                    "JOIN emp_posnsched ps ON pi.empid = ps.empid "
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

                if time_data:
                    row_position = self.parent.TimeListTable.rowCount()
                    self.parent.TimeListTable.insertRow(row_position)

                    def create_centered_item(text):
                        item = QTableWidgetItem(str(text))
                        item.setTextAlignment(Qt.AlignCenter)
                        return item

                    check_in_time = time_data[0]["time_in"] if time_data[0]["time_in"] else "Missing"
                    check_out_time = time_data[0]["time_out"] if time_data[0]["time_out"] else "Missing"

                    self.parent.TimeListTable.setItem(row_position, 0,
                                                      create_centered_item(str(time_data[0]["bioNum"])))
                    self.parent.TimeListTable.setItem(row_position, 1, create_centered_item(emp_name))
                    self.parent.TimeListTable.setItem(row_position, 2,
                                                      create_centered_item(str(time_data[0]["trans_date"])))
                    self.parent.TimeListTable.setItem(row_position, 3,
                                                      create_centered_item(str(time_data[0]["mach_code"])))
                    self.parent.TimeListTable.setItem(row_position, 4, create_centered_item(str(check_in_time)))
                    self.parent.TimeListTable.setItem(row_position, 5, create_centered_item(str(check_out_time)))
                    self.parent.TimeListTable.setItem(row_position, 6, create_centered_item(schedule))

            # Assign data to original_data
            self.parent.original_data = time_data

        except Exception as e:
            logging.error(f"Error populating time list table: {e}")

        finally:
            cursor_list_log.close()
            cursor_file201.close()
            connection_list_log.close()
            connection_file201.close()


class buttonTimecardFunction:
    def __init__(self, parent):
        self.parent = parent  # Reference to the main UI class

    def updateSchedule(self):
        # Access UI elements through self.parent
        selectedCostCenterFrom = self.parent.costCenterFrom.currentText()
        selectedCostCenterBox = self.parent.costCenterBox.currentText()
        selectedCostCenterTo = self.parent.costCenterTo.currentText()

        if not selectedCostCenterFrom or not selectedCostCenterBox or not selectedCostCenterTo:
            print("Please select all required fields.")
            return

        # Print the selected data
        print(f"Selected Cost Center From: {selectedCostCenterFrom}")
        print(f"Selected Cost Center To: {selectedCostCenterTo}")
        print(f"Selected Cost Center Box: {selectedCostCenterBox}")

        # Show caution message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Caution")
        msg.setText(f"CAUTION! It will change the schedule of {selectedCostCenterBox}. Do you want to continue?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec_()

        # Proceed only if the user clicks "Yes"
        if result == QMessageBox.Yes:
            # Database connection (ensure create_connection is defined/imported)
            connection = create_connection('FILE201')
            if not connection:
                logging.error("Error: Unable to connect to FILE201 database.")
                return

            try:
                cursor = connection.cursor()

                # Query to fetch existing schedule
                query = """
                    SELECT sched_in, sched_out
                    FROM emp_posnsched
                    WHERE dept_name = %s
                """
                cursor.execute(query, (selectedCostCenterBox,))
                result = cursor.fetchone()

                if result:
                    sched_in, sched_out = result
                    print(f"Existing Scheduled In: {sched_in}")
                    print(f"Existing Scheduled Out: {sched_out}")

                    # Update sched_in and sched_out based on selectedCostCenterFrom and selectedCostCenterTo
                    update_query = """
                        UPDATE emp_posnsched
                        SET sched_in = %s, sched_out = %s
                        WHERE dept_name = %s
                    """
                    cursor.execute(update_query, (selectedCostCenterFrom, selectedCostCenterTo, selectedCostCenterBox))
                    connection.commit()

                    print(f"Updated Scheduled In to: {selectedCostCenterFrom}")
                    print(f"Updated Scheduled Out to: {selectedCostCenterTo}")
                else:
                    print("No schedule found for the selected Cost Center Box.")

            except Exception as e:
                logging.error(f"An error occurred while updating schedule: {e}")
            finally:
                connection.close()
        else:
            print("Update canceled by user.")

    def export_to_excel(self, checked=False):
        # Access original_data through self.parent
        if hasattr(self.parent, 'original_data') and self.parent.original_data:
            try:
                if isinstance(self.parent.original_data, pd.DataFrame):
                    data_to_export = self.parent.original_data
                else:
                    data_to_export = pd.DataFrame(self.parent.original_data)

                # Use self.parent as the parent for QFileDialog
                file_dialog = QFileDialog(self.parent, "Save File", "", "Excel Files (*.xlsx)")
                if file_dialog.exec_():
                    file_name = file_dialog.selectedFiles()[0]
                    if not file_name.endswith('.xlsx'):
                        file_name += '.xlsx'

                    # Ensure globalFunction.export_to_excel is defined/imported
                    globalFunction.export_to_excel(data_to_export, file_name)

                    QMessageBox.information(self.parent, "Export Successful",
                                            f"Data has been successfully exported to {file_name}")
                else:
                    QMessageBox.warning(self.parent, "Export Cancelled", "Export was cancelled by the user.")

            except Exception as e:
                QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {e}")
                logging.error(f"Export error: {e}")
        else:
            QMessageBox.warning(self.parent, "No Data", "There is no data to export.")

    def createTimeSheet(self, checked=False):
        # Access TimeListTable through self.parent
        if self.parent.TimeListTable.rowCount() == 0:
            QMessageBox.warning(
                self.parent,
                "No rows available",
                "No rows detected, please make sure that there are data available within the table first in order to proceed!"
            )
            return

        dataMerge = []

        # Fetch date values from ComboBoxes through self.parent
        date_from = self.parent.dateFromCC.currentText()
        date_to = self.parent.dateToCC.currentText()

        for row in range(self.parent.TimeListTable.rowCount()):
            # Fetch data from the table for each row
            bioNum = self.parent.TimeListTable.item(row, 0).text()
            emp_name = self.parent.TimeListTable.item(row, 1).text()
            trans_date = self.parent.TimeListTable.item(row, 2).text()
            mach_code = self.parent.TimeListTable.item(row, 3).text()
            check_in = self.parent.TimeListTable.item(row, 4).text()
            check_out = self.parent.TimeListTable.item(row, 5).text()

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

            # Check the type of the date (ensure timekeepingFunction.getTypeOfDate is defined/imported)
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
                'Employee': emp_name,
                'Check_In': check_in,
                'Check_Out': check_out,
                'Hours_Worked': str(hoursWorked),
                'Difference': difference,
                'Regular Holiday Overtime': regularOT,
                'Special Holiday Overtime': specialOT
            })

        for data in dataMerge:
            logging.info(data)

        # Pass date and mach_code along with the dataMerge to TimeSheet dialog
        try:
            dialog = TimeSheet(dataMerge, date_from, date_to, mach_code)  # Ensure TimeSheet is defined/imported
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error opening TimeSheet dialog: {e}")

    def CheckSched(self, checked=False):
        # Access TimeListTable through self.parent
        selected_row = self.parent.TimeListTable.currentRow()

        if selected_row != -1:
            bioNum = self.parent.TimeListTable.item(selected_row, 0).text() if self.parent.TimeListTable.item(
                selected_row, 0) else "N/A"
            empName = self.parent.TimeListTable.item(selected_row, 1).text() if self.parent.TimeListTable.item(
                selected_row, 1) else "N/A"
            trans_date = self.parent.TimeListTable.item(selected_row, 2).text() if self.parent.TimeListTable.item(
                selected_row, 2) else "N/A"
            checkIn = self.parent.TimeListTable.item(selected_row, 4).text() if self.parent.TimeListTable.item(
                selected_row, 4) else "Missing"
            checkOut = self.parent.TimeListTable.item(selected_row, 5).text() if self.parent.TimeListTable.item(
                selected_row, 5) else "Missing"
            sched = self.parent.TimeListTable.item(selected_row, 6).text() if self.parent.TimeListTable.item(
                selected_row, 6) else "N/A"

            total_hours = self.getTotalHoursWorked(checkIn, checkOut)

            empNum = "DefaultEmpNum"
            data = [empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours]

            if len(data) == 8:
                dialog = chkSched(data)  # Ensure chkSched is defined/imported
                dialog.exec_()
            else:
                QMessageBox.warning(
                    self.parent,
                    "Data Error",
                    "Insufficient data to process. Please check the row data."
                )
        else:
            QMessageBox.warning(
                self.parent,
                "No Row Selected",
                "Please select a row from the table first!"
            )

    def on_row_double_clicked(self, index):
        try:
            logging.debug("Row double-clicked in TimeListTable.")
            selected_row = index.row()

            if selected_row != -1:
                bioNum = self.parent.TimeListTable.item(selected_row, 0).text() if self.parent.TimeListTable.item(
                    selected_row, 0) else "N/A"
                empName = self.parent.TimeListTable.item(selected_row, 1).text() if self.parent.TimeListTable.item(
                    selected_row, 1) else "N/A"
                trans_date = self.parent.TimeListTable.item(selected_row, 2).text() if self.parent.TimeListTable.item(
                    selected_row, 2) else "N/A"
                checkIn = self.parent.TimeListTable.item(selected_row, 4).text() if self.parent.TimeListTable.item(
                    selected_row, 4) else "Missing"
                checkOut = self.parent.TimeListTable.item(selected_row, 5).text() if self.parent.TimeListTable.item(
                    selected_row, 5) else "Missing"
                sched = self.parent.TimeListTable.item(selected_row, 6).text() if self.parent.TimeListTable.item(
                    selected_row, 6) else "N/A"

                total_hours = self.getTotalHoursWorked(checkIn, checkOut)

                empNum = "DefaultEmpNum"  # Replace with the actual employee number if available
                data = [empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours]

                if len(data) == 8:
                    logging.debug(f"Data is valid. Opening chkSched dialog with data: {data}")
                    dialog = chkSched(data)  # Ensure chkSched is defined/imported
                    dialog.exec_()
                else:
                    logging.warning("Insufficient data to process. Please check the row data.")
                    QMessageBox.warning(
                        self.parent,
                        "Data Error",
                        "Insufficient data to process. Please check the row data."
                    )
            else:
                logging.warning("No row selected in TimeListTable.")
                QMessageBox.warning(
                    self.parent,
                    "No Row Selected",
                    "Please select a row from the table first!"
                )
        except Exception as e:
            logging.error(f"Error in on_row_double_clicked: {e}", exc_info=True)

    def getTotalHoursWorked(self, time_start, time_end):
        # Ensure time is in correct format
        try:
            timeIn = datetime.strptime(time_start, "%H:%M:%S")
            timeOut = datetime.strptime(time_end, "%H:%M:%S")
        except ValueError as e:
            logging.error(f"Time format error: {e}")
            return "Unknown"

        # Converting time into seconds
        seconds_in_a_day = 24 * 60 * 60
        time_in_seconds = (timeIn.hour * 3600) + (timeIn.minute * 60) + timeIn.second
        time_out_seconds = (timeOut.hour * 3600) + (timeOut.minute * 60) + timeOut.second

        # Handle crossing midnight
        if time_out_seconds < time_in_seconds:
            time_out_seconds += seconds_in_a_day

        time_difference = time_out_seconds - time_in_seconds
        work_duration_in_hours = time_difference / 3600
        return round(work_duration_in_hours, 2)


class searchBioNum:
    def __init__(self, parent):
        self.parent = parent

    def search_bioNum(self):
        search_text = self.parent.searchBioNum.text().strip().lower()
        logging.info(f"Search text: '{search_text}'")

        logging.info(f"Original data before filtering: {self.parent.original_data}")

        if not search_text:
            logging.info("Search text is empty. Restoring original data.")
            self.populate_table_with_data(self.parent.original_data)
            return

        filtered_data = [row for row in self.parent.original_data if search_text in str(row[0]).lower()]
        logging.info(f"Filtered data contains {len(filtered_data)} rows.")

        if not filtered_data:
            logging.warning("No matching records found.")

        self.populate_table_with_data(filtered_data)

    def populate_table_with_data(self, data):
        try:
            self.parent.TimeListTable.setRowCount(0)  # Clear existing rows
            logging.info("Populating table with data.")

            for row_data in data:
                row_position = self.parent.TimeListTable.rowCount()
                self.parent.TimeListTable.insertRow(row_position)

                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.parent.TimeListTable.setItem(row_position, col, item)

            logging.info(f"Table populated with {len(data)} rows.")
        except Exception as e:
            logging.error(f"Error populating table with data: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while populating the table: {str(e)}")


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\filter.ui")
        loadUi(ui_file, self)

        self.cmbCheckIn = self.findChild(QComboBox, 'cmbCheckIn')
        self.cmbCheckOut = self.findChild(QComboBox, 'cmbCheckOut')
        self.btnOK = self.findChild(QPushButton, 'btnOK')
        self.btnClear = self.findChild(QPushButton, 'btnClear')
        self.btnMissing = self.findChild(QPushButton, 'btnMissing')

        if not all([self.cmbCheckIn, self.cmbCheckOut, self.btnOK, self.btnClear, self.btnMissing]):
            raise ValueError("One or more UI elements not found")

        self.btnOK.clicked.connect(self.accept)
        self.btnClear.clicked.connect(self.clear_filter)
        self.btnMissing.clicked.connect(self.show_missing)

        for combo in [self.cmbCheckIn, self.cmbCheckOut]:
            if combo.itemText(0) != "AM/PM":
                combo.insertItem(0, "AM/PM")

        self.selected_check_in = "AM/PM"
        self.selected_check_out = "AM/PM"
        self.parent = parent

    def clear_filter(self, checked=False):
        try:
            if self.parent:
                logging.info("Clearing filter...")
                logging.info(f"Original data before clearing: {self.parent.original_data}")
                self.parent.filtered_data = self.parent.original_data.copy()
                self.populate_table_with_data(self.parent.filtered_data)
                logging.info("Filter cleared and table restored to original state.")
        except Exception as e:
            logging.error(f"Error in clear_filter: {str(e)}")
            logging.error(traceback.format_exc())
        self.accept()

    def show_missing(self, checked=False):
        try:
            filter_values = {
                'check_in_ampm': "AM/PM",
                'check_out_ampm': "AM/PM",
                'show_missing': True
            }
            logging.info("Showing missing entries with filter values: %s", filter_values)
            self.apply_filter(filter_values)
        except Exception as e:
            logging.error(f"Error in show_missing: {str(e)}")
            logging.error(traceback.format_exc())
        self.accept()

    def get_filter_values(self):
        values = {
            'check_in_ampm': self.cmbCheckIn.currentText(),
            'check_out_ampm': self.cmbCheckOut.currentText(),
            'show_missing': False
        }
        logging.info(f"Filter values: {values}")
        return values

    def apply_filter(self, filter_values):
        try:
            logging.info(f"Applying filter with values: {filter_values}")

            filtered = []
            logging.info(f"Original data contains {len(self.parent.original_data)} rows.")

            for row in self.parent.original_data:
                check_in_time = row[4]
                check_out_time = row[5]

                logging.debug(f"Row check-in time: {check_in_time}, check-out time: {check_out_time}")

                if filter_values['show_missing']:
                    if check_in_time == 'Missing' or check_out_time == 'Missing':
                        filtered.append(row)
                        logging.debug(f"Row with bioNum {row[0]} added due to missing time.")
                        continue

                if check_in_time != 'Missing' and check_out_time != 'Missing':
                    try:
                        check_in_hour = int(check_in_time.split(':')[0])
                        check_out_hour = int(check_out_time.split(':')[0])
                    except ValueError as ve:
                        logging.error(f"Error parsing time: {ve}")
                        continue

                    if filter_values['check_in_ampm'] == 'AM' and not (0 <= check_in_hour < 12):
                        logging.debug(f"Row with bioNum {row[0]} excluded based on AM/PM filter.")
                        continue
                    if filter_values['check_in_ampm'] == 'PM' and not (12 <= check_in_hour < 24):
                        logging.debug(f"Row with bioNum {row[0]} excluded based on AM/PM filter.")
                        continue
                    if filter_values['check_out_ampm'] == 'AM' and not (0 <= check_out_hour < 12):
                        logging.debug(f"Row with bioNum {row[0]} excluded based on AM/PM filter.")
                        continue
                    if filter_values['check_out_ampm'] == 'PM' and not (12 <= check_out_hour < 24):
                        logging.debug(f"Row with bioNum {row[0]} excluded based on AM/PM filter.")
                        continue

                    filtered.append(row)
                    logging.debug(f"Row with bioNum {row[0]} added to filtered list.")

            logging.info(f"Filtered data contains {len(filtered)} rows.")
            self.parent.filtered_data = filtered
            self.populate_table_with_data(self.parent.filtered_data)

        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while applying the filter: {str(e)}")

    def populate_table_with_data(self, data):
        try:
            self.parent.TimeListTable.setRowCount(0)
            logging.info("Populating table with data.")

            for row_data in data:
                row_position = self.parent.TimeListTable.rowCount()
                self.parent.TimeListTable.insertRow(row_position)

                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.parent.TimeListTable.setItem(row_position, col, item)

            logging.info(f"Table populated with {len(data)} rows.")
        except Exception as e:
            logging.error(f"Error populating table with data: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while populating the table: {str(e)}")

    def filterModal(self):
        try:
            if self.exec_() == QDialog.Accepted:
                filter_values = self.get_filter_values()
                logging.info(f"Filter values obtained from dialog: {filter_values}")
                self.apply_filter(filter_values)
            else:
                logging.info("Filter dialog was canceled by the user.")

        except Exception as e:
            logging.error(f"Error in filterModal: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while opening the filter dialog: {str(e)}")

    def closeEvent(self, event):
        self.selected_check_in = self.cmbCheckIn.currentText()
        self.selected_check_out = self.cmbCheckOut.currentText()
        super().closeEvent(event)
