from MainFrame.Resources.lib import *

from FILE201.file201_Function.modalFunction import modalFunction

from MainFrame.systemFunctions import globalFunction

class personalModal(QDialog):
    def __init__(self):
        super(personalModal, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(1153, 665)
        #ui_file = os.path.join(os.path.dirname(__file__), 'personalInformation.ui')
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\personalInformation.ui"))
        loadUi(ui_file, self)

        self.functions = modalFunction(self)

        current_date = QtCore.QDate.currentDate()
        self.set_current_date_to_all_date_edits(current_date)

        self.addBTN.clicked.connect(self.functions.add_Employee)
        self.editBTN.clicked.connect(self.functions.edit_Employee)
        self.editBTN.clicked.connect(self.enable_save_button)
        self.saveBTN.clicked.connect(self.functions.save_Employee)
        self.revertBTN.clicked.connect(self.functions.revert_Employee)

        self.set_validators()
        self.set_keyboard_shortcut()

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

    def enable_save_button(self):
        self.saveBTN.setEnabled(True)