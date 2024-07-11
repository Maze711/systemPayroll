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

            if not all([self.cmbCheckIn, self.cmbCheckOut, self.btnOK, self.btnClear]):
                raise ValueError("One or more UI elements not found")

            self.cmbCheckIn.currentIndexChanged.connect(self.save_settings)
            self.cmbCheckOut.currentIndexChanged.connect(self.save_settings)
            self.btnOK.clicked.connect(self.accept)
            self.btnClear.clicked.connect(self.clear_filter)

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

    def get_filter_values(self):
        values = {
            'check_in_ampm': "AM" if self.cmbCheckIn.currentIndex() == 0 else "PM",
            'check_out_ampm': "AM" if self.cmbCheckOut.currentIndex() == 0 else "PM"
        }
        logging.info(f"Filter values: {values}")
        return values