import sys
import os

from MainFrame.TimeKeeping.timeSheet.timeSheet import TimeSheet

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

        # Initialize the year combo box
        self.populate_year_combo_box()

        # Connect signals to slots
        self.yearCC.currentTextChanged.connect(self.populate_date_combo_boxes)
        self.dateFromCC.currentTextChanged.connect(self.populate_time_list_table)
        self.dateToCC.currentTextChanged.connect(self.populate_time_list_table)
        self.timeSheetButton.clicked.connect(self.createTimeSheet)

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
            print(f"Error populating year combo box: {e}")

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
            print(f"Error populating date combo boxes: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_time_list_table(self):
        """Populate the time list table with check-in and check-out times."""
        selected_year_month = self.yearCC.currentText()
        from_day = self.dateFromCC.currentText()
        to_day = self.dateToCC.currentText()

        if not selected_year_month or not from_day or not to_day:
            return

        # Construct full dates
        from_date = f"{selected_year_month}_{from_day.zfill(2)}"
        to_date = f"{selected_year_month}_{to_day.zfill(2)}"

        # Construct table name
        table_name = f"table_{selected_year_month}"

        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # Check if the table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                print(f"Error: Table does not exist: {table_name}")
                return

            # Query data within the selected date range
            query = f"""
                SELECT bioNum, date, time, sched
                FROM `{table_name}`
                WHERE DATE_FORMAT(date, '%Y_%m_%d') BETWEEN '{from_date}' AND '{to_date}'
                ORDER BY bioNum, date, time
            """
            cursor.execute(query)
            records = cursor.fetchall()

            # Clear existing rows in the table
            self.TimeListTable.setRowCount(0)
            time_data = {}

            for bio_num, trans_date, trans_time, sched in records:
                if bio_num not in time_data:
                    time_data[bio_num] = {"Check_In": None, "Check_Out": None}

                if sched == "Time IN":
                    time_data[bio_num]["Check_In"] = (trans_date, str(trans_time))
                elif sched == "Time OUT":
                    time_data[bio_num]["Check_Out"] = (trans_date, str(trans_time))

                # Add row to table if both check-in and check-out times are present
                if time_data[bio_num]["Check_In"] or time_data[bio_num]["Check_Out"]:
                    row_position = self.TimeListTable.rowCount()
                    self.TimeListTable.insertRow(row_position)

                    # Create QTableWidgetItem and set text alignment to center
                    def create_centered_item(text):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        return item

                    check_in_time = time_data[bio_num]["Check_In"][1] if time_data[bio_num]["Check_In"] else "Missing"
                    check_out_time = time_data[bio_num]["Check_Out"][1] if time_data[bio_num][
                        "Check_Out"] else "Missing"

                    self.TimeListTable.setItem(row_position, 0, create_centered_item(str(bio_num)))
                    self.TimeListTable.setItem(row_position, 2, create_centered_item(str(trans_date)))
                    self.TimeListTable.setItem(row_position, 4, create_centered_item(check_in_time))
                    self.TimeListTable.setItem(row_position, 5, create_centered_item(check_out_time))

                    # Reset data for this bio_num
                    time_data[bio_num] = {"Check_In": None, "Check_Out": None}

        except Exception as e:
            print(f"Error populating time list table: {e}")

        finally:
            cursor.close()
            connection.close()

    @single_function_logger.log_function
    def createTimeSheet(self, checked=False):
        dataMerge = []

        for row in range(self.TimeListTable.rowCount()):
            # Fetch data from the table for each row
            bio_num = self.TimeListTable.item(row, 0).text()
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
                    logging.info(f"BioNum: {bio_num}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Difference: {difference:.2f}")
                except ValueError:
                    logging.error(f"Error calculating difference for BioNum: {bio_num}")
                    difference = 'N/A'

            if dateType == "Regular Holiday" and hoursWorked != 'Unknown':
                try:
                    regularOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {bio_num}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Regular Holiday Overtime: {regularOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating regular holiday for BioNum: {bio_num}")
                    regularOT = 'N/A'

            if dateType == "Special Holiday" and hoursWorked != 'Unknown':
                try:
                    specialOT = round(hoursWorked - workHours, 2)
                    logging.info(f"BioNum: {bio_num}, Work Hours: {workHours:.2f}, "
                                 f"Hours Worked: {hoursWorked:.2f}, Special Holiday Overtime: {specialOT:.2f}")
                except ValueError:
                    logging.error(f"Error calculating special holiday for BioNum: {bio_num}")
                    specialOT = 'N/A'

            # Append the data to the dataMerge list
            dataMerge.append({
                'BioNum': bio_num,
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
