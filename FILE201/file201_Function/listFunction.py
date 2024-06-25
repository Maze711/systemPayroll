from PyQt5.QtCore import QTimer, QDate
from PyQt5.QtWidgets import QTableWidgetItem, QPlainTextEdit, QComboBox, QDateEdit, QLineEdit, QMessageBox
from time import *
import logging

from PyQt5.uic.properties import QtCore
from mysql.connector import Error

# Configure logging
logger = logging.getLogger(__name__)

from FILE201.Database_Connection.DBConnection import create_connection
from FILE201.Database_Connection.modalSQLQuery import executeSearchQuery
from FILE201.Other_Information.otherInformationModal import personalModal
from FILE201.Database_Connection.listSQLQuery import getAllFetchEmployees

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
        selected_row = self.main_window.employeeListTable.currentRow()
        if selected_row != -1:
            empID = self.main_window.employeeListTable.item(selected_row, 0).text()
            employee_data = self.fetch_employee_data(empID)
            if employee_data:
                modal = personalModal()
                self.populate_modal_with_employee_data(modal, employee_data)
                self.set_fields_non_editable(modal)
                modal.finished.connect(self.displayEmployees)
                modal.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a row from the table")
            msg.setWindowTitle("No Row Selected")
            msg.exec_()

    def set_fields_non_editable(self, modal):
        disableStyle = "background-color: lightgray; color: gray;"

        for widget in modal.findChildren(QLineEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disableStyle)

        for widget in modal.findChildren(QDateEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disableStyle)

        for widget in modal.findChildren(QComboBox):
            widget.setDisabled(True)
            widget.setStyleSheet(disableStyle)

        for widget in modal.findChildren(QPlainTextEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disableStyle)

    def fetch_employee_data(self, empID):
        query = """
            SELECT p.empID, p.lastName, p.firstName, p.middleName, p.street, p.barangay, p.city, p.province, p.zip, 
               p.phoneNum, p.height, p.weight, p.civilStatus, p.dateOfBirth, p.placeOfBirth, p.gender,
               f.fathersLastName, f.fathersFirstName, f.fathersMiddleName, f.mothersLastName, 
               f.mothersFirstName, f.mothersMiddleName, f.spouseLastName, f.spouseFirstName, 
               f.spouseMiddleName, f.beneficiaryLastName, f.beneficiaryFirstName, f.beneficiaryMiddleName, 
               f.dependentsName,
               i.sssNum, i.pagibigNum, i.philhealthNum, i.tinNum,
               w.fromDate, w.toDate, w.companyName, w.companyAdd, w.empPosition,
               e.techSkill, e.certificateSkill, e.validationDate, e.college, e.highSchool, e.elemSchool,
               e.collegeAdd, e.highschoolAdd, e.elemAdd, e.collegeCourse, e.highschoolStrand, e.collegeYear,
               e.highschoolYear, e.elemYear
               FROM personal_information p
               LEFT JOIN family_background f ON p.empID = f.empID
               LEFT JOIN list_of_id i ON p.empID = i.empID
               LEFT JOIN work_exp w ON p.empID = w.empID
               LEFT JOIN educ_information e ON p.empID = e.empID
               WHERE p.empID = %s
            """
        try:
            connection = create_connection()
            if connection is None:
                logger.error("Error: Could not establish database connection.")
                return None

            cursor = connection.cursor()
            cursor.execute(query, (empID,))
            result = cursor.fetchone()
            if result:
                return result  # Returns a tuple with all fetched columns
            return None

        except Error as e:
            logger.error(f"Error fetching employee data: {e}")
            return None

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logger.info("Database connection closed")

    def populate_modal_with_employee_data(self, modal, data):
        try:
            (empID, lastName, firstName, middleName, street, barangay, city, province, zip,
             phoneNum, height, weight, civilStatus, dateOfBirth, placeOfBirth, gender,
             fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, mothersFirstName, mothersMiddleName,
             spouseLastName, spouseFirstName, spouseMiddleName, beneficiaryLastName, beneficiaryFirstName,
             beneficiaryMiddleName, dependentsName,
             sss_num, pagibig_num, philhealth_num, tin_num,
             from_date, to_date, company_name, company_add, position,
             tech_skill, certificate_skill, validation_date, college, high_school, elem_school,
             college_add, highschool_add, elem_add, college_course, highschool_strand, college_year,
             highschool_year, elem_year) = data

            modal.lblTitle_2.setText(f"Name: {lastName} {firstName} {middleName}")
            modal.lblTitle_3.setText(str(empID))
            modal.txtLastName.setText(lastName)
            modal.txtFirstName.setText(firstName)
            modal.txtMiddleName.setText(middleName)
            modal.txtStreet.setText(street)
            modal.txtBarangay.setText(barangay)
            modal.txtCity.setText(city)
            modal.txtProvince.setText(province)
            modal.txtZip.setText(zip)
            modal.txtPhone.setText(phoneNum)
            modal.txtHeight.setText(str(height))
            modal.txtWeight.setText(str(weight))
            modal.cmbCivil.setCurrentText(civilStatus)
            modal.dtDateOfBirth.setDate(QDate.fromString(dateOfBirth, "MM-dd-yyyy"))
            modal.txtPlace.setText(placeOfBirth)
            modal.cmbGender.setCurrentText(gender)

            modal.txtFatherLast.setText(fathersLastName)
            modal.txtFatherFirst.setText(fathersFirstName)
            modal.txtFatherMiddle.setText(fathersMiddleName)
            modal.txtMotherLast.setText(mothersLastName)
            modal.txtMotherFirst.setText(mothersFirstName)
            modal.txtMotherMiddle.setText(mothersMiddleName)
            modal.txtSpouseLast.setText(spouseLastName)
            modal.txtSpouseFirst.setText(spouseFirstName)
            modal.txtSpouseMiddle.setText(spouseMiddleName)
            modal.txtBeneLast.setText(beneficiaryLastName)
            modal.txtBeneFirst.setText(beneficiaryFirstName)
            modal.txtBeneMiddle.setText(beneficiaryMiddleName)
            modal.txtDependent.setText(dependentsName)

            modal.sssTextEdit.setPlainText(sss_num)
            modal.pagibigTextEdit.setPlainText(pagibig_num)
            modal.philHealthTextEdit.setPlainText(philhealth_num)
            modal.tinTextEdit.setPlainText(tin_num)

            modal.dateStart_4.setDate(QDate.fromString(from_date, "MM-dd-yyyy"))
            modal.dateEnd_4.setDate(QDate.fromString(to_date, "MM-dd-yyyy"))
            modal.companyTextEdit_4.setPlainText(company_name)
            modal.addressTextEdit_4.setPlainText(company_add)
            modal.positionTextEdit_4.setPlainText(position)

            modal.techSkillTextEdit.setPlainText(tech_skill)
            modal.certiTextEdit1.setPlainText(certificate_skill)
            modal.validationDate1.setDate(QDate.fromString(validation_date, "MM-dd-yyyy"))

            modal.collegeTextEdit.setPlainText(college)
            modal.highTextEdit.setPlainText(high_school)
            modal.elemTextEdit.setPlainText(elem_school)

            modal.addressTextEdit.setPlainText(college_add)
            modal.addressTextEdit2.setPlainText(highschool_add)
            modal.addressTextEdit3.setPlainText(elem_add)

            modal.courseTextEdit.setPlainText(college_course)
            modal.courseTextEdit2.setPlainText(highschool_strand)

            modal.schoolYear.setDate(QDate.fromString(college_year, "MM-dd-yyyy"))
            modal.schoolYear2.setDate(QDate.fromString(highschool_year, "MM-dd-yyyy"))
            modal.schoolYear3.setDate(QDate.fromString(elem_year, "MM-dd-yyyy"))

        except Exception as e:
            logger.error(f"Error populating modal with employee data: {e}")
            print(f"Error: {e}")

    def open_otherInformationMODAL_add(self):
        modal = personalModal()
        modal.editBTN.setEnabled(False)
        modal.saveBTN.setEnabled(False)
        modal.revertBTN.setEnabled(False)
        modal.finished.connect(self.displayEmployees) # Updates the employeeListTable upon closing
        modal.exec_()

    def clearFunction(self):
        self.main_window.txtEmployeeID.clear()
        self.main_window.txtLastName.clear()
        self.main_window.txtFirstName.clear()
        self.main_window.txtMiddleName.clear()

    def searchEmployees(self):
        searchText = self.main_window.txtSearch.text()
        if searchText:
            query = f"SELECT * FROM personal_information WHERE empID LIKE '%{searchText}%' OR lastName LIKE '%{searchText}%' OR firstName LIKE '%{searchText}%'"
            self.main_window.functions.searchAndDisplay(query)
        else:
            self.main_window.functions.displayEmployees()