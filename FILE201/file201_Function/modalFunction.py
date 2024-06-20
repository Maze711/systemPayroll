from PyQt5.QtWidgets import QPlainTextEdit
import logging
from PyQt5.QtWidgets import QMessageBox
from FILE201.Database_Connection.modalSQLQuery import add_employee

# Configure the logger
logger = logging.getLogger(__name__)

class modalFunction:
    def __init__(self, main_window):
        self.main_window = main_window

    def add_Employee(self):
        try:
            required_fields = [
                # Personal information
                ('Last Name', self.main_window.txtLastName.text()),
                ('First Name', self.main_window.txtFirstName.text()),
                ('Middle Name', self.main_window.txtMiddleName.text()),
                ('Suffix', self.main_window.txtLastName.text()),

                # Address/Phone Number Inputs
                ('Street', self.main_window.txtStreet.text()),
                ('Barangay', self.main_window.txtBarangay.text()),
                ('City', self.main_window.txtCity.text()),
                ('Province', self.main_window.txtProvince.text()),
                ('ZIP', self.main_window.txtZip.text()),
                ('Phone Number', self.main_window.txtPhone.text()),

                ('Height', self.main_window.txtHeight.text()),
                ('Weight', self.main_window.txtWeight.text()),
                ('Civil Status', self.main_window.cmbCivil.currentText()),
                ('Date of Birth', self.main_window.dtDateOfBirth.date().toString("MM.dd.yyyy")),
                ('Place of Birth', self.main_window.txtPlace.text()),
                ('Gender', self.main_window.cmbGender.currentText()),

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

                # Employee ID inputs
                ('SSS Number', self.main_window.sssTextEdit.toPlainText()),
                ('Pag-IBIG Number', self.main_window.pagibigTextEdit.toPlainText()),
                ('PhilHealth Number', self.main_window.philHealthTextEdit.toPlainText()),
                ('TIN Number', self.main_window.tinTextEdit.toPlainText()),

                # HR Notes Text Input
                ('HR Notes', self.main_window.hrNoteTextEdit.toPlainText()),

                # Working Experience Containers/Inputs
                ('Date From', self.main_window.dateStart_4.date().toString("MM.dd.yyyy")),
                ('Date To', self.main_window.dateEnd_4.date().toString("MM.dd.yyyy")),
                ('Company', self.main_window.companyTextEdit_4.toPlainText()),
                ('Company Address', self.main_window.addressTextEdit_4.toPlainText()),
                ('Position', self.main_window.positionTextEdit_4.toPlainText()),

                # Educational and Skill Information text and date inputs
                ('Technical Skills #1', self.main_window.techSkillTextEdit.toPlainText()),
                # ('Technical Skills #2', self.main_window.techSkillTextEdit_2.toPlainText()),
                # ('Technical Skills #3', self.main_window.techSkillTextEdit_3.toPlainText()),

                ('Certificate #1', self.main_window.certiTextEdit1.toPlainText()),
                # ('Certificate #2', self.main_window.certiTextEdit1_2.toPlainText()),
                # ('Certificate #3', self.main_window.certiTextEdit1_3.toPlainText()),

                ('Validation Date #1', self.main_window.validationDate1.date().toString("MM.dd.yyyy")),
                # ('Validation Date #2', self.main_window.validationDate1_2.date().toString("MM.dd.yyyy")),
                # ('Validation Date #3', self.main_window.validationDate1_3.date().toString("MM.dd.yyyy")),

                ('College', self.main_window.collegeTextEdit.toPlainText()),
                ('High-School', self.main_window.highTextEdit.toPlainText()),
                ('Elementary', self.main_window.elemTextEdit.toPlainText()),

                ('College Address', self.main_window.addressTextEdit.toPlainText()),
                ('High-School Address', self.main_window.addressTextEdit2.toPlainText()),
                ('Elementary Address', self.main_window.addressTextEdit3.toPlainText()),

                ('College Course', self.main_window.courseTextEdit.toPlainText()),
                ('High-School Strand', self.main_window.courseTextEdit2.toPlainText()),

                ('College Graduate Year', self.main_window.schoolYear.date().toString("MM.dd.yyyy")),
                ('High-School Graduate Year', self.main_window.schoolYear2.date().toString("MM.dd.yyyy")),
                ('Elementary Graduate Year', self.main_window.schoolYear3.date().toString("MM.dd.yyyy")),
            ]

            # Validate required fields
            for field_name, value in required_fields:
                if field_name != 'Suffix' and not value.strip():  # Check if the value is empty or whitespace
                    QMessageBox.warning(self.main_window, "Input Error", f"{field_name} is required.")
                    return

            # Create a dictionary with field names as keys and values as GUI input values
            data = {name: value for name, value in required_fields}

            # Log data
            for key, value in data.items():
                logger.info(f"{key}: {value}")

            # Call function to add employee data to the database
            success = add_employee(data)

            message = "Employee data added successfully." if success else "Failed to add employee data."
            logger.info(message)
            if success:
                QMessageBox.information(self.main_window, "Success", message)
            else:
                QMessageBox.critical(self.main_window, "Error", message)

        except Exception as e:
            logger.error(f"Error in add_Employee: {e}")
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {e}")

    def edit_Employee(self):
        print("This is a EDIT Button")

    def save_Employee(self):
        print("This is a SAVE Button")

    def revert_Employee(self):
        print("This is a REVERT Button")