import sys
import os
import logging

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QWidget, QLabel, QPushButton, QDateEdit
from PyQt5.uic import loadUi

from TimeKeeping.datImporter.dialogLoader import dialogModal

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = dialogModal()
    dialog.show()
    sys.exit(app.exec_())