from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import globalFunction, timekeepingFunction, ValidInteger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class schedule(QDialog):
    def __init__(self, data):
        super(schedule, self).__init__()
        self.setFixedSize(1442, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\Schedule.ui")
        loadUi(ui_file, self)

        self.data = data
        self.populate_employee_table()
        self.clear_employee_details()

        validator = ValidInteger()
        validator.set_validators(self.txtVacn, self.txtSick, self.txtEmerLeave,
                                 self.txtMagda, self.txtMaternity,
                                 self.txtPaternity, self.txtSole, self.txtSpecialy, self.txtSIL)

        # Connect signals
        self.employeeTable.itemSelectionChanged.connect(self.on_row_selected)
        self.searchBioNum.textChanged.connect(self.search_employee)

    def populate_employee_table(self):
        try:
            connection = create_connection('NTP_EMP_LIST')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return

            cursor = connection.cursor()
            query = """
            SELECT empid, CONCAT(surname, ', ', firstname, ' ', mi) as full_name 
            FROM emp_info 
            ORDER BY full_name
            """
            cursor.execute(query)
            employees = cursor.fetchall()

            self.employeeTable.setRowCount(len(employees))
            self.employeeTable.setColumnCount(2)
            self.employeeTable.setHorizontalHeaderLabels(["BioNum", "EmpName"])

            for row, employee in enumerate(employees):
                self.employeeTable.setItem(row, 0, QTableWidgetItem(str(employee[0])))
                self.employeeTable.setItem(row, 1, QTableWidgetItem(employee[1]))

            self.employeeTable.resizeColumnsToContents()

        except Error as e:
            QMessageBox.critical(self, "Error", f"An error occurred while fetching employee data: {e}")
            logging.error(f"Error fetching employee data: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def on_row_selected(self):
        selected_items = self.employeeTable.selectedItems()
        if selected_items:
            bionum = selected_items[0].text()
            empname = selected_items[1].text()
            self.populate_schedule_with_data([None, bionum, empname, None, None, None, None])
        else:
            self.clear_employee_details()

    def clear_employee_details(self):
        self.empNameTxt.clear()
        self.bioNumTxt.clear()
        self.dateOfWork.setDate(QDate.currentDate())
        self.timeInTxt.clear()
        self.timeOutTxt.clear()
        self.hoursWorkedTxt.clear()
        self.holidayNameTxt.clear()
        self.typeOfDayCb.setCurrentIndex(0)

    def search_employee(self, text):
        for row in range(self.employeeTable.rowCount()):
            bionum = self.employeeTable.item(row, 0).text()
            if text.lower() in bionum.lower():
                self.employeeTable.showRow(row)
            else:
                self.employeeTable.hideRow(row)

    def populate_schedule_with_data(self, data):
        (empNum, bioNum, empName, trans_date, checkIn, checkOut, total_hours) = data

        self.empNameTxt.setText(empName)
        self.bioNumTxt.setText(bioNum)
        if trans_date:
            self.dateOfWork.setDate(QDate.fromString(trans_date, "yyyy-MM-dd"))
        self.timeInTxt.setText(checkIn if checkIn else "")
        self.timeOutTxt.setText(checkOut if checkOut else "")
        self.hoursWorkedTxt.setText(str(total_hours) if total_hours else "")
        if trans_date:
            self.holidayNameTxt.setText(self.getHolidayName(trans_date))
            self.typeOfDayCb.setCurrentText(timekeepingFunction.getTypeOfDate(trans_date))
        else:
            self.holidayNameTxt.clear()
            self.typeOfDayCb.setCurrentIndex(0)

    def getHolidayName(self, trans_date):
        try:
            connection = create_connection('NTP_HOLIDAY_LIST')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return None
            cursor = connection.cursor()

            # Fetches the holiday name in type_of_dates database
            fetch_holiday_name = "SELECT holidayName FROM type_of_dates WHERE holidayDate = %s"
            cursor.execute(fetch_holiday_name, (trans_date, ))

            result = cursor.fetchone()
            if result:
                return result[0]

            return "Normal Day"

        except Error as e:
            QMessageBox.critical(self, "Error",
                                 "An error occurred while fetching the holiday information. Please try again.")
            logging.error(f"Error fetching holiday name: {e}")
            return
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")