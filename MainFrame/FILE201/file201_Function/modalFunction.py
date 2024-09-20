import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.modalSQLQuery import add_employee, save_employee
from MainFrame.systemFunctions import DatabaseConnectionError


def set_fields_non_editable(modal):
    activeStyle = "background-color: white; color: black;"

    for widget in modal.findChildren(QLineEdit):
        widget.setReadOnly(False)
        widget.setStyleSheet(activeStyle)

    for widget in modal.findChildren(QDateEdit):
        widget.setReadOnly(False)
        widget.setStyleSheet(activeStyle)

    for widget in modal.findChildren(QComboBox):
        widget.setDisabled(False)
        widget.setStyleSheet(activeStyle)

    for widget in modal.findChildren(QPlainTextEdit):
        widget.setReadOnly(False)
        widget.setStyleSheet(activeStyle)


class modalFunction:
    def __init__(self, main_window):
        self.main_window = main_window
        self.image_value = None

    def add_Employee(self):
        try:
            required_fields = [
                # Personal information
                ('Last Name', self.main_window.txtLastName.text()),
                ('First Name', self.main_window.txtFirstName.text()),
                ('Middle Name', self.main_window.txtMiddleName.text()),
                ('Suffix', self.main_window.txtSuffix.text()),

                # Address/Phone Number Inputs
                ('Street', self.main_window.txtStreet.text()),
                ('Barangay', self.main_window.txtBarangay.text()),
                ('City', self.main_window.txtCity.text()),
                ('Province', self.main_window.txtProvince.text()),
                ('zipcode', self.main_window.txtZip.text()),
                ('Phone Number', self.main_window.txtPhone.text()),
                ('Religion', self.main_window.txtReligion.text()),
                ('Citizenship', self.main_window.txtCitizenship.text()),
                ('Email', self.main_window.txtEmail.text()),

                ('Height', self.main_window.txtHeight.text()),
                ('Weight', self.main_window.txtWeight.text()),
                ('Civil Status', self.main_window.cmbCivil.currentText()),
                ('Date of Birth', self.main_window.dtDateOfBirth.date().toString("dd-MMM-yy")),
                ('Place of Birth', self.main_window.txtPlace.text()),
                ('Gender', self.main_window.cmbGender.currentText()),
                ('Blood Type', self.main_window.cmbBlood.currentText()),

                # Employee's uploaded image
                ('Employee Image', self.get_employee_img()),

                # Employee's Family Background Inputs
                ("Father's Last Name", self.main_window.txtFatherLast.text()),
                ("Father's First Name", self.main_window.txtFatherFirst.text()),
                ("Father's Middle Name", self.main_window.txtFatherMiddle.text()),

                ("Mother's Last Name", self.main_window.txtMotherLast.text()),
                ("Mother's First Name", self.main_window.txtMotherFirst.text()),
                ("Mother's Middle Name", self.main_window.txtMotherMiddle.text()),

                ("Spouse's Last Name", self.main_window.txtSpouseLast.text()),
                ("Spouse's First Name", self.main_window.txtSpouseFirst.text()),
                ("Spouse's Middle Name", self.main_window.txtSpouseMiddle.text()),

                ("Beneficiary's Last Name", self.main_window.txtBeneLast.text()),
                ("Beneficiary's First Name", self.main_window.txtBeneFirst.text()),
                ("Beneficiary's Middle Name", self.main_window.txtBeneMiddle.text()),

                ("Dependent's Name", self.main_window.txtDependent.text()),
                ("Emergency Name", self.main_window.txtEmergency.text()),

                # # Employee ID inputs
                # ('SSS Number', self.main_window.sssTextEdit.text()),
                # ('Pag-IBIG Number', self.main_window.pagibigTextEdit.text()),
                # ('PhilHealth Number', self.main_window.philHealthTextEdit.text()),
                # ('TIN Number', self.main_window.tinTextEdit.text()),
                # ('Taxstat', self.main_window.txtTaxstat.text()),
                # ('Account no.', self.main_window.txtAccount.text()),
                # ('Bank code', self.main_window.txtBank.text()),
                # ('Cola', self.main_window.txtCola.text()),

                # HR Notes Text Input
                ('HR Notes', self.main_window.hrNoteTextEdit.toPlainText()),

                # Working Experience Containers/Inputs
                ('Date From', self.main_window.dateStart_4.date().toString("MM-dd-yyyy")),
                ('Date To', self.main_window.dateEnd_4.date().toString("MM-dd-yyyy")),
                ('Company', self.main_window.companyTextEdit_4.text()),
                ('Company Address', self.main_window.addressTextEdit_4.text()),
                ('Position', self.main_window.positionTextEdit_4.text()),

                # Educational and Skill Information text and date inputs
                ('Technical Skills #1', self.main_window.techSkillTextEdit.text()),
                ('Technical Skills #2', self.main_window.techSkillTextEdit_2.text()),
                ('Technical Skills #3', self.main_window.techSkillTextEdit_3.text()),

                ('Certificate #1', self.main_window.certiTextEdit1.text()),
                ('Certificate #2', self.main_window.certiTextEdit1_2.text()),
                ('Certificate #3', self.main_window.certiTextEdit1_3.text()),

                ('Validation Date #1', self.main_window.validationDate1.date().toString("MM-dd-yyyy")),
                ('Validation Date #2', self.main_window.validationDate1_2.date().toString("MM.dd.yyyy")),
                ('Validation Date #3', self.main_window.validationDate1_3.date().toString("MM.dd.yyyy")),

                ('College', self.main_window.collegeTextEdit.text()),
                ('High-School', self.main_window.highTextEdit.text()),
                ('Elementary', self.main_window.elemTextEdit.text()),

                ('College Address', self.main_window.addressTextEdit.text()),
                ('High-School Address', self.main_window.addressTextEdit2.text()),
                ('Elementary Address', self.main_window.addressTextEdit3.text()),

                ('College Course', self.main_window.courseTextEdit.text()),
                ('High-School Strand', self.main_window.courseTextEdit2.text()),

                ('College Graduate Year', self.main_window.schoolYear.date().toString("MM-dd-yyyy")),
                ('High-School Graduate Year', self.main_window.schoolYear2.date().toString("MM-dd-yyyy")),
                ('Elementary Graduate Year', self.main_window.schoolYear3.date().toString("MM-dd-yyyy")),

                ('Computer Code', self.main_window.lblComp.text()),
                ('Department Code', self.main_window.lblDept_2.text()),
                ('Status', self.main_window.txtStatus.text()),
                ('Date Hired', self.main_window.dateHired_2.date().toString("dd-MMM-yy")),
                ('Resigned', self.main_window.cmbResigned_2.currentText()),
                ('Date Resign', self.main_window.dateResigned.date().toString("dd-MMM-yy"))
            ]

            not_required_fields = ['Suffix', 'zipcode', 'Height', 'Weight', 'Place of Birth', 'Date From', 'Date To',
                                   'Employee Image', 'Company', 'Company Address', 'Position',
                                   "Father's Last Name", "Father's First Name", "Father's Middle Name",
                                   "Mother's Last Name", "Mother's First Name", "Mother's Middle Name",
                                   "Spouse's Last Name", "Spouse's First Name", "Spouse's Middle Name",
                                   "Beneficiary's Last Name", "Beneficiary's First Name", "Beneficiary's Middle Name",
                                   'HR Notes', "Dependent's Name", 'Technical Skills #1', 'Certificate #1',
                                   'Validation Date #1', 'Technical Skills #2', 'Certificate #2', 'Validation Date #2',
                                   'Technical Skills #3', 'Certificate #3', 'Validation Date #3', 'Elementary',
                                   'Elementary Address', 'Elementary Graduate Year', 'High-School',
                                   'High-School Address',
                                   'High-School Strand', 'High-School Graduate Year', 'College', 'College Address',
                                   'College Course', 'College Graduate Year', 'Computer Code', 'Department Code']

            # Validate required fields
            for field_name, value in required_fields:
                if field_name not in not_required_fields and not value.strip():  # Check if the value is empty or whitespace
                    QMessageBox.warning(self.main_window, "Input Error", f"{field_name} is required.")
                    return

            # Create a dictionary with field names as keys and values as GUI input values
            data = {name: value for name, value in required_fields}

            # Call function to add employee data to the database
            success = add_employee(data)
            message = "Employee data added successfully." if success else "Failed to add employee data."
            if success:
                QMessageBox.information(self.main_window, "Success", message)
                self.image_value = None
                self.main_window.close()  # Closes the modal
            else:
                QMessageBox.critical(self.main_window, "Adding Employee Error", f"{message} "
                                                                                f"Please check your network connection or contact the "
                                                                                f"system administrator.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Adding Employee Error", f"An error occurred: {e}")

    def edit_Employee(self):
        self.set_fields_editable()

    def set_fields_editable(self):
        activeStyle = "background-color: white; color: black;"

        for widget in self.main_window.findChildren(QLineEdit):
            widget.setReadOnly(False)
            widget.setStyleSheet(activeStyle)

        for widget in self.main_window.findChildren(QDateEdit):
            widget.setReadOnly(False)
            widget.setStyleSheet(activeStyle)

        for widget in self.main_window.findChildren(QComboBox):
            widget.setEnabled(True)
            widget.setStyleSheet(activeStyle)

        for widget in self.main_window.findChildren(QPlainTextEdit):
            widget.setReadOnly(False)
            widget.setStyleSheet(activeStyle)

    def gather_form_data(self):
        data = {
            'lastName': self.main_window.txtLastName.text(),
            'firstName': self.main_window.txtFirstName.text(),
            'middleName': self.main_window.txtMiddleName.text(),
            'suffix': self.main_window.txtSuffix.text(),

            'Street': self.main_window.txtStreet.text(),
            'Barangay': self.main_window.txtBarangay.text(),
            'City': self.main_window.txtCity.text(),
            'Province': self.main_window.txtProvince.text(),
            'zipcode': self.main_window.txtZip.text(),
            'Phone Number': self.main_window.txtPhone.text(),
            'Religion': self.main_window.txtReligion.text(),
            'Citizenship': self.main_window.txtCitizenship.text(),
            'Email': self.main_window.txtEmail.text(),

            'Height': self.main_window.txtHeight.text(),
            'Weight': self.main_window.txtWeight.text(),
            'Civil Status': self.main_window.cmbCivil.currentText(),
            'Date of Birth': self.main_window.dtDateOfBirth.date().toString("dd-MMM-yy"),
            'Place of Birth': self.main_window.txtPlace.text(),
            'Gender': self.main_window.cmbGender.currentText(),
            'Blood Type': self.main_window.cmbBlood.currentText(),

            'Employee Image': self.getImageByte(),

            "Father's Last Name": self.main_window.txtFatherLast.text(),
            "Father's First Name": self.main_window.txtFatherFirst.text(),
            "Father's Middle Name": self.main_window.txtFatherMiddle.text(),

            "Mother's Last Name": self.main_window.txtMotherLast.text(),
            "Mother's First Name": self.main_window.txtMotherFirst.text(),
            "Mother's Middle Name": self.main_window.txtMotherMiddle.text(),

            "Spouse's Last Name": self.main_window.txtSpouseLast.text(),
            "Spouse's First Name": self.main_window.txtSpouseFirst.text(),
            "Spouse's Middle Name": self.main_window.txtSpouseMiddle.text(),

            "Beneficiary's Last Name": self.main_window.txtBeneLast.text(),
            "Beneficiary's First Name": self.main_window.txtBeneFirst.text(),
            "Beneficiary's Middle Name": self.main_window.txtBeneMiddle.text(),

            "Dependent's Name": self.main_window.txtDependent.text(),
            "Emergency Name": self.main_window.txtEmergency.text(),

            # 'SSS Number': self.main_window.sssTextEdit.text(),
            # 'Pag-IBIG Number': self.main_window.pagibigTextEdit.text(),
            # 'PhilHealth Number': self.main_window.philHealthTextEdit.text(),
            # 'TIN Number': self.main_window.tinTextEdit.text(),
            # 'Taxstat': self.main_window.txtTaxstat.text(),
            # 'Account no.': self.main_window.txtAccount.text(),
            # 'Bank code': self.main_window.txtBank.text(),
            # 'Cola': self.main_window.txtCola.text(),

            'HR Notes': self.main_window.hrNoteTextEdit.toPlainText(),

            'Date From': self.main_window.dateStart_4.date().toString("MM-dd-yyyy"),
            'Date To': self.main_window.dateEnd_4.date().toString("MM-dd-yyyy"),
            'Company': self.main_window.companyTextEdit_4.text(),
            'Company Address': self.main_window.addressTextEdit_4.text(),
            'Position': self.main_window.positionTextEdit_4.text(),

            'Technical Skills #1': self.main_window.techSkillTextEdit.text(),
            'Certificate #1': self.main_window.certiTextEdit1.text(),
            'Validation Date #1': self.main_window.validationDate1.date().toString("MM-dd-yyyy"),

            'Technical Skills #2': self.main_window.techSkillTextEdit_2.text(),
            'Certificate #2': self.main_window.certiTextEdit1_2.text(),
            'Validation Date #2': self.main_window.validationDate1_2.date().toString("MM-dd-yyyy"),

            'Technical Skills #3': self.main_window.techSkillTextEdit_3.text(),
            'Certificate #3': self.main_window.certiTextEdit1_3.text(),
            'Validation Date #3': self.main_window.validationDate1_3.date().toString("MM-dd-yyyy"),

            'College': self.main_window.collegeTextEdit.text(),
            'High-School': self.main_window.highTextEdit.text(),
            'Elementary': self.main_window.elemTextEdit.text(),

            'College Address': self.main_window.addressTextEdit.text(),
            'High-School Address': self.main_window.addressTextEdit2.text(),
            'Elementary Address': self.main_window.addressTextEdit3.text(),

            'College Course': self.main_window.courseTextEdit.text(),
            'High-School Strand': self.main_window.courseTextEdit2.text(),

            'College Graduate Year': self.main_window.schoolYear.date().toString("MM-dd-yyyy"),
            'High-School Graduate Year': self.main_window.schoolYear2.date().toString("MM-dd-yyyy"),
            'Elementary Graduate Year': self.main_window.schoolYear3.date().toString("MM-dd-yyyy"),

            'Computer Code': self.main_window.lblComp.text(),
            'Department Code': self.main_window.lblDept_2.text(),
            'Status': self.main_window.txtStatus.text(),
            'Date Hired': self.main_window.dateHired_2.date().toString("dd-MMM-yy"),
            'Resigned': self.main_window.cmbResigned_2.currentText(),
            'Date Resign': self.main_window.dateResigned.date().toString("dd-MMM-yy")
        }
        return data

    def save_Employee(self):
        message = QMessageBox.question(self.main_window, "Save Employee", "Are you sure you want to save changes?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            empID = self.main_window.idDisplay.text()
            data = self.gather_form_data()

            try:
                success = save_employee(empID, data)

                if success:
                    QMessageBox.information(self.main_window, "Success", "Employee data saved successfully.")
                    self.image_value = None
                    self.main_window.close()  # Close the modal upon successful save
                else:
                    logging.error(f"Failed to save employee data for Employee ID: {empID}.")
                    QMessageBox.critical(self.main_window, "Error", "Failed to save employee data.")

            except DatabaseConnectionError as dce:
                logging.error(f"Database Connection Error: {dce}")
                QMessageBox.critical(self.main_window, "Saving Employee Data Error",
                                        f"Failed to save employee data "
                                     "An unexpected disconnection has occurred. Please check your network connection or "
                                     "contact the system administrator.")
            except Exception as e:
                print(f"Unexpected error occurred: {e}")
                logging.error(f"Unexpected error occurred: {e}")
                QMessageBox.critical(self.main_window, "Saving Employee Data Error",
                                     "An unexpected error occurred while saving employee data.")


    def revert_Employee(self):
        set_fields_non_editable(self.main_window)
        print("Revert")

    def upload_img(self):
        """Image Uploader for Employees Profile"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.main_window, "Select Excel File", "",
                "JPG, JPEG, PNG Files (*.jpg *jpeg *.png);")

            if file_name:
                file_size = os.path.getsize(file_name)
                max_size = 5 * 1024 * 1024 # 5MB size limit

                if file_size > max_size:
                    QMessageBox.warning(self.main_window, "File Too Large",
                                        "The selected file exceeds the 5 MB size limit. Please choose a smaller file.")
                else:
                    # Preview the uploaded image
                    self.pixmap = QPixmap(file_name)
                    # Scales the pixmap to fit within the lblViewImg size
                    scaled_pixmap = self.pixmap.scaled(self.main_window.lblViewImg.size(),
                                                       Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.main_window.lblViewImg.setPixmap(scaled_pixmap)

                    file_to_bytes = self.convertFileToBLOB(file_name)

                    self.set_employee_img(file_to_bytes)


        except Exception as e:
            print("Error Uploading an image: ", e)
            QMessageBox.critical(self.main_window, "Upload Error",
                                "Something went wrong while uploading an image, please try again later.")

    def convertFileToBLOB(self, file_name):
        """Converts Image file into BLOB"""
        with open(file_name, 'rb') as file:
            binary_data = file.read()
        return binary_data

    def set_employee_img(self, blob):
        self.image_value = blob

    def get_employee_img(self):
        return self.image_value

    def getImageByte(self):
        """Retrieves the image from QLabel and converts it into bytes"""
        default_img_pixmap = QPixmap("MainFrame/Resources/Icons/user.svg") # Default Profile Image
        current_pixmap = self.main_window.lblViewImg.pixmap() # Current/new Profile Image

        if current_pixmap is None:
            return None  # No image is currently set

        default_byte = self.pixmap_to_byte(default_img_pixmap)
        current_byte = self.pixmap_to_byte(current_pixmap)

        if default_byte == current_byte:
            return None

        return bytes(current_byte)

    def pixmap_to_byte(self, pixmap):
        """Pixmap to Byte Conversion"""
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, 'PNG')

        return byte_array
