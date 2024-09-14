import sys
import os
import logging

from MainFrame.notificationMaker import notificationLoader

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

    def import_dat_file(self):
        try:
            # Open file dialog to select a .DAT file
            fileName, _ = QFileDialog.getOpenFileName(self.parent, "Open DAT File", "", "DAT Files (*.DAT)")
            if fileName:
                logging.info(f"Selected file: {fileName}")

                notification_dialog = notificationLoader(fileName)
                notification_dialog.importSuccessful.connect(self.update_after_import)
                notification_dialog.exec_()
            else:
                QMessageBox.information(self.parent, "No File Selected", "Please select a DAT file to import.")
        except Exception as e:
            # Log any errors
            logging.error(f"Error in import_dat_file: {e}")
            QMessageBox.critical(self.parent, "File Import Error", f"An error occurred: {e}")

    def update_after_import(self):
        # Update the necessary UI elements
        self.populate_year_combo_box()
        self.populate_date_combo_boxes()

    def populate_year_combo_box(self):
        """Populate the year combo box with available year-month combinations from table names."""
        connection = create_connection('NTP_LOG_IMPORTS')
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
            self.parent.yearCC.clear()  # Clear previous items
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

        connection = create_connection('NTP_LOG_IMPORTS')
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
            days_set = set()

            cursor.execute(f"""
                SELECT DISTINCT DATE_FORMAT(date, '%d') AS day
                FROM {table_name}
            """)
            days = cursor.fetchall()

            for (day,) in days:
                days_set.add(day)

            # Update date combo boxes
            self.parent.dateFromCC.clear()  # Clear previous items
            self.parent.dateToCC.clear()  # Clear previous items
            self.parent.dateFromCC.addItems(sorted(days_set))
            self.parent.dateToCC.addItems(sorted(days_set))

        except Exception as e:
            logging.error(f"Error populating date combo boxes: {e}")

        finally:
            cursor.close()
            connection.close()

    def populateCostCenterBox(self):
        """Populate the costCenterBox with values from the pos_descr column in the emp_posnsched table."""
        connection = create_connection('NTP_EMP_LIST')
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

        from_date = f"{selected_year_month}-{from_day.zfill(2)}"
        to_date = f"{selected_year_month}-{to_day.zfill(2)}"
        table_name = f"table_{selected_year_month.replace('-', '_')}"

        connection_list_log = create_connection('NTP_LOG_IMPORTS')
        connection_file201 = create_connection('NTP_EMP_LIST')

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

            # Fetch time records
            query_list_log = f"""
                SELECT bioNum, date, time_in, time_out, machCode
                FROM `{table_name}`
                WHERE date BETWEEN '{from_date}' AND '{to_date}'
                ORDER BY bioNum, date, time_in
            """
            cursor_list_log.execute(query_list_log)
            records = cursor_list_log.fetchall()

            # Fetch employee data
            bio_nums = set(record[0] for record in records)
            emp_query = f"""
                SELECT pi.empid, pi.surname, pi.firstname, pi.mi, ps.sched_in, ps.sched_out
                FROM emp_info pi
                JOIN emp_posnsched ps ON pi.empid = ps.empid
                WHERE pi.empid IN ({', '.join(map(str, bio_nums))})
            """
            cursor_file201.execute(emp_query)
            emp_records = cursor_file201.fetchall()
            emp_data_cache = {record[0]: record[1:] for record in emp_records}

            # Prepare time data
            time_data = []
            for bioNum, trans_date, time_in, time_out, mach_code in records:
                check_in_time = time_in or "00:00:00"
                check_out_time = time_out or "00:00:00"
                employee_data = emp_data_cache.get(bioNum, ("Unknown", "Unknown", "Unknown", "00:00:00", "00:00:00"))
                emp_name = f"{employee_data[0]}, {employee_data[1]} {employee_data[2]}"
                sched_in = employee_data[3] or "00:00:00"
                sched_out = employee_data[4] or "00:00:00"

                time_data.append([
                    bioNum, emp_name, trans_date, mach_code, check_in_time, check_out_time, sched_in, sched_out
                ])

            # Update table
            self.parent.TimeListTable.setUpdatesEnabled(False)
            self.populate_table_with_data(time_data)
            self.parent.TimeListTable.setUpdatesEnabled(True)
            self.parent.original_data = time_data

        except Exception as e:
            logging.error(f"Error populating time list table: {e}")

        finally:
            cursor_list_log.close()
            cursor_file201.close()
            connection_list_log.close()
            connection_file201.close()

    def populate_table_with_data(self, data):
        """Populate the table with employee time data, using ComboBoxes for sched_in and sched_out."""
        try:
            logging.info("Populating table with data.")

            def create_time_combobox(initial_value):
                combo = QComboBox()
                for hour in range(24):
                    for minute in range(0, 60, 15):
                        time_str = f"{hour:02d}:{minute:02d}"
                        combo.addItem(time_str)
                combo.setCurrentText(initial_value)
                return combo

            self.parent.TimeListTable.setUpdatesEnabled(False)
            self.parent.TimeListTable.setRowCount(len(data))

            items = []
            widgets = []

            for row_position, row_data in enumerate(data):
                row_items = []
                for col, value in enumerate(row_data):
                    if col in [6, 7]:
                        sched_time = str(value)
                        if len(sched_time) == 8:
                            sched_time = sched_time[:5]
                        combo = create_time_combobox(sched_time)
                        widgets.append((row_position, col, combo))
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        row_items.append(item)
                items.append(row_items)

            for row_position, row_items in enumerate(items):
                for col, item in enumerate(row_items):
                    self.parent.TimeListTable.setItem(row_position, col, item)
            for row_position, col, widget in widgets:
                self.parent.TimeListTable.setCellWidget(row_position, col, widget)

            header = self.parent.TimeListTable.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Fixed)

            logging.info(f"Table populated with {len(data)} rows.")

        except Exception as e:
            logging.error(f"Error populating table with data: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while populating the table: {str(e)}")

        finally:
            self.parent.TimeListTable.setUpdatesEnabled(True)


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
            connection = create_connection('NTP_EMP_LIST')
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
        if self.parent.TimeListTable.rowCount() == 0:
            QMessageBox.warning(
                self.parent,
                "No rows available",
                "No rows detected, please make sure that there is data available within the table first in order to proceed!"
            )
            return

        aggregated_data = {}
        date_from = self.parent.dateFromCC.currentText()
        date_to = self.parent.dateToCC.currentText()

        for row in range(self.parent.TimeListTable.rowCount()):
            bioNum = self.parent.TimeListTable.item(row, 0).text()
            emp_name = self.parent.TimeListTable.item(row, 1).text()
            trans_date = self.parent.TimeListTable.item(row, 2).text()
            mach_code = self.parent.TimeListTable.item(row, 3).text()
            check_in = self.parent.TimeListTable.item(row, 4).text()
            check_out = self.parent.TimeListTable.item(row, 5).text()

            try:
                hours_worked, nd_hours, ndot_hours = self.getTotalHoursWorked(check_in, check_out)
                formatted_hours = f"{hours_worked:.2f}"
                formatted_nd_hours = f"{nd_hours:.2f}"
                formatted_ndot_hours = f"{ndot_hours:.2f}"
            except AttributeError as e:
                logging.error(f"Error: {e} - Please make sure getTotalHoursWorked is defined.")
                formatted_hours = "0.00"
                formatted_nd_hours = "0.00"
                formatted_ndot_hours = "0.00"

            if bioNum not in aggregated_data:
                aggregated_data[bioNum] = {
                    'BioNum': bioNum,
                    'EmpNumber': bioNum,
                    'Employee': emp_name,
                    'Total_Hours_Worked': 0.0,
                    'Night_Differential': 0.0,
                    'Night_Differential_OT': 0.0,
                    'Days_Work': 0,
                    'Days_Present': 0
                }

            aggregated_data[bioNum]['Total_Hours_Worked'] += float(formatted_hours)
            aggregated_data[bioNum]['Night_Differential'] += float(formatted_nd_hours)
            aggregated_data[bioNum]['Night_Differential_OT'] += float(formatted_ndot_hours)
            aggregated_data[bioNum]['Days_Work'] += 1

        dataMerge = list(aggregated_data.values())

        for data in dataMerge:
            data['Total_Hours_Worked'] = f"{data['Total_Hours_Worked']:.2f}"
            data['Night_Differential'] = f"{data['Night_Differential']:.2f}"
            data['Night_Differential_OT'] = f"{data['Night_Differential_OT']:.2f}"
            logging.info(data)

        try:
            dialog = TimeSheet(dataMerge, date_from, date_to, mach_code)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error opening TimeSheet dialog: {e}")

    def getTotalHoursWorked(self, time_start, time_end):
        # Define ND and NDO times
        nd_start = datetime.strptime("22:00:00", "%H:%M:%S").time()
        nd_end = datetime.strptime("06:00:00", "%H:%M:%S").time()
        ndot_start = datetime.strptime("02:00:00", "%H:%M:%S").time()
        ndot_end = datetime.strptime("06:00:00", "%H:%M:%S").time()

        # Parse times
        time_in = datetime.strptime(time_start, "%H:%M:%S")
        time_out = datetime.strptime(time_end, "%H:%M:%S")

        # Handle overnight shifts
        if time_out <= time_in:
            time_out += timedelta(days=1)

        # Calculate total hours worked
        total_hours = (time_out - time_in).total_seconds() / 3600

        # Calculate ND and NDO hours
        nd_hours = 0
        ndot_hours = 0
        current_time = time_in
        while current_time < time_out:
            if nd_start <= current_time.time() or current_time.time() < nd_end:
                nd_hours += 1
            if ndot_start <= current_time.time() < ndot_end:
                ndot_hours += 1
            current_time += timedelta(hours=1)

        nd_hours /= 60  # Convert minutes to hours
        ndot_hours /= 60  # Convert minutes to hours

        return round(total_hours, 3), round(nd_hours, 3), round(ndot_hours, 3)

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


class searchBioNum:
    def __init__(self, parent):
        self.parent = parent
        self.populate_list_instance = populateList(self.parent)  # Create instance of populateList

    def search_bioNum(self):
        """Search for a specific bioNum and update the table with filtered data."""
        search_text = self.parent.searchBioNum.text().strip().lower()
        logging.info(f"Search text: '{search_text}'")

        if not hasattr(self.parent, 'original_data') or not isinstance(self.parent.original_data, list):
            logging.error("original_data is not properly initialized or is not a list.")
            QMessageBox.critical(self.parent, "Error", "Original data is not properly initialized.")
            return

        if not search_text:
            logging.info("Search text is empty. Restoring original data.")
            self.populate_list_instance.populate_table_with_data(self.parent.original_data)
            self.parent.TimeListTable.repaint()  # Force UI update
            return

        # Ensure original_data is a list of lists/tuples
        if not all(isinstance(row, (list, tuple)) for row in self.parent.original_data):
            logging.error("Original data is not in the expected format.")
            QMessageBox.critical(self.parent, "Error", "Original data format is incorrect.")
            return

        # Perform the search
        filtered_data = [row for row in self.parent.original_data if search_text in str(row[0]).lower()]
        logging.info(f"Filtered data contains {len(filtered_data)} rows.")

        if not filtered_data:
            logging.warning("No matching records found.")

        # Update the table with filtered data
        self.populate_list_instance.populate_table_with_data(filtered_data)
        self.parent.TimeListTable.repaint()  # Force UI update


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

        self.btnOK.clicked.connect(self.accept)
        self.btnClear.clicked.connect(self.clear_filter)
        self.btnMissing.clicked.connect(self.show_missing)

        for combo in [self.cmbCheckIn, self.cmbCheckOut]:
            if combo.itemText(0) != "AM/PM":
                combo.insertItem(0, "AM/PM")

        self.parent = parent

    def clear_filter(self, checked=False):
        try:
            if self.parent:
                logging.info("Clearing filter...")
                logging.info(f"Original data before clearing: {self.parent.original_data}")

                # Reset to original data
                self.parent.filtered_data = self.parent.original_data.copy()

                # Populate the table using the populate_time_list_table method
                self.parent.populateComboBox.populate_time_list_table(self.parent.filtered_data)
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
            for row in self.parent.original_data:
                check_in_time = row[4]
                check_out_time = row[5]

                # Filter logic for missing entries
                if filter_values['show_missing']:
                    if check_in_time == 'Missing' or check_out_time == 'Missing':
                        filtered.append(row)
                        continue

                # AM/PM filtering logic
                if check_in_time != 'Missing' and check_out_time != 'Missing':
                    check_in_hour = int(check_in_time.split(':')[0])
                    check_out_hour = int(check_out_time.split(':')[0])

                    if filter_values['check_in_ampm'] == 'AM' and not (0 <= check_in_hour < 12):
                        continue
                    if filter_values['check_in_ampm'] == 'PM' and not (12 <= check_in_hour < 24):
                        continue
                    if filter_values['check_out_ampm'] == 'AM' and not (0 <= check_out_hour < 12):
                        continue
                    if filter_values['check_out_ampm'] == 'PM' and not (12 <= check_out_hour < 24):
                        continue

                    filtered.append(row)

            logging.info(f"Filtered data contains {len(filtered)} rows.")
            self.parent.filtered_data = filtered

            # Update the table with filtered data
            self.parent.populateComboBox.populate_table_with_data(self.parent.filtered_data)

        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"An error occurred while applying the filter: {str(e)}")

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
