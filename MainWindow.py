import sys

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from PyQt5.uic import loadUi

from FILE201.Employee_List.employeeList import EmployeeList
from MainFrame.fontLoader import load_fonts
from TimeKeeping.datImporter.dialogLoader import dialogModal
from TimeKeeping.payTimeSheetImporter.payTimeSheetImporter import PayrollDialog
from TimeKeeping.dateChange.dateChange import DateChange
from MainFrame.systemFunctions import globalFunction


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\Main.ui")
        loadUi(ui_file, self)

        self.functions = self

        # Window Connections
        self.btnEmployeeList.clicked.connect(self.employeeWindow)

        self.additional_buttons_container = None

        self.btnTimeKeeping.installEventFilter(self)
        self.btnPayRoll.clicked.connect(self.openPayRoll)

    def eventFilter(self, source, event):
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
        self.employee_list_window = EmployeeList()
        self.employee_list_window.show()

    def openDateChange(self):
        self.datechange = DateChange()
        self.datechange.show()

    def openTimeLogger(self):
        self.timekeeping_window = dialogModal()
        self.timekeeping_window.show()

    def openPayRoll(self):
        self.payroll_window = PayrollDialog()
        self.payroll_window.show()


def main():
    app = QApplication(sys.argv)
    load_fonts()
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
