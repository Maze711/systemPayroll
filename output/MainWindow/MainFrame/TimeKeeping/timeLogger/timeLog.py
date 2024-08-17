import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.TimeKeeping.timeCardMaker.timeCard import timecard
from MainFrame.TimeKeeping.paytimeSheet.paytimeSheet import PaytimeSheet
from MainFrame.systemFunctions import globalFunction, timekeepingFunction, single_function_logger


class timelogger(QMainWindow):
    def __init__(self, content):
        super().__init__()
        self.setFixedSize(1180, 665)
        #loadUi(os.path.join(os.path.dirname(__file__), 'timeLog.ui'), self)
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\timeLog.ui"))
        loadUi(ui_file, self)

        self.content = content

        self.fromCalendar = self.findChild(QDateEdit, 'dateStart')
        self.toCalendar = self.findChild(QDateEdit, 'dateEnd')
        self.filterButton = self.findChild(QPushButton, 'btnFilter')
        self.createCard = self.findChild(QPushButton, 'btnCard')
        self.employeeListTable = self.findChild(QTableWidget, 'employeeListTable')

        self.fromCalendar.setDate(QDate.currentDate())
        self.toCalendar.setDate(QDate.currentDate())

        self.filterButton.clicked.connect(self.showFilteredData)
        self.createCard.clicked.connect(self.openTimeCard)
        # self.createCard.clicked.connect(self.createPaytimeSheet)
        self.createCard.setEnabled(False)

        self.processContent()
        self.loadData()

        # Make the column headers fixed size
        self.employeeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.employeeListTable.horizontalHeader().setStretchLastSection(True)

    # @single_function_logger.log_function
    def processContent(self):

        rows = self.content.strip().split('\n')
        self.data = []
        for row in rows:
            columns = row.split('\t')
            if len(columns) < 6:
                logging.error(f"Row has missing columns: {row}")
                continue

            try:
                bio_no, date_time, mach_code, code_1, code_2, code_3 = columns[:6]
                trans_date, time_value = date_time.split(' ')
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
                'sched': sched  # Store sched instead of code_1, code_2, code_3
            })


#     @single_function_logger.log_function
    def loadData(self):

        try:
            self.populateTable(self.data)
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    @single_function_logger.log_function
    def showFilteredData(self, checked=False):

        from_date = self.fromCalendar.date()
        to_date = self.toCalendar.date()
        from_date_str = from_date.toString("yyyy-MM-dd")
        to_date_str = to_date.toString("yyyy-MM-dd")

        filtered_data = [
            row for row in self.data
            if from_date_str <= row['trans_date'] <= to_date_str
        ]

        self.populateTable(filtered_data)
        self.createCard.setEnabled(bool(filtered_data))

    @single_function_logger.log_function
    def populateTable(self, data):

        self.employeeListTable.setRowCount(len(data))
        self.employeeListTable.clearContents()

        for row_position, row in enumerate(data):
            items = [
                QTableWidgetItem(row['bio_no']),
                QTableWidgetItem(row['trans_date']),
                QTableWidgetItem(row['time']),
                QTableWidgetItem(row['mach_code']),
                QTableWidgetItem(row['sched'])
            ]
            for item in items:
                item.setTextAlignment(Qt.AlignCenter)

            for column, item in enumerate(items):
                self.employeeListTable.setItem(row_position, column, item)


    @single_function_logger.log_function
    def openTimeCard(self, checked=False):
        filtered_data, from_date, to_date = timekeepingFunction.appendDate(self.fromCalendar, self.toCalendar, self.data)

        combined_data = {}
        connection = create_connection('FILE201')
        if connection:
            try:
                cursor = connection.cursor()
                for row in filtered_data:
                    bio_no = row['bio_no']
                    trans_date = row['trans_date']
                    mach_code = row['mach_code']
                    if row['sched'] == 'Time IN':
                        time_in = row['time']
                        time_out = None
                    elif row['sched'] == 'Time OUT':
                        time_out = row['time']
                        time_in = None
                    else:
                        time_in = None
                        time_out = None

                    query = f"SELECT ep.sched_in, ep.sched_out, pi.surname, pi.firstname, pi.mi " \
                            f"FROM emp_info pi " \
                            f"JOIN emp_posnsched ep ON pi.empl_id = ep.empl_id " \
                            f"WHERE pi.empl_id = '{bio_no}'"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result:
                        sched_in, sched_out, surname, firstname, mi = result
                        emp_name = f"{surname}, {firstname} {mi}"
                        if sched_in and sched_out:
                            workHours = self.calculateHoursWorked(sched_in, sched_out)
                        else:
                            workHours = "Unknown"
                        sche_name = f"{sched_in} - {sched_out}"

                    else:
                        emp_name = "Unknown"
                        sche_name = "Unknown"
                        workHours = "Unknown"
                        logging.warning(f"No data found for Employee ID: {bio_no}")

                    # Create a key based on bio_no and trans_date to handle unique entries per date
                    key = (bio_no, trans_date)
                    if key not in combined_data:
                        combined_data[key] = {
                            'EmpNumber': '',  # Replace with actual EmpNumber if available
                            'BioNum': bio_no,
                            'EmpName': emp_name,
                            'Trans_Date': trans_date,
                            'MachCode': mach_code,
                            'Check_In': time_in if time_in else 'Missing',
                            'Check_Out': time_out if time_out else 'Missing',
                            'Schedule': sche_name,  # Assign formatted schedule name
                            'workHours': workHours  # Assign calculated hours worked
                        }
                    else:
                        if time_in:
                            combined_data[key]['Check_In'] = time_in
                        if time_out:
                            combined_data[key]['Check_Out'] = time_out

                final_data = list(combined_data.values())
                self.timecard_window = timecard(final_data, from_date, to_date)
                self.timecard_window.show()
                self.hide()

            except Exception as e:
                logging.error(f"Error fetching or processing data: {e}")
            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if 'connection' in locals() and connection is not None:
                    connection.close()
        else:
            logging.error("Failed to establish database connection")

    @single_function_logger.log_function
    def calculateHoursWorked(self, sched_in, sched_out):
        try:
            sched_in_time = datetime.strptime(sched_in, "%I:%M %p")  # Example: '6:00 am'
            sched_out_time = datetime.strptime(sched_out, "%I:%M %p")  # Example: '2:00 pm'

            diff = sched_out_time - sched_in_time
            hours_worked = diff.total_seconds() / 3600

            return round(hours_worked, 2)

        except ValueError:
            return "Invalid Time Format"

    @single_function_logger.log_function
    def createPaytimeSheet(self):
        filtered_data, from_date, to_date = timekeepingFunction.appendDate(self.fromCalendar, self.toCalendar, self.data)

        data = []
        num_of_present_days = {}
        processed_bio_num = set()
        num_of_present_holidays = {}
        holiday_dates = self.fetch_all_holidays()

        for row in filtered_data:
            bio_num = row['bio_no']
            trans_date = row['trans_date']

            if bio_num not in num_of_present_days:
                num_of_present_days[bio_num] = set()

            num_of_present_days[bio_num].add(trans_date)

        logging.info(f"Number of days: \n{num_of_present_days}")

        num_of_present_holidays = {
            bio_num: len(dates.intersection(holiday_dates))
            for bio_num, dates in num_of_present_days.items()
        }

        num_of_present_days = {bio_num: len(dates) for bio_num, dates in num_of_present_days.items()}

        connection = create_connection('FILE201')
        if connection:
            try:
                cursor = connection.cursor()
                for bio_num in num_of_present_days:
                    if bio_num in processed_bio_num:
                        continue
                    else:
                        processed_bio_num.add(bio_num)

                    query = f"SELECT pi.empl_id, pi.surname, pi.firstname, pi.mi " \
                            f"FROM emp_info pi " \
                            f"WHERE pi.empl_id = '{bio_num}'"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result:
                        empl_id, surname, firstname, mi = result
                        emp_name = f"{surname}, {firstname} {mi}"
                    else:
                        empl_id = "Unknown"
                        emp_name = "Unknown"
                        logging.warning(f"No data found for Employee ID: {bio_num}")

                    data.append({
                        'EmpNo': empl_id,
                        'BioNum': bio_num,
                        'EmpName': emp_name,
                        'Present Days': num_of_present_days[bio_num],
                        'Present Holidays': num_of_present_holidays[bio_num]
                    })

            except Error as e:
                logging.error(f"Error fetching employee details: {e}")

            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if 'connection' in locals() and connection is not None:
                    connection.close()

        # Sort data by EmpName in alphabetical order
        data.sort(key=lambda x: x['EmpName'])

        logging.info(f"Data to be passed: \n{data}")

        self.window = PaytimeSheet(data, from_date, to_date)
        self.window.show()
        self.close()

    @single_function_logger.log_function
    def fetch_all_holidays(self):
        connection = create_connection('TIMEKEEPING')
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT date FROM type_of_dates"
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    # Formats the tuple result to string with the format 'year-month-day'
                    formatted_dates = [date[0].strftime('%Y-%m-%d') for date in result]
                    return formatted_dates

            except Error as e:
                logging.error(f"Error fetching all holidays: {e}")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()