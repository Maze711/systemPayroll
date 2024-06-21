from FILE201.Database_Connection.listSQLQuery import getAllFetchEmployees
from PyQt5.QtWidgets import QTableWidgetItem
from time import *

class ListFunction:
    def __init__(self, main_window):
        self.main_window = main_window

    # Displays Current Date and Time
    def timeClock(self):
        time_format = strftime("%I:%M:%S %p")
        self.main_window.lblTime.setText(time_format)

        date_format = strftime("%A, %B %d, %Y")
        self.main_window.lblDate.setText(date_format)


    # Displays all employees in the table
    def displayEmployees(self):
        # Clears/Resets the rows in the table
        self.main_window.employeeListTable.setRowCount(0)

        employees = getAllFetchEmployees()

        if employees is None:
            print("There are no current employees")
            return

        for rowNum, eachRow in enumerate(employees):
            self.main_window.employeeListTable.insertRow(rowNum)
            for column, data in enumerate(eachRow):
                self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))


    # Retrieves selected row in the employeeListTable
    def getSelectedRow(self):
        selected_row = self.main_window.employeeListTable.currentRow()

        if selected_row != -1:
            empID = self.main_window.employeeListTable.item(selected_row, 0).text()
            lastName = self.main_window.employeeListTable.item(selected_row, 1).text()
            firstName = self.main_window.employeeListTable.item(selected_row, 2).text()
            middleName = self.main_window.employeeListTable.item(selected_row, 3).text()

        # Displays the data of selected row in the Employee Basic Info Frame
            self.main_window.txtEmployeeID.setText(empID)
            self.main_window.txtLastName.setText(lastName)
            self.main_window.txtFirstName.setText(firstName)
            self.main_window.txtMiddleName.setText(middleName)