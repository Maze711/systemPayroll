from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.modalSQLQuery import executeQuery
from MainFrame.FILE201.Other_Information.otherInformationModal import personalModal
from MainFrame.systemFunctions import DatabaseConnectionError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ListFunction:
    def __init__(self, main_window):
        self.main_window = main_window

        self.main_window.employeeListTable.cellDoubleClicked.connect(self.on_emp_double_click)

    # Displays Current Date and Time
    def timeClock(self):
        time_format = strftime("%I:%M:%S %p")
        self.main_window.lblTime.setText(time_format)

        date_format = strftime("%A, %B %d, %Y")
        self.main_window.lblDate.setText(date_format)

    # Displays all employees in the table
    def displayEmployees(self):
        try:
            # Clears/Resets the rows in the table
            self.main_window.employeeListTable.setRowCount(0)

            # Select only the required columns and order by surname
            query = "SELECT empl_id, surname, firstname, mi FROM emp_info ORDER BY empl_id"
            employees = executeQuery(query)

            if employees is None:
                print("There are no current employees")
                return

            for rowNum, eachRow in enumerate(employees):
                self.main_window.employeeListTable.insertRow(rowNum)
                # Assuming eachRow contains (empl_id, surname, firstname, mi)
                for column, data in enumerate(eachRow):
                    item = QTableWidgetItem(str(data))
                    # item.setTextAlignment(Qt.AlignCenter)  # Center the text
                    self.main_window.employeeListTable.setItem(rowNum, column, item)

        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(self.main_window, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

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
        try:
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

        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(self.main_window, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

    def open_otherInformationMODAL_view(self):
        try:
            modal = personalModal(mode='view')

            selected_row_id = self.main_window.txtEmployeeID.text()
            if selected_row_id != "":
                empID = selected_row_id
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

        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(self.main_window, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

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
            SELECT p.empl_id, p.surname, p.firstname, p.mi, p.suffix, p.street, p.barangay, p.city, p.province,
                   p.zipcode, p.mobile, p.height, p.weight, p.status, p.birthday, p.birthplace, p.sex, p.religion, 
                   p.citizenship, p.blood_type, p.email, f.fathersLastName, f.fathersFirstName, f.fathersMiddleName, 
                   f.mothersLastName, f.mothersFirstName, f.mothersMiddleName, f.spouseLastName, f.spouseFirstName, 
                   f.spouseMiddleName, f.beneficiaryLastName, f.beneficiaryFirstName, f.beneficiaryMiddleName, 
                   f.dependentsName, m.emer_name, w.fromDate, w.toDate, w.companyName, w.companyAdd, w.empPosition,
                   i.sss, i.tin, i.pagibig, i.philhealth,
                   t.techSkill1, t.certificate1, t.validationDate1, t.techSkill2, t.certificate2, t.validationDate2,
                   t.techSkill3, t.certificate3, t.validationDate3, e.college, e.highSchool, e.elemSchool,
                   e.collegeAdd, e.highschoolAdd, e.elemAdd, e.collegeCourse, e.highschoolStrand, e.collegeYear,
                   e.highschoolYear, e.elemYear, img.empl_img, s.compcode, s.dept_code, s.emp_stat, 
                   s.date_hired, s.resigned, s.dtresign
            FROM emp_info p
            LEFT JOIN educ_information e ON p.empl_id = e.empl_id
            LEFT JOIN emergency_list m ON p.empl_id = m.empl_id
            LEFT JOIN family_background f ON p.empl_id = f.empl_id
            LEFT JOIN work_exp w ON p.empl_id = w.empl_id
            LEFT JOIN emp_list_id i ON p.empl_id = i.empl_id
            LEFT JOIN tech_skills t ON p.empl_id = t.empl_id
            LEFT JOIN emp_images img ON p.empl_id = img.empl_id
            LEFT JOIN emp_status s ON p.empl_id = s.empl_id
            WHERE p.empl_id = %s
        """
        try:
            connection = create_connection('NTP_EMP_LIST')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (empID,))
            result = cursor.fetchone()
            return result if result else None

        except Error as e:
            logging.error(f"Error fetching employee data: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")

    def populate_modal_with_employee_data(self, modal, data):
        def capitalize_string(value):
            """Capitalize string values while handling None and non-string types"""
            if not isinstance(value, str):
                return value

            # Skip capitalization for specific cases
            if '@' in value or any(c.isdigit() for c in value) or value.isupper():
                return value

            # Capitalize each word
            return ' '.join(word.capitalize() for word in value.split())

        try:
            # Dictionary mapping modal fields to data keys
            field_mapping = {
                # EMP_INFO TABLE
                "nameDisplay": f"{data['surname']} {data['firstname']} {data['mi']}",
                "idDisplay": data['empl_id'],
                "txtLastName": capitalize_string(data['surname']),
                "txtFirstName": capitalize_string(data['firstname']),
                "txtMiddleName": capitalize_string(data['mi']),
                "txtSuffix": capitalize_string(data['suffix']),
                "txtStreet": capitalize_string(data['street']),
                "txtBarangay": capitalize_string(data['barangay']),
                "txtCity": capitalize_string(data['city']),
                "txtProvince": capitalize_string(data['province']),
                "txtZip": data['zipcode'],
                "txtPhone": data['mobile'],
                "txtHeight": data['height'],
                "txtWeight": data['weight'],
                "cmbCivil": capitalize_string(data['status']),
                "dtDateOfBirth": QDate.fromString(data['birthday'], "dd-MMM-yy"),
                "txtPlace": capitalize_string(data['birthplace']),
                "cmbGender": capitalize_string(data['sex']),
                "txtReligion": capitalize_string(data['religion']),
                "txtCitizenship": capitalize_string(data['citizenship']),
                "txtEmail": data['email'],
                "cmbBlood": data['blood_type'],
                # FAMILY_BACKGROUND TABLE
                "txtFatherLast": capitalize_string(data['fathersLastName']),
                "txtFatherFirst": capitalize_string(data['fathersFirstName']),
                "txtFatherMiddle": capitalize_string(data['fathersMiddleName']),
                "txtMotherLast": capitalize_string(data['mothersLastName']),
                "txtMotherFirst": capitalize_string(data['mothersFirstName']),
                "txtMotherMiddle": capitalize_string(data['mothersMiddleName']),
                "txtSpouseLast": capitalize_string(data['spouseLastName']),
                "txtSpouseFirst": capitalize_string(data['spouseFirstName']),
                "txtSpouseMiddle": capitalize_string(data['spouseMiddleName']),
                "txtBeneLast": capitalize_string(data['beneficiaryLastName']),
                "txtBeneFirst": capitalize_string(data['beneficiaryFirstName']),
                "txtBeneMiddle": capitalize_string(data['beneficiaryMiddleName']),
                "txtDependent": capitalize_string(data['dependentsName']),
                # EMERGENCY_LIST TABLE
                "txtEmergency": capitalize_string(data['emer_name']),
                # WORK_EXP TABLE
                "dateStart_4": QDate.fromString(data['fromDate'], "MM-dd-yyyy"),
                "dateEnd_4": QDate.fromString(data['toDate'], "MM-dd-yyyy"),
                "companyTextEdit_4": capitalize_string(data['companyName']),
                "addressTextEdit_4": capitalize_string(data['companyAdd']),
                "positionTextEdit_4": capitalize_string(data['empPosition']),
                # EMP_LIST_ID TABLE
                "sssIDTextEdit": data['sss'],
                "pagibigIDTextEdit": data['pagibig'],
                "philheatlhIDTextEdit": data['philhealth'],
                "tinIDTextEdit": data['tin'],
                # TECH_SKILLS TABLE
                "techSkillTextEdit": capitalize_string(data['techSkill1']),
                "certiTextEdit1": capitalize_string(data['certificate1']),
                "validationDate1": QDate.fromString(data['validationDate1'], "MM-dd-yyyy"),
                "techSkillTextEdit_2": capitalize_string(data['techSkill2']),
                "certiTextEdit1_2": capitalize_string(data['certificate2']),
                "validationDate1_2": QDate.fromString(data['validationDate2'], "MM-dd-yyyy"),
                "techSkillTextEdit_3": capitalize_string(data['techSkill3']),
                "certiTextEdit1_3": capitalize_string(data['certificate3']),
                "validationDate1_3": QDate.fromString(data['validationDate3'], "MM-dd-yyyy"),
                # EDUCATION TABLE
                "collegeTextEdit": capitalize_string(data['college']),
                "highTextEdit": capitalize_string(data['highSchool']),
                "elemTextEdit": capitalize_string(data['elemSchool']),
                "addressTextEdit": capitalize_string(data['collegeAdd']),
                "addressTextEdit2": capitalize_string(data['highschoolAdd']),
                "addressTextEdit3": capitalize_string(data['elemAdd']),
                "courseTextEdit": capitalize_string(data['collegeCourse']),
                "courseTextEdit2": capitalize_string(data['highschoolStrand']),
                "schoolYear": QDate.fromString(data['collegeYear'], "MM-dd-yyyy"),
                "schoolYear2": QDate.fromString(data['highschoolYear'], "MM-dd-yyyy"),
                "schoolYear3": QDate.fromString(data['elemYear'], "MM-dd-yyyy"),
                # EMP_IMAGES TABLE
                "lblViewImg": data['empl_img'],
                # EMP_STATUS TABLE
                "lblComp": data['compcode'],
                "lblDept_2": data['dept_code'],
                "boxStatus": data['emp_stat'],
                "dateHired_2": QDate.fromString(data['date_hired'], "dd-MMM-yy"),
                "cmbResigned_2": data['resigned'],
                "dateResigned": QDate.fromString(data['dtresign'], "dd-MMM-yy")
            }

            # Populate modal fields
            for field, value in field_mapping.items():
                if hasattr(modal, field):
                    widget = getattr(modal, field)

                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QLabel):
                        widget.setText(str(value))
                        if widget.objectName() == 'lblViewImg':
                            if not value:
                                pixmap = QPixmap("MainFrame/Resources/Icons/user.svg")
                                widget.setPixmap(pixmap)
                            else:
                                pixmap = self.convertBLOBToPixmap(value)
                                scaled_pixmap = pixmap.scaled(widget.size(),
                                                              Qt.KeepAspectRatioByExpanding,
                                                              Qt.SmoothTransformation)
                                widget.setPixmap(scaled_pixmap)
                                modal.btnUploadImg.hide()
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentText(str(value))
                    elif isinstance(widget, QDateEdit):
                        widget.setDate(value if isinstance(value, QDate) else QDate.currentDate())
                    else:
                        logging.warning(f"Unhandled widget type for field: {field}")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error Populating Modal",
                                 f"Error populating modal with employee data: {e}\n"
                                 "Please check the data provided.")

    def open_otherInformationMODAL_add(self):
        modal = personalModal(mode='add')
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

    def convertBLOBToPixmap(self, blob_data):
        pixmap = QPixmap()
        try:
            if not pixmap.loadFromData(QByteArray(blob_data)):
                logging.error("Failed to load image from BLOB data.")
                return None
        except Exception as e:
            QMessageBox.critical(self.main_window, "Exception Occurred",
                                 f"An error occurred while loading the image: {e}")
            return None
        return pixmap

    def on_emp_double_click(self, row, column):
        try:
            empl_id = self.main_window.employeeListTable.item(row, 0).text()

            if empl_id:
                self.open_otherInformationMODAL_view()
            else:
                QMessageBox.warning(self.main_window, "No Employee Selected", "Please select a valid employee.")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

    def handle_checkbox_change(self, checkbox):
        """Handles the checkbox state changes for employee status filters"""
        try:
            boxAllEmp = self.main_window.boxAllEmp
            boxActEmp = self.main_window.boxActEmp
            boxResEmp = self.main_window.boxResEmp

            if not checkbox.isChecked():
                return

            if checkbox == boxAllEmp:
                boxActEmp.setChecked(False)
                boxResEmp.setChecked(False)
                self.displayEmployees()  # Show all employees
            elif checkbox == boxActEmp:
                boxAllEmp.setChecked(False)
                boxResEmp.setChecked(False)
                self.displayActiveEmployees()
            elif checkbox == boxResEmp:
                boxAllEmp.setChecked(False)
                boxActEmp.setChecked(False)
                self.displayResignedEmployees()

        except Exception as e:
            logging.error(f"Error in handle_checkbox_change: {e}")
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")

    def displayActiveEmployees(self):
        """Displays only active employees in the table"""
        try:
            self.main_window.employeeListTable.setRowCount(0)
            query = """
                SELECT e.empl_id, e.surname, e.firstname, e.mi 
                FROM emp_info e
                INNER JOIN emp_status s ON e.empl_id = s.empl_id
                WHERE s.resigned = 'N'
                ORDER BY e.surname
            """
            employees = executeQuery(query)

            if employees:
                for rowNum, eachRow in enumerate(employees):
                    self.main_window.employeeListTable.insertRow(rowNum)
                    for column, data in enumerate(eachRow):
                        self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))

        except Exception as e:
            logging.error(f"Error displaying active employees: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to load active employees: {str(e)}")

    def displayResignedEmployees(self):
        """Displays only resigned employees in the table"""
        try:
            self.main_window.employeeListTable.setRowCount(0)
            query = """
                SELECT e.empl_id, e.surname, e.firstname, e.mi 
                FROM emp_info e
                INNER JOIN emp_status s ON e.empl_id = s.empl_id
                WHERE s.resigned = 'Y'
                ORDER BY e.surname
            """
            employees = executeQuery(query)

            if employees:
                for rowNum, eachRow in enumerate(employees):
                    self.main_window.employeeListTable.insertRow(rowNum)
                    for column, data in enumerate(eachRow):
                        self.main_window.employeeListTable.setItem(rowNum, column, QTableWidgetItem(str(data)))

        except Exception as e:
            logging.error(f"Error displaying resigned employees: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to load resigned employees: {str(e)}")