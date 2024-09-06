import os.path

from MainFrame.Resources.lib import *
from email.utils import formataddr
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.systemFunctions import globalFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class BugReportModal(QDialog):
    def __init__(self):
        super(BugReportModal, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\bugReport.ui")
        loadUi(ui_file, self)
        self.setFixedSize(570, 480)

        self.user_session = UserSession().getALLSessionData()

        self.attachment_scroll_area = self.findChild(QtWidgets.QScrollArea, 'attachment_scroll_area')
        self.scroll_layout = self.scroll_contents.layout()

        self.bugReportInputTxt = self.findChild(QPlainTextEdit, "bugReportInputTxt")

        self.btnAttachFiles.clicked.connect(self.attach_files)
        self.btnSendReport.clicked.connect(self.sendBugReport)
        self.btnCancel.clicked.connect(self.cancelBtn)

        # Store attachments
        self.attachments = []

    def attach_files(self):
        """Handles all the attached files and append them"""
        if len(self.attachments) > 3:
            QMessageBox.warning(self, 'Limit Reached', 'You can only attach up to 3 files.')
            return

        files, _ = QFileDialog.getOpenFileNames(self, 'Select Files')

        if files:
            for file in files:
                if len(self.attachments) < 3:
                    self.attachments.append(file)
                    self.add_attachment_container(file)
                else:
                    QMessageBox.warning(self, 'Limit Reached', 'You can only attach up to 3 files.')
                    break

    def add_attachment_container(self, file_path):
        """Adds a container for file if there's any attached files"""
        file_name = os.path.basename(file_path)

        # Creates an attachment container for each uploaded attachment
        attachment_container = QWidget(self)
        attachment_layout = QHBoxLayout(attachment_container)
        attachment_container.setStyleSheet("background-color: #cccccc; border-radius: 5px;")
        attachment_container.setMaximumHeight(50)
        attachment_layout.setContentsMargins(10, 0, 10, 0)
        
        # Displays the file name
        file_label = QLabel(file_name, self)
        file_label.setStyleSheet("font-family: Poppins; font-size: 12px;")
        attachment_layout.addWidget(file_label)

        # Creates remove Attachment button
        remove_button = QPushButton('x', self)
        remove_button.setFixedSize(30, 30)
        remove_button.setCursor(Qt.PointingHandCursor)
        remove_button.setStyleSheet("font-family: Poppins; font-size: 25px; color: black; "
                                    "background-color: none; border: none;")
        remove_button.clicked.connect(lambda: self.remove_attachment(file_path, attachment_container))
        attachment_layout.addWidget(remove_button)

        self.scroll_layout.addWidget(attachment_container)

        if len(self.attachments) > 0:
            self.attachMessage.hide()
            return

    def remove_attachment(self, file_path, attachment_container):
        # Remove the file from the attachment list and the widget
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            self.scroll_layout.removeWidget(attachment_container)
            attachment_container.deleteLater()

        if len(self.attachments) == 0:
            self.attachMessage.show()

    def sendBugReport(self):
        subjectTxt = self.subjectTxt.text().strip()
        bugReportTxt = self.bugReportInputTxt.toPlainText().strip()

        if not subjectTxt:
            QMessageBox.warning(self, "Input Error", "Please fill out the Subject!")
            return

        if not bugReportTxt or len(bugReportTxt) < 10:
            QMessageBox.warning(self, "Input Error", "Please enter at least 10 characters!")
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

        subject = subjectTxt
        body = self.prepare_email_body(bugReportTxt)

        context = ssl.create_default_context()

        msg = MIMEMultipart()
        msg['From'] = formataddr((f"{sender_name}", f"{email_sender}"))  # Displays the user_name as sender
        msg['Bcc'] = ', '.join(developers_email)  # Concatenates all dev emails
        msg['Subject'] = subject
        msg.attach(MIMEText(body, _subtype='html'))

        # Attach Files in email
        for attachment in self.attachments:
            with open(attachment, 'rb') as file:
                part = MIMEApplication(file.read())
                part['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(attachment))
                msg.attach(part)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)

                if self.send_email(msg, smtp):
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

    def send_email(self, msg, smtp):
        # Sends email to each receiver
        try:
            smtp.send_message(msg)
        except Exception as e:
            logging.warning(f"Failed to send email: {e}")
            return False
        return True

    def cancelBtn(self):
        """Clears the bug report inputs and removes all attachments before closing the dialog"""
        # Clear the text input
        self.bugReportInputTxt.clear()
        self.subjectTxt.clear()

        # Remove all attachment containers and clear the attachments list
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget and widget is not self.attachMessage:
                    self.scroll_layout.removeWidget(widget)
                    widget.deleteLater()

        self.attachments.clear()
        self.attachMessage.show()
        self.close()