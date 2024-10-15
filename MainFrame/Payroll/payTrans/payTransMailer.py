from MainFrame.Resources.lib import *
from email.message import EmailMessage
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_session import UserSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

            # # Tentative Email Receiver
            # email_receiver = [
            #     'badlonmazeclarion@gmail.com', 'berri@temp-inbox.me', 'leghtk@temp-inbox.me',
            #     'xrxnkb@temp-inbox.me', 'nqiivl@temp-inbox.me', 'ndliida@temp-inbox.me',
            #     'zizbwh@temp-inbox.me', 'nbajd@temp-inbox.me', 'yvycx@temp-inbox.me',
            #     'hhxrvjb@temp-inbox.me', 'zkxjsvp@temp-inbox.me', 'yojktw@temp-inbox.me',
            #     'qbthp@temp-inbox.me', 'sauylfh@temp-inbox.me', 'uergjx@temp-inbox.me',
            #     'zurejm@temp-inbox.me', 'rsipc@temp-inbox.me', 'ueuzo@temp-inbox.me',
            #     'ojfivuv@temp-inbox.me', 'bnlxe@temp-inbox.me', 'llpozv@temp-inbox.me',
            #     'ezziysc@temp-inbox.me', 'nqhjau@temp-inbox.me', 'elwaslh@temp-inbox.me',
            #     'fuxgr@temp-inbox.me', 'oyfyrs@temp-inbox.me', 'tzaijwj@temp-inbox.me',
            #     'ckquilw@temp-inbox.me', 'evaivh@temp-inbox.me', 'bwnpyc@temp-inbox.me',
            #     'xksucn@temp-inbox.me', 'qwlxxm@temp-inbox.me', 'jaeyry@temp-inbox.me',
            #     'azdgw@temp-inbox.me', 'pdeax@temp-inbox.me', 'tzixev@temp-inbox.me',
            #     'fdqqpos@temp-inbox.me', 'duqqwe@temp-inbox.me', 'cblye@temp-inbox.me',
            #     'qgduswf@temp-inbox.me', 'shandee@temp-inbox.me', 'riuio@temp-inbox.me',
            #     'usoshwkw@temp-inbox.me', 'vaoajwnq@temp-inbox.me', 'jsoctsja@temp-inbox.me',
            #     'ja0ajalqk@temp-inbox.me', 'kapahwiqjq@temp-inbox.me', 'qpau@temp-inbox.me',
            #     'gajaja@temp-inbox.me', 'gajana@temp-inbox.me', 'ua8agqq@temp-inbox.me',
            #     'bziahaa@temp-inbox.me', 'baiaha@temp-inbox.me', 'hsisbwjs@temp-inbox.me',
            #     'oaowjw@temp-inbox.me', 'hajaha@temp-inbox.me', 'haisha@temp-inbox.me',
            #     'bzis@temp-inbox.me', 'bskana@temp-inbox.me', 'hssh@temp-inbox.me',
            #     'uu@temp-inbox.me', 'lizabeth@temp-inbox.me'
            # ]

            email_receiver = ['rodelcuyag123@gmail.com', 'jhayemcalleja011@gmail.com', 'badlonmazeclarion@gmail.com']

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
        employee_name = row['EmpName']

        # Ordinary Day
        present_days = int(float(row['Present Days']))
        basic_pay = row['RegDay_Earn']
        overtime_hours = int(float(row['OrdinaryDayOT']))
        overtime_earnings = row['OT_Earn']
        night_diff_hours = int(float(row['Regular Day Night Diff']))
        night_diff_earnings = row['RegDayNightDiffEarn']
        night_diff_ot_hours = int(float(row['Regular Day Night Diff OT']))
        night_diff_ot_earnings = row['RegDayNightDiffOTEarn']

        # Rest Day/Special Holiday
        sun_spcl_day_hours = int(float(row['Rest Day Hours']))
        sun_spcl_day_earnings = row['RestDay_Earn']
        sun_spcl_day_ot_hours = int(float(row['Rest Day OT Hours']))
        sun_spcl_day_ot_earnings = row['RestDayOT_Earn']
        sun_spcl_day_nd_hours = int(float(row['Rest Day Night Diff Hours'])) + int(float(row['Rest Day Night Diff OT']))
        sun_spcl_day_nd_earnings = float(row['RestDayND_Earn']) + float(row['RestDayNDOT_Earn'])

        # Regular Holiday
        total_holiday_hours = sum([float(row['Holiday Hours']), float(row['Holiday Night Diff Hours']),
                                   float(row['Holiday OT Hours']), float(row['Holiday Night Diff OT'])])
        total_holiday_earnings = sum([float(row['HolidayDay_Earn']), float(row['HolidayDayOT_Earn']),
                                      float(row['HolidayDayND_Earn']), float(row['HolidayNDOT_Earn'])])
        holiday_hours = int(total_holiday_hours)
        holiday_earnings = total_holiday_earnings

        # Deductions
        sss_loan = float(row['sss_loan'])
        pagibig_loan = float(row['pag_ibig_loan'])
        cash_advance = float(row['cash_advance'])
        canteen = float(row['canteen'])
        tax = float(row['tax'])
        clinic = float(row['clinic'])
        arayata_annual = float(row['arayata_manual'])
        hmi = float(row['hmi'])
        funeral = float(row['funeral'])
        voluntary = float(row['voluntary'])
        sss_contribution = float(row['sss_contribution'])
        medicare_philhealth = float(row['medicare_philhealth'])
        pag_ibig = float(row['pag_ibig'])

        total_deductions = sum([sss_loan, sss_contribution, pag_ibig, pagibig_loan, cash_advance, canteen, tax,
                                medicare_philhealth])

        gross_pay = float(row['Gross_Income'])
        net_pay = round(gross_pay - total_deductions, 2)

        # stylesheet for html body
        styles = """
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 14px;
                padding: 15px;
              }
              
            table {
                border-collapse: collapse;
                width: 95%;
                margin-left: auto;
                margin-right: auto;
            }
              
            th, td {
                border: 1px solid black;
                padding: 5px;
            }
        
        
            .employee-info td {
                text-align: left;
                font-weight: bold;
            }
              
            .main-table th, .others-table th {
                font-weight: normal;
                text-align: left;
            }
              
            .others-table td, .main-table td {
                text-align: right;
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
                
                <br>
                
                <table class="employee-info">
                    <tr>
                        <td>Employee Name</td>
                        <td>{employee_name}</td>
                        <td>Payroll cut off period</td>
                        <td>JULY 1 - 15, 2024</td>
                    </tr>
                    <tr>
                        <td>Employee Number</td>
                        <td>{employee_number}</td>
                        <td>Department</td>
                        <td>SHELDAHL</td>
                    </tr>
                </table>
                
                <br>
                <br>
                
                <table class="main-table">
                  <tr>
                    <th colspan="3" style="text-align:center; background-color: #f0f0f0;"><b>E A R N I N G S</b></th>
                    <th rowspan="13" style="width:5%;"></th>
                    <th colspan="2" style="width:45%; text-align:center; background-color: #f0f0f0;"><b>D E D U C T I O N S</b></th>
                  </tr>
                  <tr>
                    <th>BASIC PAY</th>
                    <td style="width:10%;">{present_days}</td>
                    <td style="width:15%;">{basic_pay}</td>
                    <th>LATE/ABSENT</th>
                    <td style="width:15%;">0.00</td>
                  </tr>
                  <tr>
                    <th>OVERTIME</th>
                    <td>{overtime_hours}</td>
                    <td>{overtime_earnings}</td>
                    <th>SSS LOAN</th>
                    <td>{sss_loan}</td>
                  </tr>
                  <tr>
                    <th>SUN/SPCL DAY</th>
                    <td>{sun_spcl_day_hours}</td>
                    <td>{sun_spcl_day_earnings}</td>
                    <th>PAG-IBIG LOAN</th>
                    <td>{pagibig_loan}</td>
                  </tr>
                  <tr>
                    <th>SUN/SPCL OT</th>
                    <td>{sun_spcl_day_ot_hours}</td>
                    <td>{sun_spcl_day_ot_earnings}</td>
                    <th>CASH ADVANCE</th>
                    <td>{cash_advance}</td>
                  </tr>
                  <tr>
                    <th>SUN/SPCL NIGHT DIFF</th>
                    <td>{sun_spcl_day_nd_hours}</td>
                    <td>{sun_spcl_day_nd_earnings}</td>
                    <th>CANTEEN</th>
                    <td>{canteen}</td>
                  </tr>
                  <tr>
                    <th>NIGHT DIFF</th>
                    <td>{night_diff_hours}</td>
                    <td>{night_diff_earnings}</td>
                    <th>TAX</th>
                    <td>{tax}</td>
                  </tr>
                  <tr>
                    <th>NIGHT OT</th>
                    <td>{night_diff_ot_hours}</td>
                    <td>{night_diff_ot_earnings}</td>
                    <th>SSS</th>
                    <td>{sss_contribution}</td>
                  </tr>
                  <tr>
                    <th>HOLIDAY</th>
                    <td>{holiday_hours}</td>
                    <td>{holiday_earnings}</td>
                    <th>MEDICARE/PHILHEALTH</th>
                    <td>{medicare_philhealth}</td>        
                  </tr>
                  <tr>
                    <th>ALLOWANCE</th>
                    <td>0</td>
                    <td>0.00</td>
                    <th>PAG-IBIG</th>
                    <td>{pag_ibig}</td>        
                  </tr>
                  <tr>
                    <th>OTHERS(+)</th>
                    <td>0</td>
                    <td>0.00</td>
                    <th>OTHERS(-)</th>
                    <td>0.00</td>        
                  </tr>
                  <tr>
                    <td colspan="3" style="height:15px;"></td>
                    <td colspan="3" style="height:15px;"></td>
                  </tr>
                  <tr>
                    <th colspan="2"><b>GROSS PAY</b></th>
                    <td>₱{gross_pay}</td>
                    <th><b>TOTAL DEDUCTIONS</b></th>
                    <td>₱{total_deductions}</td> 
                  </tr>
                </table>
                
                <br>
                <br>
                
                <table>
                  <tr>
                    <th colspan="4" style="text-align: left; background-color: #f0f0f0;"><b>NETPAY</b></th>
                    <td colspan="2" style="text-align: right; width:50%;">₱{net_pay}</td>
                  </tr>
                </table>
                
                <br>
                <br>
                
                <table class="others-table">
                  <tr>
                      <th colspan="2" style="text-align:center; font-weight:bold; background-color: #f0f0f0;">O T H E R S (+)</th>
                      <th colspan="4" style="text-align:center; font-weight:bold; background-color: #f0f0f0;">O T H E R S (-)</th>
                  </tr>
                  <tr>
                      <th>TYLS</th>
                      <td style="width:12%;">0.00</td>
                      <th>CLINIC</th>
                      <td style="width:12%;">{clinic}</td>
                      <th>NTPECA CONTRI</th>
                      <td style="width:12%;">0.00</td>
                  </tr>
                  <tr>
                      <th>OS ALLOWANCE</th>
                      <td>0.00</td>
                      <th>ARAYATA ANNUAL</th>
                      <td>{arayata_annual}</td>
                      <th>LONG TERM</th>
                      <td>0.00</td>
                  </tr>
                  <tr>
                      <th>CBA ALLOWANCE</th>
                      <td>0.00</td>
                      <th>HMI</th>
                      <td>{hmi}</td>
                      <th>SHORT TERM</th>
                      <td>0.00</td>
                  </tr>
                  <tr>
                      <th>HAZARD PAY</th>
                      <td>0.00</td>
                      <th>FUNERAL</th>
                      <td>{funeral}</td>
                      <th>CFE</th>
                      <td>0.00</td>
                  </tr>
                  <tr>
                      <th>PA</th>
                      <td>0.00</td>
                      <th>VOLUNTARY</th>
                      <td>{voluntary}</td>
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
                
                <br>
                <br>
                
                <p>If you have any questions or need further clarification regarding your payroll, please feel free to reach out to the HR department.</p>
                
                <br>
                
                <p>Thanks and Best Regards,</p>
                <p>========================</p>
            
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
            QMessageBox.critical(self, "Email Sending Failed", f"Could not send email to {em['To']}: {str(e)}")
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