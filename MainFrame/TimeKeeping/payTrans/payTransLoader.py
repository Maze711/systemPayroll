import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PayTrans(QMainWindow):
    def __init__(self, from_date, to_date, data):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytrans.ui")
        loadUi(ui_file, self)

        self.data = data
        self.original_data = data  # Store original data
        self.from_date = from_date
        self.to_date = to_date

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.populatePayTransTable(self.data)
        self.btnPayTrans.clicked.connect(self.export_to_excel)
        self.btnSendToEmail.clicked.connect(self.sendToEmail)

    def populatePayTransTable(self, data):
        for row in range(self.paytransTable.rowCount()):
            self.paytransTable.setRowHidden(row, False)

        self.paytransTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(row['EmpNo'])
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            basic_item = QTableWidgetItem(str(row['Basic']))
            present_days_item = QTableWidgetItem(row['Present Days'])
            rate_item = QTableWidgetItem(row.get('Rate', 'Missing'))  # Get rate or 'Missing' if not found
            ordinary_day_ot_item = QTableWidgetItem(row.get('OrdinaryDayOT', 'N/A'))  # Add OrdinaryDayOT
            ot_earn_item = QTableWidgetItem(str(row['OT_Earn']))  # Get OT_Earn or '0.00' if not found

            # Center all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, basic_item, present_days_item, rate_item,
                         ordinary_day_ot_item, ot_earn_item]:
                item.setTextAlignment(Qt.AlignCenter)

            # Set items in the table. Adjust the column indices as needed.
            self.paytransTable.setItem(i, 0, emp_no_item)
            self.paytransTable.setItem(i, 1, bio_num_item)
            self.paytransTable.setItem(i, 2, emp_name_item)
            self.paytransTable.setItem(i, 3, basic_item)  # Basic
            self.paytransTable.setItem(i, 4, rate_item)   # Rate
            self.paytransTable.setItem(i, 5, present_days_item)  # Present Days
            self.paytransTable.setItem(i, 6, ordinary_day_ot_item)  # OT Hours (add column index here)
            self.paytransTable.setItem(i, 14, ot_earn_item)  # OT Hours (add column index here)

    def export_to_excel(self, checked=False):
        # Define the file name where data will be saved
        file_name = "paytrans_data.xlsx"
        try:
            globalFunction.export_to_excel(self.data, file_name)
            QMessageBox.information(self, "Export Successful", f"Data has been successfully exported to {file_name}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"An error occurred while exporting data: {e}")
            logging.error(f"Export error: {e}")

    def sendToEmail(self, checked=False):
        message = QMessageBox.question(self, "Sending Email", "Are you sure you want to send an email?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            try:
                # Replace your email credentials here for testing
                email_sender = '' # Place your email here
                email_password = '' # Place your generated google password here

                # Tentative Email Receiver
                email_receiver = ['rodelcuyag123@gmail.com', 'badlonmazeclarion@gmail.com', 'jhayemcalleja011@gmail.com']

                date_sent = date.today()

                context = ssl.create_default_context()

                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)

                    for i, row in enumerate(self.original_data[0:3]): # Only 3 data will be processed (for now)
                        subject = f'Payroll Details - {date_sent}'
                        body = self.prepare_email_body(row, date_sent)

                        em = EmailMessage()
                        em['From'] = email_sender
                        em['To'] = email_receiver[i]
                        em['Subject'] = subject
                        em.set_content(body)

                        if self.send_email(em, smtp):
                            logging.info(f"Email sent successfully to {email_receiver[i]}")
                        else:
                            logging.error(f"Failed to send email to {email_receiver[i]}")

                QMessageBox.information(self, "Email Sent", "All emails have been successfully sent!")
                logging.info("All emails has been successfully sent")
            except smtplib.SMTPException as e:
                QMessageBox.warning(self, "Sending Email Error", "An SMTP error occurred while sending emails.")
                logging.error(f"SMTP error: {e}")

            except Exception as e:
                QMessageBox.warning(self, "Sending Email Error", "An unexpected error occurred while sending emails.")
                logging.error(f"Unexpected error: {e}")

    def prepare_email_body(self, row, date_sent):
        # Prepares the content/body of an email
        employee_number = row['EmpNo']
        biometrics_number = row['BioNum']
        employee_name = row['EmpName']
        basic_salary = row['Basic']
        present_days = int(float(row['Present Days']))
        daily_rate = row.get('Rate', 'Missing')
        ordinary_day_overtime = row.get('OrdinaryDayOT', 'N/A')
        overtime_earnings = row['OT_Earn']

        body = f"""
        Dear {employee_name},

            Below are your payroll details for the period {date_sent}.

            Employee Information:

            Employee Number: {employee_number}
            Biometrics Number: {biometrics_number}
            Employee Name: {employee_name}

            Attendance & Earnings:

            Daily Rate: {daily_rate} PHP
            Basic Salary: {basic_salary} PHP
            Days Present: {present_days} days
            Ordinary Day Overtime: {ordinary_day_overtime} hrs
            Overtime Earnings: {overtime_earnings} PHP

        If you have any questions or need further clarification regarding your payroll, please feel free to reach out to the HR department.

        Thank you for your hard work and dedication.
        """

        return body

    def send_email(self, em, smtp):
        # Sends email to each receiver
        try:
            smtp.sendmail(em['From'], em['To'], em.as_string())
        except Exception as e:
            logging.warning(f"Failed to send email to {em['To']}: {e}")
            return False
        return True