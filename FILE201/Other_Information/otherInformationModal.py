import sys
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QPlainTextEdit
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from FILE201.file201_Function.modalFunction import modalFunction

class NumberOnlyPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(NumberOnlyPlainTextEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        key = event.key()
        # Allow only numbers, backspace, delete, left arrow, right arrow
        if key in (Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
                   Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right):
            super(NumberOnlyPlainTextEdit, self).keyPressEvent(event)
        else:
            event.ignore()

class personalModal(QDialog):
    def __init__(self):
        super(personalModal, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(1153, 665)
        ui_file = os.path.join(os.path.dirname(__file__), 'personalInformation.ui')
        loadUi(ui_file, self)

        self.functions = modalFunction(self)

        current_date = QtCore.QDate.currentDate()
        self.set_current_date_to_all_date_edits(current_date)

        self.addBTN.clicked.connect(self.functions.add_Employee)
        self.editBTN.clicked.connect(self.functions.edit_Employee)
        self.saveBTN.clicked.connect(self.functions.save_Employee)
        self.revertBTN.clicked.connect(self.functions.revert_Employee)

        self.apply_number_only_validation(self.sssTextEdit)
        self.apply_number_only_validation(self.pagibigTextEdit)
        self.apply_number_only_validation(self.philHealthTextEdit)
        self.apply_number_only_validation(self.tinTextEdit)

    def set_current_date_to_all_date_edits(self, current_date):
        for widget in self.findChildren(QtWidgets.QDateEdit):
            widget.setDate(current_date)

    def apply_number_only_validation(self, text_edit):
        text_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        if isinstance(source, QPlainTextEdit) and source.objectName() in ['sssTextEdit', 'pagibigTextEdit', 'philHealthTextEdit', 'tinTextEdit']:
            if event.type() == QtCore.QEvent.KeyPress:
                key = event.key()
                if key in (Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
                           Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right):
                    return super(personalModal, self).eventFilter(source, event)
                elif key == Qt.Key_Escape:
                    self.close()
                    return True
        return super(personalModal, self).eventFilter(source, event)

