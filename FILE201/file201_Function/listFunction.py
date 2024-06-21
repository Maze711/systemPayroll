from FILE201.Database_Connection.listSQLQuery import getAllFetchEmployees
from PyQt5.QtWidgets import QTableWidgetItem
from time import *

from FILE201.Database_Connection.modalSQLQuery import executeSearchQuery
from FILE201.Other_Information.otherInformationModal import personalModal


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

    def searchAndDisplay(self, query):
        self.main_window.employeeListTable.setRowCount(0)

        employees = executeSearchQuery(query)

        if employees is None:
            print("No employees match the search criteria")
            return

        for rowNum, eachRow in enumerate(employees):
            self.main_window.employeeListTable.insertRow(rowNum)
            for column, data in enumerate(eachRow):
                self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))

    def open_otherInformationMODAL_view(self):
        self.main_window.modal = personalModal()
        self.main_window.modal.show()

    def open_otherInformationMODAL_add(self):
        self.main_window.modal = personalModal()
        self.main_window.modal.editBTN.setEnabled(False)
        self.main_window.modal.saveBTN.setEnabled(False)
        self.main_window.modal.revertBTN.setEnabled(False)
        self.main_window.modal.show()

    def searchEmployees(self):
        searchText = self.main_window.txtSearch.text()
        if searchText:
            query = f"SELECT * FROM personal_information WHERE empID LIKE '%{searchText}%' OR lastName LIKE '%{searchText}%' OR firstName LIKE '%{searchText}%'"
            self.main_window.functions.searchAndDisplay(query)
        else:
            self.main_window.functions.displayEmployees()