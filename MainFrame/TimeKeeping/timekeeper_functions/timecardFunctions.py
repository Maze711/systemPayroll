import operator
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
        self.data_cache = {}
        self.cost_center_cache = None

    def import_dat_file(self):
        try:
            fileName, _ = QFileDialog.getOpenFileName(self.parent, "Open DAT File", "", "DAT Files (*.DAT)")
            if fileName:
                logging.info(f"Selected file: {fileName}")
                notification_dialog = notificationLoader(fileName)
                notification_dialog.importSuccessful.connect(self.update_after_import)
                notification_dialog.exec_()
            else:
                QMessageBox.information(self.parent, "No File Selected", "Please select a DAT file to import.")
        except Exception as e:
            logging.error(f"Error in import_dat_file: {e}")
            QMessageBox.critical(self.parent, "File Import Error", f"An error occurred: {e}")

    def update_after_import(self):
        self.populate_year_combo_box()
        self.populate_date_combo_boxes()

    def populate_year_combo_box(self):
        connection = create_connection('NTP_LOG_IMPORTS')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'table_%'")
            tables = cursor.fetchall()

            year_months = set()
            for (table_name,) in tables:
                match = re.search(r'table_(\d{4})_(\d{2})', table_name)
                if match:
                    year_months.add(f"{match.group(1)}_{match.group(2)}")

            self.parent.yearCC.clear()
            self.parent.yearCC.addItems(sorted(year_months, reverse=True))
            self.parent.yearCC.setCurrentIndex(-1)

        except Exception as e:
            logging.error(f"Error populating year combo box: {e}")
        finally:
            cursor.close()
            connection.close()

    def populate_date_combo_boxes(self):
        selected_year_month = self.parent.yearCC.currentText()
        if not selected_year_month:
            return

        if selected_year_month in self.data_cache:
            days = self.data_cache[selected_year_month]
        else:
            connection = create_connection('NTP_LOG_IMPORTS')
            if not connection:
                return

            try:
                cursor = connection.cursor()
                table_name = f"table_{selected_year_month}"
                cursor.execute(f"SELECT DISTINCT DATE_FORMAT(date, '%d') AS day FROM {table_name}")
                days = [day[0] for day in cursor.fetchall()]
                self.data_cache[selected_year_month] = days
            except Exception as e:
                logging.error(f"Error populating date combo boxes: {e}")
                return
            finally:
                cursor.close()
                connection.close()

        self.parent.dateFromCC.clear()
        self.parent.dateToCC.clear()
        self.parent.dateFromCC.addItems(sorted(days))
        self.parent.dateToCC.addItems(sorted(days))

    def populateCostCenterBox(self):
        """Populate the costCenterBox with values from the dept_name column in the emp_posnsched table."""
        if self.cost_center_cache is not None:
            # Use cached data if available
            self.parent.costCenterBox.clear()
            self.parent.costCenterBox.addItems(self.cost_center_cache)
            self.parent.costCenterBox.setCurrentIndex(-1)
            logging.info("Cost center box populated from cache.")
            return

        connection = create_connection('NTP_EMP_LIST')
        if not connection:
            logging.error("Error: Unable to connect to FILE201 database.")
            return

        try:
            cursor = connection.cursor()

            # Optimized query to fetch distinct dept_name values
            query = "SELECT DISTINCT dept_name FROM emp_posnsched ORDER BY dept_name"
            cursor.execute(query)

            # Fetch all results at once
            dept_names = [row[0] for row in cursor.fetchall()]

            # Cache the results
            self.cost_center_cache = dept_names

            # Clear the current items in the QComboBox
            self.parent.costCenterBox.clear()
            self.parent.costCenterBox.addItems(dept_names)
            self.parent.costCenterBox.setCurrentIndex(-1)

            logging.info("Cost center box populated successfully.")

        except Exception as e:
            logging.error(f"Error populating cost center box: {e}")

        finally:
            cursor.close()
            connection.close()

    def clear_cache(self):
        """Clear all cached data"""
        self.data_cache.clear()
        self.cost_center_cache = None
        logging.info("All caches cleared.")

    def populate_table_loader(self):
        if hasattr(self, 'TablePopulationLoader') and self.TablePopulationLoader.isVisible():
            return

        self.TablePopulationLoader = TablePopulationLoader(self.parent.original_data, self.parent)
        self.TablePopulationLoader.show()

    def populate_table_with_data(self, data):
        try:
            logging.info("Populating table with data.")
            self.parent.TimeListTable.setUpdatesEnabled(False)

            sorted_data = sorted(data, key=operator.itemgetter(1))

            self.parent.TimeListTable.setRowCount(len(sorted_data))

            for row_position, row_data in enumerate(sorted_data):
                for col, value in enumerate(row_data):
                    if col in [6, 7]:  # sched_in and sched_out columns
                        combo = QComboBox()
                        for hour in range(24):
                            for minute in range(0, 60, 15):
                                time_str = f"{hour:02d}:{minute:02d}:00"
                                combo.addItem(time_str)
                        combo.setCurrentText(str(value))
                        combo.setStyleSheet("QComboBox { qproperty-alignment: AlignCenter; }")
                        self.parent.TimeListTable.setCellWidget(row_position, col, combo)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.parent.TimeListTable.setItem(row_position, col, item)

            header = self.parent.TimeListTable.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Fixed)

            logging.info(f"Table populated with {len(sorted_data)} rows.")
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

        timesheet_data = []
        date_from = self.parent.dateFromCC.currentText()
        date_to = self.parent.dateToCC.currentText()

        for row in range(self.parent.TimeListTable.rowCount()):
            bioNum = self.parent.TimeListTable.item(row, 0).text()
            emp_name = self.parent.TimeListTable.item(row, 1).text()
            trans_date = self.parent.TimeListTable.item(row, 2).text()
            mach_code = self.parent.TimeListTable.item(row, 3).text()
            check_in = self.parent.TimeListTable.item(row, 4).text()
            check_out = self.parent.TimeListTable.item(row, 5).text()
            sched_in = self.parent.TimeListTable.cellWidget(row, 6).currentText()
            sched_out = self.parent.TimeListTable.cellWidget(row, 7).currentText()

            timesheet_data.append((bioNum, emp_name, trans_date, mach_code, check_in, check_out, sched_in, sched_out))

        results = self.process_timesheet(timesheet_data)

        # Aggregate the data by summing the total hours, ND, NDOT, and counting unique days
        total_hours_worked = 0
        total_nd = 0
        total_ndot = 0
        unique_dates = set()  # To track distinct workdays

        for result in results:
            total_hours_worked += result['total_hours']
            total_nd += result['nd_hours']
            total_ndot += result['ndot_hours']
            unique_dates.add(result['trans_date'])  # Ensure each date is only counted once

        # Prepare the merged data
        dataMerge = [{
            'BioNum': results[0]['bio_num'],  # Assuming one employee, as it's aggregated
            'EmpNumber': results[0]['bio_num'],
            'Employee': results[0]['emp_name'],
            'Total_Hours_Worked': f"{total_hours_worked:.2f}",
            'Night_Differential': f"{total_nd:.2f}",
            'Night_Differential_OT': f"{total_ndot:.2f}",
            'Days_Work': len(unique_dates),  # Count of distinct days
            'Days_Present': len(unique_dates)
        }]

        try:
            dialog = TimeSheet(dataMerge, date_from, date_to, mach_code)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error opening TimeSheet dialog: {e}")
            QMessageBox.warning(self.parent, "Dialog Error", f"Failed to open the TimeSheet dialog: {e}") 

    def calculate_nd_ndot(self, check_in, check_out, schedule_in, schedule_out):
        check_in = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
        check_out = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S")
        schedule_in = datetime.strptime(schedule_in, "%H:%M:%S").time()
        schedule_out = datetime.strptime(schedule_out, "%H:%M:%S").time()

        if check_out <= check_in:
            check_out += timedelta(days=1)

        nd_ranges = [
            (datetime.combine(check_in.date(), datetime.strptime("22:00:00", "%H:%M:%S").time()),
             datetime.combine(check_in.date(), datetime.strptime("23:59:59", "%H:%M:%S").time())),
            (datetime.combine(check_in.date(), datetime.strptime("00:00:00", "%H:%M:%S").time()),
             datetime.combine(check_in.date(), datetime.strptime("06:00:00", "%H:%M:%S").time()))
        ]
        ndot_range = (
            datetime.combine(check_in.date(), datetime.strptime("02:00:00", "%H:%M:%S").time()),
            datetime.combine(check_in.date(), datetime.strptime("06:00:00", "%H:%M:%S").time())
        )

        nd_minutes = 0
        ndot_minutes = 0
        current = check_in
        while current < check_out:
            next_minute = current + timedelta(minutes=1)

            for nd_start, nd_end in nd_ranges:
                if nd_start <= current < nd_end or nd_start <= next_minute < nd_end:
                    nd_minutes += 1
                    break

            if ndot_range[0] <= current < ndot_range[1] or ndot_range[0] <= next_minute < ndot_range[1]:
                ndot_minutes += 1

            current = next_minute

        return nd_minutes / 60, ndot_minutes / 60

    def process_timesheet(self, timesheet_data):
        results = []
        for entry in timesheet_data:
            bio_num, emp_name, trans_date, mach_code, check_in, check_out, sched_in, sched_out = entry

            check_in_datetime = f"{trans_date} {check_in}"
            check_out_datetime = f"{trans_date} {check_out}"

            if datetime.strptime(check_out, "%H:%M:%S") < datetime.strptime(check_in, "%H:%M:%S"):
                check_out_date = datetime.strptime(trans_date, "%Y-%m-%d") + timedelta(days=1)
                check_out_datetime = f"{check_out_date.strftime('%Y-%m-%d')} {check_out}"

            nd_hours, ndot_hours = self.calculate_nd_ndot(check_in_datetime, check_out_datetime, sched_in, sched_out)
            total_hours = (datetime.strptime(check_out_datetime, "%Y-%m-%d %H:%M:%S") -
                           datetime.strptime(check_in_datetime, "%Y-%m-%d %H:%M:%S")).total_seconds() / 3600

            sched_total_hours, sched_nd_hours, sched_ndot_hours = self.calculate_sched_combo_nd_ndot(sched_in,
                                                                                                     sched_out)

            results.append({
                'bio_num': bio_num,
                'emp_name': emp_name,
                'trans_date': trans_date,
                'check_in': check_in,
                'check_out': check_out,
                'total_hours': round(total_hours, 2),
                'nd_hours': round(nd_hours, 2),
                'ndot_hours': round(ndot_hours, 2),
                'sched_total_hours': sched_total_hours,
                'sched_nd_hours': sched_nd_hours,
                'sched_ndot_hours': sched_ndot_hours
            })
        return results

    def calculate_sched_combo_nd_ndot(self, sched_in, sched_out):
        time_in = datetime.strptime(sched_in, "%H:%M:%S")
        time_out = datetime.strptime(sched_out, "%H:%M:%S")

        if time_out <= time_in:
            time_out += timedelta(days=1)

        total_hours = (time_out - time_in).total_seconds() / 3600
        nd_hours, ndot_hours = self.calculate_nd_ndot(
            time_in.strftime("%Y-%m-%d %H:%M:%S"),
            time_out.strftime("%Y-%m-%d %H:%M:%S"),
            sched_in,
            sched_out
        )

        return round(total_hours, 3), round(nd_hours, 3), round(ndot_hours, 3)

    def getTotalHoursWorked(self, check_in, check_out):
        time_in = datetime.strptime(check_in, "%H:%M:%S")
        time_out = datetime.strptime(check_out, "%H:%M:%S")

        if time_out <= time_in:
            time_out += timedelta(days=1)

        total_hours = (time_out - time_in).total_seconds() / 3600
        nd_hours, ndot_hours = self.calculate_nd_ndot(
            time_in.strftime("%Y-%m-%d %H:%M:%S"),
            time_out.strftime("%Y-%m-%d %H:%M:%S"),
            time_in.strftime("%H:%M:%S"),
            time_out.strftime("%H:%M:%S")
        )

        return round(total_hours, 3), round(nd_hours, 3), round(ndot_hours, 3)

    def CheckSched(self, checked=False):
        selected_row = self.parent.TimeListTable.currentRow()

        if selected_row != -1:
            # Extract employee data from the selected row
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

            # Extract schedule times from comboBoxes
            sched_in_combo = self.parent.TimeListTable.cellWidget(selected_row, 6).currentText()
            sched_out_combo = self.parent.TimeListTable.cellWidget(selected_row, 7).currentText()

            total_hours, nd_hours, ndot_hours = self.calculate_sched_combo_nd_ndot(sched_in_combo, sched_out_combo)

            empNum = "DefaultEmpNum"
            data = [empNum, bioNum, empName, trans_date, checkIn, checkOut, sched_in_combo, sched_out_combo,
                    total_hours, nd_hours, ndot_hours]

            if len(data) == 11:
                dialog = chkSched(data)  # Assuming `chkSched` is a valid dialog class to show schedule info
                dialog.exec_()
            else:
                QMessageBox.warning(self.parent, "Data Error",
                                    "Insufficient data to process. Please check the row data.")
        else:
            QMessageBox.warning(self.parent, "No Row Selected", "Please select a row from the table first!")


class searchBioNum:
    def __init__(self, parent):
        self.parent = parent
        self.populate_list_instance = populateList(self.parent)

    def search_bioNum(self):
        search_text = self.parent.searchBioNum.text().strip().lower()
        logging.info(f"Search text: '{search_text}'")

        if not hasattr(self.parent, 'original_data') or not isinstance(self.parent.original_data, list):
            logging.error("original_data is not properly initialized or is not a list.")
            QMessageBox.critical(self.parent, "Error", "Original data is not properly initialized.")
            return

        if not search_text:
            logging.info("Search text is empty. Restoring original data.")
            self.populate_list_instance.populate_table_with_data(self.parent.original_data)
            return

        filtered_data = [row for row in self.parent.original_data if search_text in str(row[0]).lower()]
        logging.info(f"Filtered data contains {len(filtered_data)} rows.")

        self.populate_list_instance.populate_table_with_data(filtered_data)


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


class TablePopulationLoader(QDialog):
    """Displays a dialog with progress bar for visualization of populating table with data"""

    def __init__(self, data, timeCardWindow=None):
        super(TablePopulationLoader, self).__init__(timeCardWindow)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)
        self.setModal(True)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        try:

            self.data = data
            self.parent = timeCardWindow

            self.functions = populateList(self.parent)

            # Get UI elements
            self.progressBar = self.findChild(QProgressBar, 'progressBar')

            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)

            self.thread = QThread()
            self.worker = FetchDataToPopulateTableProcessor(self.parent, self.data)
            self.worker.moveToThread(self.thread)
            self.worker.progressChanged.connect(self.updateProgressBar)
            self.worker.finished.connect(self.fetchingDataFinished)
            self.worker.error.connect(self.fetchingDataError)
            self.thread.started.connect(self.worker.process_populate_time_list_table)
            self.thread.start()
        except Exception as e:
            print("Error Showing TablePopulationLoader: ", e)

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fetchingDataFinished(self, time_data):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        # Update table
        self.parent.TimeListTable.setUpdatesEnabled(False)
        self.functions.populate_table_with_data(time_data)
        self.parent.TimeListTable.setUpdatesEnabled(True)
        self.parent.original_data = time_data

        # Closes and reset the instance of dialog
        self.close()
        self.parent.TablePopulationLoader = None

    def fetchingDataError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.parent, "Populating Table with Data Error", error)

        # Closes and reset the instance of dialog
        self.close()
        self.parent.TablePopulationLoader = None


class FetchDataToPopulateTableProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, timeCardWindow, data):
        super().__init__()
        self.parent = timeCardWindow
        self.data = data

    def process_populate_time_list_table(self):
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
            self.error.emit("Failed to connect to database.")
            return

        try:
            cursor_list_log = connection_list_log.cursor()
            cursor_file201 = connection_file201.cursor()

            # Check if the table exists
            cursor_list_log.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor_list_log.fetchone():
                self.error.emit(f"Error: Table does not exist: {table_name}")
                return

            # Fetch time records (filtered by bioNum 7635)
            query_list_log = f"""
                   SELECT bioNum, date, time_in, time_out, machCode
                   FROM `{table_name}`
                   WHERE date BETWEEN '{from_date}' AND '{to_date}' AND bioNum = 7635
                   ORDER BY bioNum, date, time_in
               """
            cursor_list_log.execute(query_list_log)
            records = cursor_list_log.fetchall()

            # Fetch employee data (filtered by empid 7635)
            emp_query = """
                   SELECT pi.empid, pi.surname, pi.firstname, pi.mi, ps.sched_in, ps.sched_out
                   FROM emp_info pi
                   JOIN emp_posnsched ps ON pi.empid = ps.empid
                   WHERE pi.empid = 7635
               """
            cursor_file201.execute(emp_query)
            emp_records = cursor_file201.fetchall()
            emp_data_cache = {record[0]: record[1:] for record in emp_records}

            # Total records retrieved
            total_records = len(records)
            if total_records == 0:
                self.finished.emit([])  # No data to process
                return

            # Prepare time data
            time_data = []

            for i, (bioNum, trans_date, time_in, time_out, mach_code) in enumerate(records):
                check_in_time = time_in or "00:00:00"
                check_out_time = time_out or "00:00:00"
                employee_data = emp_data_cache.get(bioNum, ("Unknown", "Unknown", "Unknown", "00:00:00", "00:00:00"))
                emp_name = f"{employee_data[0]}, {employee_data[1]} {employee_data[2]}"
                sched_in = employee_data[3] or "00:00:00"
                sched_out = employee_data[4] or "00:00:00"

                time_data.append([
                    bioNum, emp_name, trans_date, mach_code, check_in_time, check_out_time, sched_in, sched_out
                ])

                # Navigates the current progress
                progress = int(((i + 1) / total_records) * 100)
                self.progressChanged.emit(progress)
                QThread.msleep(1)

            self.finished.emit(time_data)

        except Exception as e:
            print(f"Error populating time list table: {e}")
            self.error.emit(f"Error populating time list table: {e}")

        finally:
            cursor_list_log.close()
            cursor_file201.close()
            connection_list_log.close()
            connection_file201.close()

