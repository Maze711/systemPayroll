from MainFrame.Resources.lib import *

from FILE201.Employee_List.employeeList import EmployeeList
from MainFrame.fontLoader import load_fonts
from TimeKeeping.datImporter.dialogLoader import dialogModal
from TimeKeeping.payTimeSheetImporter.payTimeSheetImporter import PayrollDialog
from TimeKeeping.dateChange.dateChange import DateChange
from MainFrame.systemFunctions import globalFunction, single_function_logger

from MainFrame.Database_Connection.DBConnection import create_connection

# Setup logging for application load duration
duration_logger = logging.getLogger('DurationLogger')
duration_logger.setLevel(logging.DEBUG)
duration_file_handler = logging.FileHandler('application_duration.log', mode='w')
duration_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
duration_file_handler.setFormatter(duration_formatter)
duration_logger.addHandler(duration_file_handler)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\Main.ui")
        loadUi(ui_file, self)
        self.setFixedSize(800, 600)

        self.isLoggedIn = False
        self.verifiedUsername = None
        self.btnLogOut = self.findChild(QPushButton, "btnLogOut")

        self.functions = self
        self.employee_list_window = None
        self.datechange = None
        self.timekeeping_window = None
        self.payroll_window = None

        # Window Connections
        self.btnEmployeeList.clicked.connect(self.employeeWindow)
        self.btnPayRoll.clicked.connect(self.openPayRoll)
        self.btnTimeKeeping.installEventFilter(self)
        self.additional_buttons_container = None

        # Routing Pages
        page_buttons = {
            self.btnSignUpHere: self.signUpPage,
            self.btnLoginHere: self.loginPage,
            self.btnForgotPass: self.forgotPassPage,
            self.btnBackToLogin: self.loginPage,
            self.btnBackToLogin_2: self.loginPage
        }

        for button, targetPage in page_buttons.items():
            button.clicked.connect(lambda _, page=targetPage: self.switchPageAndResetInputs(page))

        self.cbShowLogInPass.stateChanged.connect(lambda state: self.showPassword(state, 'login'))
        self.cbShowSignUpPass.stateChanged.connect(lambda state: self.showPassword(state, 'signup'))
        self.cbShowForgotPass.stateChanged.connect(lambda state: self.showPassword(state, 'forgot'))

        self.btnSignUp.clicked.connect(self.signUpUser)
        self.btnLogin.clicked.connect(self.logInUser)
        self.btnContinue.clicked.connect(self.verifyExistingUser)
        self.btnResetPassword.clicked.connect(self.resetUserPassword)
        self.btnLogOut.clicked.connect(self.loggedOut)

        self.isUserAlreadyLoggedIn(self.isLoggedIn)


    @single_function_logger.log_function
    def logInUser(self, checked=False):
        username = self.txtUsername.text()
        password = self.txtPassword.text()

        # Input Validations
        if not username.strip() or not password.strip():
            QMessageBox.warning(self, "Input Error", "Please input all fields!")
            return
        elif self.isUsernameNotExist(username):
            QMessageBox.warning(self, "Username does not exist",
                                "Username does not exist, please sign up first!")
            return
        elif not self.isCorrectPassword(username, password):
            QMessageBox.warning(self, "Incorrect Password",
                                "The password you entered is incorrect. Please try again!")
            return

        QMessageBox.information(self, "Success","Login Successful")

        self.isLoggedIn = True
        self.isUserAlreadyLoggedIn(self.isLoggedIn)

        # Enable navigation buttons based on the user's role
        user_role = self.getUserRole(username)
        if user_role == 'HR':
            self.enableNavButton('btnEmployeeList')
        elif user_role == 'TimeKeeper':
            self.enableNavButton('btnTimeKeeping')
        elif user_role in ['Accountant', 'Pay Master 1', 'Pay Master 2', 'Pay Master 3']:
            self.enableNavButton('btnPayRoll')

        return

    @single_function_logger.log_function
    def signUpUser(self, checked=False):
        username = self.txtUsernameSignUp.text()
        pre_password = self.txtPrePassword.text()
        password = self.txtSignUpPassword.text()

        # Input Validations
        if not username.strip() or not pre_password.strip() or not password.strip():
            QMessageBox.warning(self, "Input Error", "Please input all fields!")
            return
        elif not self.isUsernameNotExist(username):
            QMessageBox.warning(self, "Input Error", "Username already exist!")
            return
        elif not self.isPasswordMatch(pre_password, password):
            QMessageBox.warning(self, "Input Error", "Passwords do not match!")
            return

        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return

            cursor = connection.cursor()
            insert_user_in_users_table = "INSERT INTO users (user_name, user_password) VALUES (%s, %s)"
            hashedPassword = self.getGeneratedHashPassword(password)
            values = (username, hashedPassword)

            cursor.execute(insert_user_in_users_table, values)
            connection.commit()

            QMessageBox.information(self, "Success", "Your account has been successfully created!")
            self.switchPageAndResetInputs(self.loginPage)
            return

        except Error as e:
            logging.error(f"Error Signing Up/Inserting User: {e}")
            return

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def verifyExistingUser(self):
        username = self.txtUsernameForgot.text()

        # Input Validations
        if not username.strip():
            QMessageBox.warning(self, "Input Error", "Please enter your username!")
            return
        elif self.isUsernameNotExist(username):
            QMessageBox.warning(self, "Input Error", "Username does not exist!")
            return

        QMessageBox.information(self, "Success", "Your account has been verfied!")
        self.switchPageAndResetInputs(self.resetPassPage)
        self.setVerifiedUserName(username)

    def setVerifiedUserName(self, username):
        self.verifiedUsername = username

    def getVerifiedUserName(self):
        return self.verifiedUsername

    @single_function_logger.log_function
    def resetUserPassword(self, checked=False):
        pre_new_password = self.txtPreNewPassword.text()
        new_password = self.txtNewPassword.text()

        # Input Validations
        if not pre_new_password.strip() or not new_password.strip():
            QMessageBox.warning(self, "Input Error", "Please input all fields!")
            return
        elif not self.isPasswordMatch(pre_new_password, new_password):
            QMessageBox.warning(self, "Input Error", "Passwords do not match!")
            return

        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return

            cursor = connection.cursor()
            update_user_password_in_users_table = "UPDATE users SET user_password = %s WHERE user_name = %s"
            username = self.getVerifiedUserName()
            hashedPassword = self.getGeneratedHashPassword(new_password)
            values = (hashedPassword, username)

            cursor.execute(update_user_password_in_users_table, values)
            connection.commit()

            QMessageBox.information(self, "Success", "Your password has been reset successfully!")
            self.switchPageAndResetInputs(self.loginPage)
            return

        except Error as e:
            logging.error(f"Error Resetting user password: {e}")
            return

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")


    @single_function_logger.log_function
    def getUserRole(self, username):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return
            cursor = connection.cursor()
            fetch_user_role_in_users_table = "SELECT user_role FROM users WHERE user_name = %s"
            cursor.execute(fetch_user_role_in_users_table, (username, ))
            result = cursor.fetchone()

            return result[0]

        except Error as e:
            logging.error(f"Error fetching user role: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    @single_function_logger.log_function
    def isCorrectPassword(self, username, password):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return
            cursor = connection.cursor()
            fetch_password_in_users_table = "SELECT user_password FROM users WHERE user_name = %s"
            cursor.execute(fetch_password_in_users_table, (username, ))
            result = cursor.fetchone()

            # Fetch and encoded stored hashed password
            stored_hashed_password = result[0].encode('utf-8')

            # Checks the inputted password and the hash password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                return True
            else:
                return False

        except Error as e:
            logging.error(f"Error fetching user password: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    @single_function_logger.log_function
    def isUsernameNotExist(self, username, checked=False):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return False

            cursor = connection.cursor()
            fetch_username_in_users_table = "SELECT user_name FROM users WHERE user_name = %s"
            cursor.execute(fetch_username_in_users_table, (username, ))
            result = cursor.fetchone()

            if result:
                return False

            return True

        except Error as e:
            logging.error(f"Error fetching username: {e}")
            return False

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def isPasswordMatch(self, pre_password, password):
        if pre_password != password:
            return False

        return True

    def getGeneratedHashPassword(self, password):
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashedPassword.decode('utf-8')

    def showPassword(self, state, page):
        passwordFields = {
            'login': ['txtPassword'],
            'signup': ['txtPrePassword', 'txtSignUpPassword'],
            'forgot': ['txtPreNewPassword', 'txtNewPassword']
        }

        fields = passwordFields.get(page, [])

        for widgetName in fields:
            passwordField = self.findChild(QLineEdit, widgetName)
            if passwordField:
                if state == Qt.Checked:
                    passwordField.setEchoMode(QLineEdit.Normal)
                else:
                    passwordField.setEchoMode(QLineEdit.Password)

    def switchPageAndResetInputs(self, targetPage):
        # Clears all QLineEdit upon page switching
        for widget in self.currentPage().findChildren(QLineEdit):
            widget.setText("")

        # Unchecks all QCheckBox upon page switching
        for widget in self.findChildren(QCheckBox):
            widget.setCheckState(Qt.Unchecked)

        self.stackedWidget.setCurrentWidget(targetPage)

    def currentPage(self):
        return self.stackedWidget.currentWidget()


    def enableNavButton(self, buttonName):
        button = self.findChild(QPushButton, buttonName)
        enableStyle = 'background-color: white; color: black;'

        if button:
            button.setEnabled(True)
            button.setStyleSheet(enableStyle)
            if buttonName == 'btnTimeKeeping':
                button.installEventFilter(self)

    def disableAllNavButtons(self):
        buttons = ['btnEmployeeList', 'btnPayRoll', 'btnTimeKeeping']
        disableStyle = 'background-color: "#f1f1f1"; color: gray;'

        for buttonName in buttons:
            button = self.findChild(QPushButton, buttonName)
            button.setEnabled(False)
            button.setStyleSheet(disableStyle)
            if buttonName == 'btnTimeKeeping':
                button.removeEventFilter(self)

    def loggedOut(self):
        message = QMessageBox.question(self, "Log out", "Are you sure you want to log out?",
                             QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            QTimer.singleShot(1000, self.loggedOutSuccessfully)

    def loggedOutSuccessfully(self):
        self.isLoggedIn = False
        self.isUserAlreadyLoggedIn(self.isLoggedIn)
        self.switchPageAndResetInputs(self.loginPage)
        QMessageBox.information(self, "Log out", "You have been logged out.")

    def isUserAlreadyLoggedIn(self, isLoggedIn):
        if isLoggedIn is False:
            self.btnLogOut.setVisible(False)
            self.disableAllNavButtons()
            self.mainBody.setVisible(True)
        else:
            self.btnLogOut.setVisible(True)
            self.mainBody.setVisible(False)


    def eventFilter(self, source, event):
        if source == self.btnTimeKeeping and not source.isEnabled():
            return False

        if source == self.btnTimeKeeping:
            if event.type() == QEvent.Enter:
                self.showAdditionalButtons()
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.checkAndHideAdditionalButtons)
        elif self.additional_buttons_container and source in self.additional_buttons_container.children():
            if event.type() == QEvent.HoverEnter:
                source.setStyleSheet("background-color: #344273; color: white; font-family: Poppins;")
            elif event.type() == QEvent.HoverLeave:
                source.setStyleSheet("background-color: white;")
            if event.type() == QEvent.Enter:
                return True
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.checkAndHideAdditionalButtons)
        return super(MainWindow, self).eventFilter(source, event)

    def showAdditionalButtons(self):
        self.hideAdditionalButtons()

        button_width = 150
        button_height = 40
        frame_width = button_width + 20
        frame_height = 2 * button_height + 25
        left_offset = self.btnTimeKeeping.geometry().right() + 5
        top_offset = self.btnTimeKeeping.geometry().top()

        self.additional_buttons_container = QWidget(self)
        self.additional_buttons_container.setGeometry(left_offset, top_offset, frame_width, frame_height)
        self.additional_buttons_container.setStyleSheet("background-color: #DCE5FE; border: 1px solid gray; font-family: Poppins;")

        additional_button_texts = ["Date Change", "Time Logger"]
        for i, text in enumerate(additional_button_texts):
            button = QPushButton(text, self.additional_buttons_container)
            button.setGeometry(10, 10 + i * (button_height + 5), button_width, button_height)
            button.setStyleSheet("background-color: white;")
            button.installEventFilter(self)

            if text == "Date Change":
                button.clicked.connect(self.openDateChange)
            elif text == "Time Logger":
                button.clicked.connect(self.openTimeLogger)

        self.additional_buttons_container.show()

    def checkAndHideAdditionalButtons(self):
        if not (self.btnTimeKeeping.underMouse() or (self.additional_buttons_container and any(button.underMouse() for button in self.additional_buttons_container.children()))):
            self.hideAdditionalButtons()

    def hideAdditionalButtons(self):
        if self.additional_buttons_container:
            self.additional_buttons_container.hide()
            self.additional_buttons_container.deleteLater()
            self.additional_buttons_container = None

    def employeeWindow(self):
        if self.employee_list_window is None:
            self.employee_list_window = EmployeeList()
        self.employee_list_window.show()

    def openDateChange(self):
        if self.datechange is None:
            self.datechange = DateChange()
        self.datechange.show()

    def openTimeLogger(self):
        if self.timekeeping_window is None:
            self.timekeeping_window = dialogModal()
        self.timekeeping_window.show()

    def openPayRoll(self):
        if self.payroll_window is None:
            self.payroll_window = PayrollDialog()
        self.payroll_window.show()

def main():
    start_time = time.time()
    logging.debug("Starting application")

    try:
        app = QApplication(sys.argv)
        load_fonts()
        main_window = MainWindow()
        main_window.show()
    except Exception as e:
        logging.error("Error occurred while loading application: %s", str(e))
        print(f"Error occurred: {e}")
        sys.exit(1)

    end_time = time.time()
    duration = end_time - start_time
    duration_logger.info(f"Application loaded in {duration:.2f} seconds")
    print(f"Application loaded in {duration:.2f} seconds")

    app.exec_()

if __name__ == "__main__":
    main()
