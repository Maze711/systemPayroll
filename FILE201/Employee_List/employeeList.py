import sys
import mysql.connector
import os

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel
from PyQt5.uic import loadUi

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.Other_Information.otherInformationModal import personalModal
from FILE201.file201_Function.modalFunction import modalFunction

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = os.path.join(os.path.dirname(__file__), 'employeeList.ui')
        loadUi(ui_file, self)

        self.frame_layout = QVBoxLayout(self.frameAnnualSummary)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.frame_layout.addWidget(self.canvas)
        self.graph_loader = graphLoader(self.canvas)
        self.graph_loader.plot_pie_chart()

        self.functions = ListFunction(self)
        self.function = modalFunction(self)

        # Calls the timeClock recursively every 1 second
        self.timer = QTimer()
        self.timer.timeout.connect(self.functions.timeClock)
        self.timer.start(1)

        # Modal Connections
        self.btnAddEmployee.clicked.connect(self.functions.open_otherInformationMODAL_add)
        self.btnViewInfo.clicked.connect(self.functions.open_otherInformationMODAL_view)

        # Displays employees in the table
        self.functions.displayEmployees()

        # Item Click event for row selection
        self.employeeListTable.itemClicked.connect(self.functions.getSelectedRow)

        # Clearing the displayed information
        self.btnClear.clicked.connect(self.function.clearFunction)

        # Connect search function to QLineEdit
        self.txtSearch.textChanged.connect(self.functions.searchEmployees)