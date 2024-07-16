import sys
import os
import logging
import traceback

from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

logging.basicConfig(level=logging.INFO, filename='filter.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class filter(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setFixedSize(400, 300)
            ui_file = resource_path("TimeKeeping\\timeCardMaker\\filter.ui")
            loadUi(ui_file, self)

            self.settings = QSettings("", "TimeCard")

            self.cmbCheckIn = self.findChild(QComboBox, 'cmbCheckIn')
            self.cmbCheckOut = self.findChild(QComboBox, 'cmbCheckOut')
            self.btnOK = self.findChild(QPushButton, 'btnOK')
            self.btnClear = self.findChild(QPushButton, 'btnClear')
            self.btnMissing = self.findChild(QPushButton, 'btnMissing')

            if not all([self.cmbCheckIn, self.cmbCheckOut, self.btnOK, self.btnClear, self.btnMissing]):
                raise ValueError("One or more UI elements not found")

            self.cmbCheckIn.currentIndexChanged.connect(self.save_settings)
            self.cmbCheckOut.currentIndexChanged.connect(self.save_settings)
            self.btnOK.clicked.connect(self.accept)
            self.btnClear.clicked.connect(self.clear_filter)
            self.btnMissing.clicked.connect(self.show_missing)

            for combo in [self.cmbCheckIn, self.cmbCheckOut]:
                if combo.itemText(0) != "AM/PM":
                    combo.insertItem(0, "AM/PM")

            self.load_settings()
        except Exception as e:
            logging.error(f"Error initializing filter dialog: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred while initializing the filter dialog: {str(e)}")

    def save_settings(self):
        self.settings.setValue("check_in_ampm", self.cmbCheckIn.currentIndex())
        self.settings.setValue("check_out_ampm", self.cmbCheckOut.currentIndex())
        logging.info(f"Settings saved: Check-in {self.cmbCheckIn.currentText()}, Check-out {self.cmbCheckOut.currentText()}")

    def load_settings(self):
        check_in_index = self.settings.value("check_in_ampm", 0, type=int)
        check_out_index = self.settings.value("check_out_ampm", 0, type=int)
        self.cmbCheckIn.setCurrentIndex(check_in_index)
        self.cmbCheckOut.setCurrentIndex(check_out_index)
        logging.info(f"Settings loaded: Check-in {self.cmbCheckIn.currentText()}, Check-out {self.cmbCheckOut.currentText()}")

    def clear_filter(self):
        self.cmbCheckIn.setCurrentIndex(0)
        self.cmbCheckOut.setCurrentIndex(0)
        self.save_settings()
        if self.parent():
            self.parent().clear_filter()
        self.accept()
        logging.info("Filter cleared")

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

    def get_filter_values(self):
        values = {
            'check_in_ampm': self.cmbCheckIn.currentText(),
            'check_out_ampm': self.cmbCheckOut.currentText(),
            'show_missing': False
        }
        logging.info(f"Filter values: {values}")
        return values