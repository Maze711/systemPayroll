from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.systemFunctions import globalFunction, single_function_logger

class BugReportModal(QDialog):
    def __init__(self):
        super(BugReportModal, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\bugReport.ui")
        loadUi(ui_file, self)
        self.setFixedSize(570, 370)

        self.user_session = UserSession().getALLSessionData()

        self.bugReportInputTxt = self.findChild(QPlainTextEdit, "bugReportInputTxt")

        self.btnSendReport.clicked.connect(self.sendBugReport)
        self.btnCancel.clicked.connect(self.cancelBtn)

    def cancelBtn(self):
        self.bugReportInputTxt.clear()
        self.close()

    @single_function_logger.log_function
    def sendBugReport(self, checked=False):
        bugReportTxt = self.bugReportInputTxt.toPlainText().strip()

        if not bugReportTxt or len(bugReportTxt) < 10:
            QMessageBox.warning(self, "Input Error", "Please enter at least 10 characters")
            return

        # Show wait message while being sent
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Sending the report. Please wait...")
        msg_box.setWindowTitle("Sending Report")
        msg_box.setStandardButtons(QMessageBox.NoButton) # disabling close button
        msg_box.show()
        QApplication.processEvents() # Ensure the message box is shown

        email_sender = str(self.user_session["user_email"])
        email_password = str(self.user_session["user_email_password"])

        # Email Receivers
        developers_email = ['rodelcuyag123@gmail.com', 'badlonmazeclarion@gmail.com', 'jhayemcalleja011@gmail.com']

        date_sent = date.today()

        subject = f'Bug Report - {date_sent}'
        body = self.prepare_email_body(bugReportTxt)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)

                for each_email in developers_email:
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = each_email
                    em['Subject'] = subject
                    em.set_content(body)

                    if not self.send_email(em, smtp):
                        logging.error(f"Failed to send email to {each_email}.")

            msg_box.done(QMessageBox.Ok) # closes the wait message

            QMessageBox.information(self, "Report Sent", "Report sent successfully!")
            self.cancelBtn()
            logging.info("Bug Report has been sent successfully!")
        except smtplib.SMTPException as e:
            QMessageBox.warning(self, "Sending Bug Report Error", "An SMTP error occurred while sending emails.")
            logging.error(f"SMTP error: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Sending Bug Report Error", "An unexpected error occurred while sending "
                                                                      "bug report.")
            logging.error(f"Unexpected error: {e}")

    def prepare_email_body(self, bug_content):

        body = f"""
        Dear Developers,
            
            I hope this email finds you well. I would like to report a bug that I encountered in the system.
                
            Bug Description:
            
                {bug_content}
                    
        Thank you for your assistance."""

        return body

    @single_function_logger.log_function
    def send_email(self, em, smtp):
        # Sends email to each receiver
        try:
            smtp.sendmail(em['From'], em['To'], em.as_string())
        except Exception as e:
            logging.warning(f"Failed to send email to {em['To']}: {e}")
            return False
        return True