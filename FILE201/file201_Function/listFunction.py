from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.modalSQLQuery import executeQuery
from FILE201.Other_Information.otherInformationModal import personalModal

from MainFrame.systemFunctions import single_function_logger


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

        # Select only the required columns and order by surname
        query = "SELECT empl_id, surname, firstname, mi FROM emp_info ORDER BY surname"
        employees = executeQuery(query)

        if employees is None:
            print("There are no current employees")
            return

        for rowNum, eachRow in enumerate(employees):
            self.main_window.employeeListTable.insertRow(rowNum)
            # Assuming eachRow contains (empl_id, surname, firstname, mi)
            for column, data in enumerate(eachRow):
                self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))

    # Retrieves selected row in the employeeListTable
    def getSelectedRow(self):
        selected_row = self.main_window.employeeListTable.currentRow()

        if selected_row != -1:
            empl_id = self.main_window.employeeListTable.item(selected_row, 0).text()
            lastName = self.main_window.employeeListTable.item(selected_row, 1).text()
            firstName = self.main_window.employeeListTable.item(selected_row, 2).text()
            middleName = self.main_window.employeeListTable.item(selected_row, 3).text()

            # Displays the data of selected row in the Employee Basic Info Frame
            self.main_window.txtEmployeeID.setText(empl_id)
            self.main_window.txtLastName.setText(lastName)
            self.main_window.txtFirstName.setText(firstName)
            self.main_window.txtMiddleName.setText(middleName)

    def searchAndDisplay(self, searchText):
        self.main_window.employeeListTable.setRowCount(0)

        query = """
            SELECT empl_id, surname, firstname, mi FROM emp_info 
            WHERE empl_id LIKE %s OR surname LIKE %s OR firstname LIKE %s OR mi LIKE %s
            ORDER BY surname
        """
        searchText = f"%{searchText}%"
        employees = executeQuery(query, searchText, searchText, searchText, searchText)

        if employees is None:
            print("No employees match the search criteria")
            return

        for rowNum, eachRow in enumerate(employees):
            self.main_window.employeeListTable.insertRow(rowNum)
            for column, data in enumerate(eachRow):
                self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))

    def open_otherInformationMODAL_view(self):
        modal = personalModal()
        modal.addBTN.setEnabled(False)
        modal.saveBTN.setEnabled(False)

        selected_row = self.main_window.employeeListTable.currentRow()
        if selected_row != -1:
            empID = self.main_window.employeeListTable.item(selected_row, 0).text()
            employee_data = self.fetch_employee_data(empID)
            if employee_data:
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

    @single_function_logger.log_function
    def fetch_employee_data(self, empID):
        query = """
            SELECT p.empl_id, p.surname, p.firstname, p.mi, p.suffix, p.street, p.barangay, p.city, p.province,
               p.zipcode, p.mobile, p.height, p.weight, p.status, p.birthday, p.birthplace, p.sex,
               f.fathersLastName, f.fathersFirstName, f.fathersMiddleName, f.mothersLastName, 
               f.mothersFirstName, f.mothersMiddleName, f.spouseLastName, f.spouseFirstName, 
               f.spouseMiddleName, f.beneficiaryLastName, f.beneficiaryFirstName, f.beneficiaryMiddleName, 
               f.dependentsName,
               i.sss, i.tin, i.pagibig, i.philhealth,
               w.fromDate, w.toDate, w.companyName, w.companyAdd, w.empPosition,
               t.techSkill1, t.certificate1, t.validationDate1, t.techSkill2, t.certificate2, t.validationDate2,
               t.techSkill3, t.certificate3, t.validationDate3,
               e.college, e.highSchool, e.elemSchool,
               e.collegeAdd, e.highschoolAdd, e.elemAdd, e.collegeCourse, e.highschoolStrand, e.collegeYear,
               e.highschoolYear, e.elemYear
               FROM emp_info p
               LEFT JOIN educ_information e on p.empl_id = e.empl_id
               LEFT JOIN family_background f ON p.empl_id = f.empl_id
               LEFT JOIN emp_list_id i ON p.empl_id = i.empl_id
               LEFT JOIN work_exp w ON p.empl_id = w.empl_id
               LEFT JOIN tech_skills t ON p.empl_id = t.empl_id
               WHERE p.empl_id = %s
            """
        try:
            connection = create_connection('FILE201')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return None

            cursor = connection.cursor()
            cursor.execute(query, (empID,))
            result = cursor.fetchone()
            if result:
                return result  # Returns a tuple with all fetched columns
            return None

        except Error as e:
            logging.error(f"Error fetching employee data: {e}")
            return None

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def populate_modal_with_employee_data(self, modal, data):
        try:
            (empl_id, surname, firstname, mi, suffix, street, barangay, city, province, zipcode,
             mobile, height, weight, status, birthday, birthplace, sex,
             fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, mothersFirstName, mothersMiddleName,
             spouseLastName, spouseFirstName, spouseMiddleName, beneficiaryLastName, beneficiaryFirstName,
             beneficiaryMiddleName, dependentsName,
             sss, pagibig, philhealth, tin,
             from_date, to_date, company_name, company_add, position,
             tech_skill1, certificate_skill1, validation_date1, tech_skill2, certificate_skill2, validation_date2,
             tech_skill3, certificate_skill3, validation_date3, college, high_school, elem_school,
             college_add, highschool_add, elem_add, college_course, highschool_strand, college_year,
             highschool_year, elem_year) = data

            modal.nameDisplay.setText(f"{surname} {firstname} {mi}")
            modal.idDisplay.setText(str(empl_id))
            modal.txtLastName.setText(surname)
            modal.txtFirstName.setText(firstname)
            modal.txtMiddleName.setText(mi)
            modal.txtSuffix.setText(suffix)
            modal.txtStreet.setText(street)
            modal.txtBarangay.setText(barangay)
            modal.txtCity.setText(city)
            modal.txtProvince.setText(province)
            modal.txtZip.setText(str(zipcode))
            modal.txtPhone.setText(mobile)
            modal.txtHeight.setText(str(height))
            modal.txtWeight.setText(str(weight))
            modal.cmbCivil.setCurrentText(status)
            modal.dtDateOfBirth.setDate(QDate.fromString(birthday, "yyyy-MM-dd"))
            modal.txtPlace.setText(birthplace)
            modal.cmbGender.setCurrentText(sex)

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

            modal.sssTextEdit.setText(str(sss))
            modal.pagibigTextEdit.setText(str(pagibig))
            modal.philHealthTextEdit.setText(str(philhealth))
            modal.tinTextEdit.setText(str(tin))

            modal.dateStart_4.setDate(QDate.fromString(from_date, "MM-dd-yyyy"))
            modal.dateEnd_4.setDate(QDate.fromString(to_date, "MM-dd-yyyy"))
            modal.companyTextEdit_4.setText(company_name)
            modal.addressTextEdit_4.setText(company_add)
            modal.positionTextEdit_4.setText(position)

            modal.techSkillTextEdit.setText(tech_skill1)
            modal.certiTextEdit1.setText(certificate_skill1)
            modal.validationDate1.setDate(QDate.fromString(validation_date1, "MM-dd-yyyy"))

            modal.techSkillTextEdit_2.setText(tech_skill2)
            modal.certiTextEdit1_2.setText(certificate_skill2)
            modal.validationDate1_2.setDate(QDate.fromString(validation_date2, "MM-dd-yyyy"))

            modal.techSkillTextEdit_3.setText(tech_skill3)
            modal.certiTextEdit1_3.setText(certificate_skill3)
            modal.validationDate1_3.setDate(QDate.fromString(validation_date3, "MM-dd-yyyy"))

            modal.collegeTextEdit.setText(college)
            modal.highTextEdit.setText(high_school)
            modal.elemTextEdit.setText(elem_school)

            modal.addressTextEdit.setText(college_add)
            modal.addressTextEdit2.setText(highschool_add)
            modal.addressTextEdit3.setText(elem_add)

            modal.courseTextEdit.setText(college_course)
            modal.courseTextEdit2.setText(highschool_strand)

            modal.schoolYear.setDate(QDate.fromString(college_year, "MM-dd-yyyy"))
            modal.schoolYear2.setDate(QDate.fromString(highschool_year, "MM-dd-yyyy"))
            modal.schoolYear3.setDate(QDate.fromString(elem_year, "MM-dd-yyyy"))

        except Exception as e:
            #logger.error(f"Error populating modal with employee data: {e}")
            print(f"Error: {e}")

    def open_otherInformationMODAL_add(self):
        modal = personalModal()
        modal.editBTN.setEnabled(False)
        modal.saveBTN.setEnabled(False)
        modal.revertBTN.setEnabled(False)
        modal.finished.connect(self.displayEmployees)  # Updates the employeeListTable upon closing
        modal.exec_()

    def clearFunction(self):
        # unselects the current selected row
        self.main_window.employeeListTable.clearSelection()
        self.main_window.employeeListTable.selectionModel().clearCurrentIndex()

        self.main_window.txtSearch.clear()
        self.main_window.txtEmployeeID.clear()
        self.main_window.txtLastName.clear()
        self.main_window.txtFirstName.clear()
        self.main_window.txtMiddleName.clear()

    def searchEmployees(self):
        searchText = self.main_window.txtSearch.text()
        if searchText:
            self.main_window.functions.searchAndDisplay(searchText)
        else:
            self.main_window.functions.displayEmployees()
