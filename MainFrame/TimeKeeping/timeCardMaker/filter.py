import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import globalFunction, single_function_logger

class filter(QDialog):
    @single_function_logger.log_function
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setFixedSize(400, 300)
            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\filter.ui")
            loadUi(ui_file, self)


            self.cmbCheckIn = self.findChild(QComboBox, 'cmbCheckIn')
            self.cmbCheckOut = self.findChild(QComboBox, 'cmbCheckOut')
            self.btnOK = self.findChild(QPushButton, 'btnOK')
            self.btnClear = self.findChild(QPushButton, 'btnClear')
            self.btnMissing = self.findChild(QPushButton, 'btnMissing')

            if not all([self.cmbCheckIn, self.cmbCheckOut, self.btnOK, self.btnClear, self.btnMissing]):
                raise ValueError("One or more UI elements not found")

            self.btnOK.clicked.connect(self.accept)
            self.btnClear.clicked.connect(self.clear_filter)
            self.btnMissing.clicked.connect(self.show_missing)

            for combo in [self.cmbCheckIn, self.cmbCheckOut]:
                if combo.itemText(0) != "AM/PM":
                    combo.insertItem(0, "AM/PM")

        except Exception as e:
            logging.error(f"Error initializing filter dialog: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred while initializing the filter dialog: {str(e)}")

    @single_function_logger.log_function
    def clear_filter(self):
        self.cmbCheckIn.setCurrentIndex(0)
        self.cmbCheckOut.setCurrentIndex(0)
        if self.parent():
            self.parent().clear_filter()
        self.accept()
        logging.info("Filter cleared")

    @single_function_logger.log_function
    def show_missing(self):
        if self.parent():
            filter_values = {
                'check_in_ampm': "AM/PM",
                'check_out_ampm': "AM/PM",
                'show_missing': True
            }
            logging.info("Showing missing entries with filter values: %s", filter_values)
            self.parent().apply_filter(filter_values)
        self.accept()

    @single_function_logger.log_function
    def get_filter_values(self):
        values = {
            'check_in_ampm': self.cmbCheckIn.currentText(),
            'check_out_ampm': self.cmbCheckOut.currentText(),
            'show_missing': False
        }
        logging.info(f"Filter values: {values}")
        return values