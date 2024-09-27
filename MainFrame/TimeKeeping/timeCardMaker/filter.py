from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class FilterDialog(QDialog):
    def __init__(self, parent=None, additional_argument=None):
        try:
            super().__init__(parent)
            self.additional_argument = additional_argument  # Handle additional_argument if needed
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

            self.selected_check_in = "AM/PM"
            self.selected_check_out = "AM/PM"

        except Exception as e:
            logging.error(f"Error initializing FilterDialog: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred while initializing the FilterDialog: {str(e)}")

    def clear_filter(self, checked=False):
        try:
            self.cmbCheckIn.setCurrentIndex(0)
            self.cmbCheckOut.setCurrentIndex(0)
            if self.parent():
                self.parent().clear_filter()
            self.accept()
            logging.info("Filter successfully cleared.")
            QMessageBox.information(self, "Filter Cleared", "The filter has been cleared successfully.")

        except Exception as e:
            logging.error(f"Error clearing filter: {e}")
            QMessageBox.critical(self, "Error", f"Failed to clear filter: {str(e)}")

    def show_missing(self, checked=False):
        if self.parent():
            filter_values = {
                'check_in_ampm': "AM/PM",
                'check_out_ampm': "AM/PM",
                'show_missing': True
            }
            logging.info("Showing missing entries with filter values: %s", filter_values)
            self.parent().apply_filter(filter_values)
        self.accept()

    def get_filter_values(self):
        values = {
            'check_in_ampm': self.cmbCheckIn.currentText(),
            'check_out_ampm': self.cmbCheckOut.currentText(),
            'show_missing': False
        }
        logging.info(f"Filter values: {values}")
        return values

    def closeEvent(self, event):
        self.selected_check_in = self.cmbCheckIn.currentText()
        self.selected_check_out = self.cmbCheckOut.currentText()
        super().closeEvent(event)