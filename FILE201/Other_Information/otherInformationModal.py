from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QDateEdit, QCalendarWidget
from PyQt5.uic import loadUi
import sys
from FILE201.file201_Function.modalFunction import modalFunction


class personalModal(QMainWindow):
    def __init__(self):
        super(personalModal, self).__init__()
        self.setFixedSize(1153, 665)
        loadUi("otherInformation.ui", self)

        self.functions = modalFunction(self)

        current_date = QtCore.QDate.currentDate()
        self.set_current_date_to_all_date_edits(current_date)

        self.addBTN.clicked.connect(self.functions.add_Employee)
        self.editBTN.clicked.connect(self.functions.edit_Employee)
        self.saveBTN.clicked.connect(self.functions.save_Employee)
        self.revertBTN.clicked.connect(self.functions.revert_Employee)
    def set_current_date_to_all_date_edits(self, current_date):
        for widget in self.findChildren(QtWidgets.QDateEdit):
            widget.setDate(current_date)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = personalModal()
    ui.show()
    app.exec_()
