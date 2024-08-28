import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_session import UserSession

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class EmailerProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data

        self.user_session = UserSession().getALLSessionData()

    def processSendingEmail(self):
        """ Processes sending email to all employees. """
        try:
            sender_name = str(self.user_session["user_name"])
            email_sender = str(self.user_session['user_email'])
            email_password = str(self.user_session['user_email_password'])

            # Tentative Email Receiver
            email_receiver = [
                'badlonmazeclarion@gmail.com', 'berri@temp-inbox.me', 'leghtk@temp-inbox.me',
                'xrxnkb@temp-inbox.me', 'nqiivl@temp-inbox.me', 'ndliida@temp-inbox.me',
                'zizbwh@temp-inbox.me', 'nbajd@temp-inbox.me', 'yvycx@temp-inbox.me',
                'hhxrvjb@temp-inbox.me', 'zkxjsvp@temp-inbox.me', 'yojktw@temp-inbox.me',
                'qbthp@temp-inbox.me', 'sauylfh@temp-inbox.me', 'uergjx@temp-inbox.me',
                'zurejm@temp-inbox.me', 'rsipc@temp-inbox.me', 'ueuzo@temp-inbox.me',
                'ojfivuv@temp-inbox.me', 'bnlxe@temp-inbox.me', 'llpozv@temp-inbox.me',
                'ezziysc@temp-inbox.me', 'nqhjau@temp-inbox.me', 'elwaslh@temp-inbox.me',
                'fuxgr@temp-inbox.me', 'oyfyrs@temp-inbox.me', 'tzaijwj@temp-inbox.me',
                'ckquilw@temp-inbox.me', 'evaivh@temp-inbox.me', 'bwnpyc@temp-inbox.me',
                'xksucn@temp-inbox.me', 'qwlxxm@temp-inbox.me', 'jaeyry@temp-inbox.me',
                'azdgw@temp-inbox.me', 'pdeax@temp-inbox.me', 'tzixev@temp-inbox.me',
                'fdqqpos@temp-inbox.me', 'duqqwe@temp-inbox.me', 'cblye@temp-inbox.me',
                'qgduswf@temp-inbox.me', 'shandee@temp-inbox.me', 'riuio@temp-inbox.me',
                'usoshwkw@temp-inbox.me', 'vaoajwnq@temp-inbox.me', 'jsoctsja@temp-inbox.me',
                'ja0ajalqk@temp-inbox.me', 'kapahwiqjq@temp-inbox.me', 'qpau@temp-inbox.me',
                'gajaja@temp-inbox.me', 'gajana@temp-inbox.me', 'ua8agqq@temp-inbox.me',
                'bziahaa@temp-inbox.me', 'baiaha@temp-inbox.me', 'hsisbwjs@temp-inbox.me',
                'oaowjw@temp-inbox.me', 'hajaha@temp-inbox.me', 'haisha@temp-inbox.me',
                'bzis@temp-inbox.me', 'bskana@temp-inbox.me', 'hssh@temp-inbox.me',
                'uu@temp-inbox.me', 'lizabeth@temp-inbox.me'
            ]

            total_data = min(len(self.data), len(email_receiver))

            date_sent = date.today()

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)

                for i in range(total_data):
                    per_email = self.data[i]
                    subject = f'Payroll Details - {date_sent}'
                    body = self.prepare_email_body(per_email, date_sent)

                    em = EmailMessage()
                    em['From'] = formataddr((f"{sender_name}", f"{email_sender}"))
                    em['To'] = email_receiver[i]
                    em['Subject'] = subject
                    em.add_alternative(body, subtype='html')

                    if self.send_email(em, smtp):
                        logging.info(f"Email sent successfully to {email_receiver[i]}")
                    else:
                        logging.error(f"Failed to send email to {email_receiver[i]}")

                    progress = int(((i + 1) / total_data) * 100)
                    self.progressChanged.emit(progress)
                    QThread.msleep(1)

                self.finished.emit("All emails have been successfully sent!")

        except smtplib.SMTPException as e:
            self.error.emit(f"SMTP error: {e}")

        except Exception as e:
            self.error.emit(f"Error in sending email: {e}")

    def prepare_email_body(self, row, date_sent):
        """ Prepares the content/body of an email"""
        employee_number = row['EmpNo']
        biometrics_number = row['BioNum']
        employee_name = row['EmpName']
        basic_salary = row['Basic']
        present_days = int(float(row['Present Days']))
        daily_rate = row.get('Rate', 'Missing')
        ordinary_day_overtime = row.get('OrdinaryDayOT', 'N/A')
        overtime_earnings = row['OT_Earn']

        # stylesheet for html body
        styles = """
        <style>
            body {
                font-family: arial, sans-serif;
            }
            table {
              border-collapse: collapse;
              width: 100%;
            }

            td, th {
              border: 1px solid #dddddd;
              text-align: left;
              padding: 8px;
              height: 10px;
            }

            .earningsTable td {
              text-align: right;
            }

            .othersTable td {
              text-align: right;
            }

            .deductionsTable td {
              text-align: right;
            }

            .earningsTable th {
              font-weight: normal;
            }

            .othersTable th {
              font-weight: normal;
            }

            .deductionsTable th {
              font-weight: normal;
            }
        </style>
        """

        html_body = f"""
        <html>
            <head>
                {styles}
            </head>
            <body>
                <p>Dear {employee_name},</p>

                <p>Below are your payroll details: </p>

                <table>
                    <tr>
                        <th>Employee Name</th>
                        <td>{employee_name}</td>
                        <th>Payroll cut off period</th>
                        <td> - </td>
                    </tr>
                    <tr>
                        <th>Employee Number</th>
                        <td>{employee_number}</td>
                        <th>Department</th>
                        <td>Company</td>
                    </tr>
                </table>

                <br>

                <table class="tables">
                    <tr>
                        <td style="border:none"></td>
                        <td style="border:none"></td>
                        <th><b>NET PAY</b></th>
                        <td>5,000</td>
                    </tr>
                    <tr>
                        <td>
                            <table class="earningsTable">
                                <tr>
                                  <th colspan="3"><b>Earnings</b></th>
                                </tr>
                                <tr>
                                  <th>BASIC PAY</th>
                                  <td>11</td>
                                  <td>{basic_salary}</td>
                                </tr>
                                <tr>
                                  <th>OVERTIME</th>
                                  <td>11</td>
                                  <td>{overtime_earnings}</td>
                                </tr>
                                <tr>
                                  <th>SUN/SPCL</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>SUN/SPCL OT</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>SUN NIGHT DIFF</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>NIGHT DIFF</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>NIGHT OT</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>HOLIDAY</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>ALLOWANCE</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th>OTHERS (+)</th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th></th>
                                  <td></td>
                                  <td></td>
                                </tr>
                                <tr>
                                  <th><b>GROSS PAY</b></th>
                                  <td>11</td>
                                  <td>5,000</td>
                                </tr>
                                <tr>
                                  <th></th>
                                  <td></td>
                                  <td></td>
                                </tr>
                            </table>
                        </td>
                    <td style="padding: 8px;"></td>
                    <td colspan="2">
                        <table class="deductionsTable">
                            <tr>
                              <th colspan="2"><b>DEDUCTIONS</b></th>
                            </tr>
                            <tr>
                              <th>LATE / ABSENT</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>SSS LOAN</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>PAG IBIG LOAN</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>CASH ADVANCE</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>CANTEEN</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>TAX</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>SSS</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>MEDICARE/PHILHEALTH</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>PAGIBIG</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th>OTHERS (+)</th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th></th>
                              <td></td>
                            </tr>
                            <tr>
                              <th><b>TOTAL DEDUCTIONS</b></th>
                              <td>5,000</td>
                            </tr>
                            <tr>
                              <th></th>
                              <td></td>
                            </tr>
                        </table>
                    </td>
                  </tr>
                </table>

                <br>
                <br>

                <table class="othersTable">
                    <tr>
                        <th style="text-align: center;" colspan="2"><b>OTHERS (+)</b></th>
                        <th style="text-align: center;" colspan="4"><b>OTHERS (+)</b></th>
                    </tr>
                    <tr>
                        <th>TYLS</th>
                        <td>0.00</td>
                        <th>CLINIC</th>
                        <td>0.00</td>
                        <th>NTPECA CONTRI</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>OS ALLOWANCE</th>
                        <td>0.00</td>
                        <th>ARAYATA ANNUAL</th>
                        <td>0.00</td>
                        <th>LONG TERM</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>CBA ALLOWANCE</th>
                        <td>0.00</td>
                        <th>HMI</th>
                        <td>0.00</td>
                        <th>SHORT TERM</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>HAZARD PAY</th>
                        <td>0.00</td>
                        <th>FUNERAL</th>
                        <td>0.00</td>
                        <th>CFE</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>PA</th>
                        <td>0.00</td>
                        <th>VOLUNTARY</th>
                        <td>0.00</td>
                        <th>GUARANTOR</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>HOL EARN/SUN ND</th>
                        <td>0.00</td>
                        <th>HDMF MP2</th>
                        <td>0.00</td>
                        <th>TRANSPO</th>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <th>BACKPAY</th>
                        <td>0.00</td>
                        <th>UD/AF</th>
                        <td>0.00</td>
                        <th>OTHERS</th>
                        <td>0.00</td>
                    </tr>
                </table>

                <p>If you have any questions or need further clarification regarding your payroll, please feel free to reach out to the HR department.</p>

                <p>Thank you for your hard work and dedication.</p>
            </body>
        </html>
        """

        # Inlining css styles to html body
        body = inline(html_body)

        return body

    def send_email(self, em, smtp):
        """ Sends email to each receiver """
        try:
            smtp.sendmail(em['From'], em['To'], em.as_string())
        except Exception as e:
            logging.warning(f"Failed to send email to {em['To']}: {e}")
            return False
        return True

class EmailerLoader(QDialog):
    def __init__(self, data, paytrans_window):
        super(EmailerLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        self.data = data

        self.paytrans_window = paytrans_window

        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = EmailerProcessor(self.data)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.emailProcessingFinished)
        self.worker.error.connect(self.emailProcessingError)
        self.thread.started.connect(self.worker.processSendingEmail)
        self.thread.start()

        self.move_to_bottom_right()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def emailProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.information(self.paytrans_window, "Email Sent", "All emails have been successfully sent!")
        self.close()

    def emailProcessingError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.paytrans_window, "Sending Email Error", f"An unexpected error occurred while sending emails:\n{error}")
        self.close()
    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)