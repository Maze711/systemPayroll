import functools
import psutil

import threading
from MainFrame.Database_Connection.notification_listener import NotificationService
from MainFrame.Payroll.paytimeSheet.paytimeSheet import PaytimeSheet
# Import classes
from MainFrame.Resources.lib import *
from MainFrame.FILE201.Employee_List.employeeList import EmployeeList
from MainFrame.fontLoader import load_fonts
from MainFrame.TimeKeeping.datImporter.dialogLoader import dialogModal
from MainFrame.TimeKeeping.dateChange.dateChange import DateChange
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.user_auth import UserAuthentication
from MainFrame.Database_Connection.user_session import UserSession
from MainFrame.bugReport import BugReportModal
from MainFrame.FILE201.file201_Function.listFunction import ListFunction

class MainWindowFunctions(QMainWindow):
    def __init__(self):
        super(MainWindowFunctions, self).__init__()
        self.notification_service = NotificationService()
        self.notification_thread = threading.Thread(target=self.notification_service.poll_notifications)
        self.server_thread = threading.Thread(target=self.notification_service.start_server)
        self.notification_thread.start()
        self.server_thread.start()

    @functools.cache
    def get_button_stylesheet(self, enabled=True):
        return '''
            QPushButton {
                background-color: white;
                color: black;
            }
            QPushButton:hover {
                background-color: #485994;
                color: white;
                border: 2px solid white;
            }
        '''

    def log_memory_usage(self, stage):
        process = psutil.Process()
        mem_info = process.memory_info()

    def initialize_widgets(self):
        self.open_dialogs = []
        self.isLoggedIn = False
        self.authentication = UserAuthentication()
        self.user_session = UserSession()
        self.session_at_main = UserSession().getALLSessionData()
        self.employee_list_window = None
        self.datechange = None
        self.timekeeping_window = None
        self.payroll_window = None
        self.bugReportModal = None
        self.btnNotification = None
        self.additional_buttons_container = None

        self.btnLogOut = self.findChild(QPushButton, "btnLogOut")
        self.btnReportBug = self.findChild(QPushButton, "btnReportBug")
        self.btnNotification = self.findChild(QPushButton, "btnNotification")
        self.btnLogin = self.findChild(QPushButton, "btnLogin")

    def setup_connections(self):
        self.btnEmployeeList.clicked.connect(self.employeeWindow)
        self.btnPayRoll.clicked.connect(self.openPayRoll)
        self.btnTimeKeeping.installEventFilter(self)
        self.btnReportBug.clicked.connect(self.openBugReportModal)
        self.cbShowLogInPass.stateChanged.connect(lambda state: self.showPassword(state, 'login'))
        self.cbShowSignUpPass.stateChanged.connect(lambda state: self.showPassword(state, 'signup'))
        self.cbShowForgotPass.stateChanged.connect(lambda state: self.showPassword(state, 'forgot'))
        self.btnSignUp.clicked.connect(lambda: self.authentication.signUpUser(self))
        self.btnLogin.clicked.connect(lambda: self.authentication.logInUser(self))
        self.btnContinue.clicked.connect(lambda: self.authentication.verifyExistingUser(self))
        self.btnResetPassword.clicked.connect(lambda: self.authentication.resetUserPassword(self))
        self.btnLogOut.clicked.connect(self.loggedOut)
        self.authentication.isUserAlreadyLoggedIn(self, self.isLoggedIn)

    def setup_page_buttons(self):
        page_buttons = {
            self.btnSignUpHere: self.signUpPage,
            self.btnLoginHere: self.loginPage,
            self.btnForgotPass: self.forgotPassPage,
            self.btnBackToLogin: self.loginPage,
            self.btnBackToLogin_2: self.loginPage
        }
        for button, targetPage in page_buttons.items():
            button.clicked.connect(lambda _, page=targetPage: self.switchPageAndResetInputs(page))

    def keyPressEvent(self, event):
        if self.btnLogin.isEnabled() and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.btnLogin.click()
        else:
            super().keyPressEvent(event)

    def loggedOut(self):
        message = QMessageBox.question(self, "Log out", "Are you sure you want to log out?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.loggedOutSuccessfully()

    def loggedOutSuccessfully(self):
        self.isLoggedIn = False
        self.authentication.isUserAlreadyLoggedIn(self, self.isLoggedIn)
        for dialog in self.open_dialogs:
            if dialog.isVisible():
                dialog.close()
        self.open_dialogs.clear()
        self.user_session.clearSession()
        self.switchPageAndResetInputs(self.loginPage)
        QMessageBox.information(self, "Log out", "You have been logged out.")
        self.btnLogin.setEnabled(True)


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
                passwordField.setEchoMode(QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password)

    def switchPageAndResetInputs(self, targetPage):
        for widget in self.currentPage().findChildren(QLineEdit):
            widget.setText("")
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
        if button:
            button.setEnabled(True)
            button.setStyleSheet(self.get_button_stylesheet(True))
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
        return super().eventFilter(source, event)

    def showAdditionalButtons(self):
        try:
            logging.info("Entering showAdditionalButtons")

            # If the container already exists and is visible, do nothing
            if self.additional_buttons_container and self.additional_buttons_container.isVisible():
                logging.info("additional_buttons_container is already shown")
                return

            # If the container exists but is hidden, just show it
            if self.additional_buttons_container:
                logging.info("additional_buttons_container exists but is hidden")
                self.additional_buttons_container.show()
            else:
                # Create the container if it doesn't exist
                logging.info("additional_buttons_container does not exist, creating new container")
                button_width = 150
                button_height = 40
                frame_width = button_width + 20
                frame_height = 2 * button_height + 25
                left_offset = self.btnTimeKeeping.geometry().right() + 5
                top_offset = self.btnTimeKeeping.geometry().top()

                self.additional_buttons_container = QWidget(self)
                self.additional_buttons_container.setGeometry(left_offset, top_offset, frame_width, frame_height)
                self.additional_buttons_container.setStyleSheet(
                    "background-color: #DCE5FE; border: 1px solid gray; font-family: Poppins;")

                additional_button_texts = ["Date Change", "Time Logger"]
                for i, text in enumerate(additional_button_texts):
                    button = QPushButton(text, self.additional_buttons_container)
                    button.setGeometry(10, 10 + i * (button_height + 5), button_width, button_height)
                    button.setStyleSheet("background-color: white;")
                    button.installEventFilter(self)
                    button.clicked.connect(self.open_dialog(text))

                logging.info("Showing additional_buttons_container")
                self.additional_buttons_container.show()
        except Exception as e:
            logging.error(f"Error in showAdditionalButtons: {str(e)}")

    def open_dialog(self, dialog_type):
        dialogs = {
            'Date Change': self.openDateChange,
            'Time Logger': self.openTimeLogger
        }
        return dialogs.get(dialog_type)

    def checkAndHideAdditionalButtons(self):
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        if not self.btnTimeKeeping.geometry().contains(cursor_pos):
            if self.additional_buttons_container:
                if not self.additional_buttons_container.geometry().contains(cursor_pos):
                    self.hideAdditionalButtons()
    def hideAdditionalButtons(self):
        if self.additional_buttons_container:
            self.additional_buttons_container.hide()

    def employeeWindow(self):
        if self.employee_list_window is None:
            self.employee_list_window = EmployeeList()
            self.open_dialogs.append(self.employee_list_window)

        if not self.employee_list_window.isVisible():
            # Clears the Employee Basic Info upon closing
            ListFunction(self.employee_list_window).clearFunction()

        if self.employee_list_window.isVisible():
            self.employee_list_window.activateWindow()
        else:
            self.employee_list_window.show()

    def openTimeLogger(self):
        if self.timekeeping_window is None:
            self.timekeeping_window = dialogModal()
            self.open_dialogs.append(self.timekeeping_window)
        self.timekeeping_window.show()

    def openDateChange(self):
        if self.datechange is None:
            self.datechange = DateChange()
            self.open_dialogs.append(self.datechange)
        self.datechange.show()

    def openPayRoll(self):
        if self.payroll_window is not None:
            self.payroll_window.close()

        user_role = self.session_at_main.get("user_role")

        # Pass notification_service to PaytimeSheet
        self.payroll_window = PaytimeSheet(self, self.session_at_main, user_role, self.notification_service)
        self.open_dialogs.append(self.payroll_window)

        if self.payroll_window.isVisible():
            self.payroll_window.activateWindow()
        else:
            self.payroll_window.show()
            self.print_user_name()

    def openBugReportModal(self):
        if self.bugReportModal is None:
            self.bugReportModal = BugReportModal()
            self.open_dialogs.append(self.bugReportModal)
        if self.bugReportModal.isVisible():
            self.bugReportModal.activateWindow()
        else:
            self.bugReportModal.finished.connect(self.bugReportModal.cancelBtn)
            self.bugReportModal.show()

    def resource_path(self, relative_path):
        return globalFunction.resource_path(relative_path)

    def load_fonts(self):
        load_fonts()

    def print_user_name(self):
        try:
            user_name = str(self.session_at_main["user_name"])
            print(f"User Name: {user_name}")
        except AttributeError:
            print("UserSession does not have the 'user_name' attribute.")
        except KeyError:
            print("The key 'user_name' does not exist in the user session dictionary.")

