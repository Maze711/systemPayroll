import sys
import mysql.connector
import os

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton
from PyQt5.uic import loadUi

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.Other_Information.otherInformationModal import personalModal

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

        # Calls the timeClock recursively every 1 second
        self.timer = QTimer()
        self.timer.timeout.connect(self.functions.timeClock)
        self.timer.start(1)

        # Connect button click event
        self.btnAddEmployee.clicked.connect(self.open_otherInformationMODAL)
        self.btnViewInfo.clicked.connect(self.open_otherInformationMODAL)

    def open_otherInformationMODAL(self):
        self.modal = personalModal()
        self.modal.show()