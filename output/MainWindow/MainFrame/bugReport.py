from MainFrame.Resources.lib import *
from email.utils import formataddr
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

    # @single_function_logger.log_function
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
        msg_box.setStandardButtons(QMessageBox.NoButton)  # disabling close button
        msg_box.show()
        QApplication.processEvents()  # Ensure the message box is shown

        sender_name = str(self.user_session["user_name"])
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

                em = EmailMessage()
                em['From'] = formataddr((f"{sender_name}", f"{email_sender}"))  # Displays the user_name as sender
                em['Bcc'] = ', '.join(developers_email)  # Concatenates all dev emails
                em['Subject'] = subject
                em.add_alternative(body, subtype='html')

                if self.send_email(em, smtp):
                    msg_box.done(QMessageBox.Ok)  # closes the wait message on success
                    QMessageBox.information(self, "Report Sent", "Report sent successfully!")
                    self.cancelBtn()
                    logging.info("Bug Report has been sent successfully!")
                else:
                    msg_box.done(QMessageBox.Ok)
                    QMessageBox.warning(self, "Sending Bug Report Error",
                                        "Failed to send the report email. Please try again later.")
                    logging.error("Failed to send the report email.")
        except smtplib.SMTPException as e:
            msg_box.done(QMessageBox.Ok)
            QMessageBox.warning(self, "Sending Bug Report Error",
                                "An SMTP error occurred while sending emails.")
            logging.error(f"SMTP error: {e}")
        except Exception as e:
            msg_box.done(QMessageBox.Ok)
            QMessageBox.warning(self, "Sending Bug Report Error",
                                "An unexpected error occurred while sending the bug report.")
            logging.error(f"Unexpected error: {e}")

    def prepare_email_body(self, bug_content):

        body = f"""
            <html>
                <body>
                    <p>Dear Developers,</p>

                    <p>I hope this email finds you well. I would like to report a bug that I encountered in the system.</p>

                    <p><strong>Bug Description:</strong></p>
                    
                    <p>{bug_content}</p>

                    <p>Thank you for your assistance.</p>
                </body>
            </html>
        """

        return body

#     @single_function_logger.log_function
    def send_email(self, em, smtp):
        # Sends email to each receiver
        try:
            smtp.send_message(em)
        except Exception as e:
            logging.warning(f"Failed to send email: {e}")
            return False
        return True