import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.FILE201.file201_Function.modalFunction import modalFunction

from MainFrame.systemFunctions import globalFunction

class personalModal(QDialog):
    def __init__(self, mode='view'):
        super(personalModal, self).__init__()
        self.setFixedSize(1153, 665)
        #ui_file = os.path.join(os.path.dirname(__file__), 'personalInformation.ui')
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\personalInformation.ui"))
        loadUi(ui_file, self)

        self.functions = modalFunction(self)
        self.mode = mode

        current_date = QtCore.QDate.currentDate()
        self.set_current_date_to_all_date_edits(current_date)

        self.editBTN.setText("Edit")

        self.setup_initial_state()
        self.install_event_filters()

        self.addBTN.clicked.connect(self.functions.add_Employee)
        self.editBTN.clicked.connect(self.on_edit_clicked)
        self.saveBTN.clicked.connect(self.functions.save_Employee)
        self.revertBTN.clicked.connect(self.functions.revert_Employee)

        self.set_validators()
        self.set_keyboard_shortcut()

    def setup_initial_state(self):
        if self.mode == 'view':
            self.addBTN.setEnabled(False)
            self.editBTN.setEnabled(True)
            self.saveBTN.setEnabled(False)
            self.revertBTN.setEnabled(False)
        elif self.mode == 'add':
            self.addBTN.setVisible(True)
            self.editBTN.setEnabled(False)
            self.saveBTN.setEnabled(False)
            self.revertBTN.setEnabled(False)

        self.set_button_styles()

    def install_event_filters(self):
        self.addBTN.installEventFilter(self)
        self.editBTN.installEventFilter(self)
        self.saveBTN.installEventFilter(self)
        self.revertBTN.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            if not obj.isEnabled():
                QApplication.setOverrideCursor(Qt.ForbiddenCursor)
            return True
        elif event.type() == QEvent.Leave:
            QApplication.restoreOverrideCursor()
            return True
        return super().eventFilter(obj, event)

    def on_edit_clicked(self):
        if self.editBTN.text() == "Edit":
            self.functions.edit_Employee()
            self.editBTN.setText("Cancel")
            self.saveBTN.setEnabled(True)
            self.revertBTN.setEnabled(True)
            self.set_button_styles()
        else:
            self.cancel_edit()

    def set_button_styles(self):
        enabled_style = '''
        QPushButton {
        background-color:  rgba(52, 66, 115, 1); 
        color: white;
        }
        QPushButton:hover {
            background-color: "#485994";
        }
        '''
        disabled_style = '''
        QPushButton {
        background-color: #cccccc; 
        color: #666666;
        }
        QPushButton:hover {
            background-color: "#485994";
        }
        '''

        self.addBTN.setStyleSheet(enabled_style if self.mode == 'add' else disabled_style)
        self.editBTN.setStyleSheet(enabled_style if self.mode == 'view' else disabled_style)

        if self.editBTN.text() == "Cancel":
            self.editBTN.setStyleSheet("background-color: #a12c23; color: white;")
            self.saveBTN.setStyleSheet(enabled_style)
            self.revertBTN.setStyleSheet(enabled_style)
            self.saveBTN.setEnabled(True)
            self.revertBTN.setEnabled(True)
        else:
            self.saveBTN.setStyleSheet(disabled_style)
            self.revertBTN.setStyleSheet(disabled_style)
            self.saveBTN.setEnabled(False)
            self.revertBTN.setEnabled(False)

        self.addBTN.setEnabled(self.mode == 'add')
        self.editBTN.setEnabled(self.mode == 'view')

    def cancel_edit(self):
        self.editBTN.setText("Edit")
        self.set_button_styles()
        self.set_fields_non_editable()

    def set_fields_non_editable(self):
        disabledStyle = "background-color: #f0f0f0; color: #4f4e4e;"

        for widget in self.findChildren(QLineEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disabledStyle)

        for widget in self.findChildren(QDateEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disabledStyle)

        for widget in self.findChildren(QComboBox):
            widget.setEnabled(False)
            widget.setStyleSheet(disabledStyle)

        for widget in self.findChildren(QPlainTextEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(disabledStyle)

    def set_current_date_to_all_date_edits(self, current_date):
        for widget in self.findChildren(QtWidgets.QDateEdit):
            widget.setDate(current_date)

    def set_validators(self):
        int_validator = QIntValidator()

        self.txtZip.setValidator(int_validator)
        self.txtPhone.setValidator(int_validator)
        self.txtHeight.setValidator(int_validator)
        self.txtWeight.setValidator(int_validator)
        self.sssTextEdit.setValidator(int_validator)
        self.pagibigTextEdit.setValidator(int_validator)
        self.philHealthTextEdit.setValidator(int_validator)
        self.tinTextEdit.setValidator(int_validator)

    def set_keyboard_shortcut(self):
        self.shortcut = QtWidgets.QShortcut(Qt.Key_Escape, self)
        self.shortcut.activated.connect(self.close)