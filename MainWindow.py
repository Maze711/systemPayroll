import sys
import os

from PyQt5.QtCore import QRect, QEvent, QPropertyAnimation, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.uic import loadUi

from FILE201.Employee_List.employeeList import EmployeeList
from MainFrame.fontLoader import load_fonts
from TimeKeeping.datImporter.dialogLoader import dialogModal

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #ui_file = os.path.join(os.path.dirname(__file__), 'Resources', 'Main.ui')
        ui_file = (resource_path("MainFrame\\Resources\\Main.ui"))
        loadUi(ui_file, self)

        self.functions = self

        # Window Connections
        self.btnEmployeeList.clicked.connect(self.employeeWindow)

        # Additional buttons list
        self.additional_buttons = []

        self.btnTimeKeeping.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.btnTimeKeeping:
            if event.type() == QEvent.Enter:
                self.showAdditionalButtons()
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.checkAndHideAdditionalButtons)
        elif source in self.additional_buttons:
            if event.type() == QEvent.Enter:
                return True
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(200, self.checkAndHideAdditionalButtons)
        return super(MainWindow, self).eventFilter(source, event)

    def showAdditionalButtons(self):
        self.hideAdditionalButtons()

        button_width = 150
        button_height = 40
        left_offset = self.btnTimeKeeping.geometry().right() + 5
        top_offset = self.btnTimeKeeping.geometry().top()

        additional_button_texts = ["Date Change", "Time Logger"]
        for i, text in enumerate(additional_button_texts):
            button = QPushButton(text, self)
            button.setGeometry(left_offset, top_offset + i * button_height, button_width, button_height)
            button.show()
            button.installEventFilter(self)
            self.additional_buttons.append(button)

            if text == "Time Logger":
                button.clicked.connect(self.openTimeLogger)

    def checkAndHideAdditionalButtons(self):
        if not (self.btnTimeKeeping.underMouse() or any(button.underMouse() for button in self.additional_buttons)):
            self.hideAdditionalButtons()

    def hideAdditionalButtons(self):
        for button in self.additional_buttons:
            button.hide()
            button.removeEventFilter(self)
        self.additional_buttons.clear()

    def employeeWindow(self):
        self.employee_list_window = EmployeeList()
        self.employee_list_window.show()

    def openTimeLogger(self):
        self.timekeeping_window = dialogModal()
        self.timekeeping_window.show()

def main():
    app = QApplication(sys.argv)
    load_fonts()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
