from MainFrame.Resources.lib import *
from MainFrame.FILE201.Employee_List.employeeList import EmployeeList
from MainFrame.fontLoader import load_fonts
from MainFrame.TimeKeeping.datImporter.dialogLoader import dialogModal
from MainFrame.TimeKeeping.payTimeSheetImporter.payTimeSheetImporter import PayrollDialog
from MainFrame.TimeKeeping.dateChange.dateChange import DateChange
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_auth import UserAuthentication
from MainFrame.Database_Connection.DBConnection import test_databases_connection
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.bugReport import BugReportModal

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

        self.open_dialogs = [] # Tracks the open dialog

        self.isLoggedIn = False
        self.btnLogOut = self.findChild(QPushButton, "btnLogOut")

        self.btnReportBug = self.findChild(QPushButton, "btnReportBug")

        self.authentication = UserAuthentication()
        self.user_session = UserSession()

        self.functions = self
        self.employee_list_window = None
        self.datechange = None
        self.timekeeping_window = None
        self.payroll_window = None
        self.bugReportModal = None

        # Window Connections
        self.btnEmployeeList.clicked.connect(self.employeeWindow)
        self.btnPayRoll.clicked.connect(self.openPayRoll)
        self.btnTimeKeeping.installEventFilter(self)
        self.btnReportBug.clicked.connect(self.openBugReportModal)
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

        self.btnSignUp.clicked.connect(lambda: self.authentication.signUpUser(self))
        self.btnLogin.clicked.connect(lambda: self.authentication.logInUser(self))
        self.btnContinue.clicked.connect(lambda: self.authentication.verifyExistingUser(self))
        self.btnResetPassword.clicked.connect(lambda: self.authentication.resetUserPassword(self))
        self.btnLogOut.clicked.connect(self.loggedOut)

        self.authentication.isUserAlreadyLoggedIn(self, self.isLoggedIn)

    def loggedOut(self):
        message = QMessageBox.question(self, "Log out", "Are you sure you want to log out?",
                             QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            QTimer.singleShot(1000, self.loggedOutSuccessfully)

    def loggedOutSuccessfully(self):
        self.isLoggedIn = False
        self.authentication.isUserAlreadyLoggedIn(self, self.isLoggedIn)

        # Close all open dialogs
        for dialog in self.open_dialogs:
            if dialog.isVisible():
                dialog.close()

        self.open_dialogs.clear() # Clears the list once closed
        self.user_session.clearSession() # Clears the user session data
        self.switchPageAndResetInputs(self.loginPage)
        QMessageBox.information(self, "Log out", "You have been logged out.")

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

    def disableAllNavButtons(self):
        buttons = ['btnEmployeeList', 'btnPayRoll', 'btnTimeKeeping']
        disableStyle = 'background-color: "#f1f1f1"; color: gray;'

        for buttonName in buttons:
            button = self.findChild(QPushButton, buttonName)
            button.setEnabled(False)
            button.setStyleSheet(disableStyle)
            if buttonName == 'btnTimeKeeping':
                button.removeEventFilter(self)

    def enableNavButton(self, buttonName):
        button = self.findChild(QPushButton, buttonName)
        enableStyle = '''
                QPushButton {
                    background-color: white;
                    color: black;
                }
                QPushButton:hover {
                    background-color: "#485994";
                    color: white;
                    border: 2px solid white;
                }
            '''
        if button:
            button.setEnabled(True)
            button.setStyleSheet(enableStyle)
            if buttonName == 'btnTimeKeeping':
                button.installEventFilter(self)


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
            self.open_dialogs.append(self.employee_list_window)
        self.employee_list_window.show()

    def openDateChange(self):
        if self.datechange is None:
            self.datechange = DateChange()
        self.datechange.exec_()

    def openTimeLogger(self):
        if self.timekeeping_window is None:
            self.timekeeping_window = dialogModal()
        self.timekeeping_window.exec_()

    def openPayRoll(self):
        if self.payroll_window is None:
            self.payroll_window = PayrollDialog(self)
        self.payroll_window.exec_()

    def openBugReportModal(self):
        if self.bugReportModal is None:
            self.bugReportModal = BugReportModal()
        self.bugReportModal.exec_()

def main():
    try:
        app = QApplication(sys.argv)
        test_databases_connection() # ensures database connection
        main_window = MainWindow()
        load_fonts()
        main_window.show()
        app.exec_()
    except Exception as e:
        logging.error("Error occurred while loading application: %s", str(e))
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()