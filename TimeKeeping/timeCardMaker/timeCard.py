import traceback
import logging

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QPushButton, QMessageBox
from PyQt5.uic import loadUi

from TimeKeeping.schedValidator.checkSched import chkSched
from TimeKeeping.timeSheet.timeSheet import TimeSheet
from TimeKeeping.timeCardMaker.filter import filter
from MainFrame.systemFunctions import globalFunction, timekeepingFunction, single_function_logger


class timecard(QDialog):
    def __init__(self, filtered_data, from_date_str, to_date_str):
        super().__init__()
        self.setFixedSize(1345, 665)
        ui_file = globalFunction.resource_path("TimeKeeping\\timeCardMaker\\timecard.ui")
        loadUi(ui_file, self)

        self.original_data = filtered_data.copy()
        self.filtered_data = filtered_data

        self.timekeepfunction = timekeepingFunction()

        # Make the column headers fixed size
        self.TimeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeListTable.horizontalHeader().setStretchLastSection(True)

        self.lblFrom = self.findChild(QLabel, 'lblFrom')
        self.lblTo = self.findChild(QLabel, 'lblTo')
        self.lblFrom.setText(from_date_str)
        self.lblTo.setText(to_date_str)

        self.timeSheetButton = self.findChild(QPushButton, 'btnTimeSheet')
        self.timeSheetButton.clicked.connect(self.createTimeSheet)

        # Add search functionality
        self.searchBioNum = self.findChild(QLineEdit, 'txtSearch')
        self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))

        self.btnCheckSched = self.findChild(QPushButton, 'btnCheckSched')
        self.btnCheckSched.clicked.connect(self.CheckSched)

        self.btnFilter = self.findChild(QPushButton, 'btnFilter')
        self.btnFilter.clicked.connect(self.filterModal)

        self.populateTimeList(self.filtered_data)

    @single_function_logger.log_function
    def populateTimeList(self, data):
        self.TimeListTable.clearContents()
        self.TimeListTable.setRowCount(len(data))
        logging.info(f"Populating table with {len(data)} rows")

        for row_index, row_data in enumerate(data):
            for col_index, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.TimeListTable.setItem(row_index, col_index, item)

        logging.info("Table population complete")

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
            empNum = self.TimeListTable.item(selected_row, 0).text()
            bioNum = self.TimeListTable.item(selected_row, 1).text()
            empName = self.TimeListTable.item(selected_row, 2).text()
            trans_date = self.TimeListTable.item(selected_row, 3).text()
            checkIn = self.TimeListTable.item(selected_row, 5).text()
            checkOut = self.TimeListTable.item(selected_row, 6).text()
            sched = self.TimeListTable.item(selected_row, 7).text()

            total_hours = self.getTotalHoursWorked(checkIn, checkOut)

            data = (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours)

            dialog = chkSched(data)
            dialog.exec_()
        else:
            QMessageBox.warning(
                self,
                "No Row Selected",
                "Please select a row from the table first!"
            )

    @single_function_logger.log_function
    def createTimeSheet(self):
        dataMerge = []
        for item in self.filtered_data:
            checkIn = item['Check_In']
            checkOut = item['Check_Out']
            trans_date = item['Trans_Date']
            workHours = item['workHours'] if 'workHours' in item else 'N/A'
            hoursWorked = self.getTotalHoursWorked(checkIn, checkOut)
            difference = ''  # Initialize as empty string
            regularOT = ''
            specialOT = ''

            # Check the type of the date
            dateType = self.timekeepfunction.getTypeOfDate(trans_date)
            if dateType == "Ordinary Day" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    difference = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Difference: {difference:.2f}")
                except ValueError:
                    logging.error(f"Error calculating difference for BioNum: {item['BioNum']}")
                    difference = 'N/A'

            if dateType == "Regular Holiday" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    regularOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Regular Holiday Overtime: {regularOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating regular holiday for BioNum: {item['BioNum']}")
                    regularOT = 'N/A'

            if dateType == "Special Holiday" and workHours != 'N/A' and hoursWorked != 'Unknown':
                try:
                    workHours = round(float(workHours), 2)
                    hoursWorked = round(float(hoursWorked), 2)
                    specialOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {item['BioNum']}, EmpName: {item['EmpName']}, "
                                 f"Work Hours: {workHours:.2f}, Hours Worked: {hoursWorked:.2f}, "
                                 f"Special Holiday Overtime: {specialOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating special holiday for BioNum: {item['BioNum']}")
                    specialOT = 'N/A'

            dataMerge.append({
                'BioNum': item['BioNum'],
                'EmpName': item['EmpName'],
                'MachCode': item['MachCode'],
                'Check_In': checkIn,
                'Check_Out': checkOut,
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

    @single_function_logger.log_function
    def apply_filter(self, filter_values):
        try:
            logging.info(f"Filter values received: {filter_values}")
            logging.info(f"Total rows in original data: {len(self.original_data)}")
            logging.info(f"Show missing flag: {filter_values['show_missing']}")

            filtered = []
            for row in self.original_data:
                check_in_time = row['Check_In']
                check_out_time = row['Check_Out']

                logging.info(f"Processing row: Check-in {check_in_time}, Check-out {check_out_time}")

                if filter_values['show_missing']:
                    if check_in_time == 'Missing' or check_out_time == 'Missing':
                        filtered.append(row)
                        logging.info("Added missing entry to filtered data")
                else:
                    if check_in_time != 'Missing' and check_out_time != 'Missing':
                        check_in_hour = int(check_in_time.split(':')[0])
                        check_out_hour = int(check_out_time.split(':')[0])

                        check_in_matches = (filter_values['check_in_ampm'] == "AM/PM") or \
                                           (filter_values['check_in_ampm'] == "AM" and check_in_hour < 12) or \
                                           (filter_values['check_in_ampm'] == "PM" and check_in_hour >= 12)

                        check_out_matches = (filter_values['check_out_ampm'] == "AM/PM") or \
                                            (filter_values['check_out_ampm'] == "AM" and check_out_hour < 12) or \
                                            (filter_values['check_out_ampm'] == "PM" and check_out_hour >= 12)

                        if check_in_matches and check_out_matches:
                            filtered.append(row)

            self.filtered_data = filtered
            logging.info(f"Filtered data count: {len(filtered)}")
            logging.info(f"First few filtered entries: {filtered[:5]}")
            self.populateTimeList(self.filtered_data)
        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}")
            logging.error(traceback.format_exc())
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