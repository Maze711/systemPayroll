import sys
import os
import mysql.connector
import pandas as pd
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QHeaderView, QPushButton
from PyQt5.uic import loadUi

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.file201_Function.modalFunction import modalFunction
from FILE201.file201_Function.excelExport import fetch_personal_information, export_to_excel
from FILE201.file201_Function.excelImporter import importIntoDB

logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = resource_path("FILE201\\Employee_List\\employeeList.ui")
        loadUi(ui_file, self)

        self.frame_layout = QVBoxLayout(self.frameAnnualSummary)

        # Make the column headers fixed size
        self.employeeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.employeeListTable.horizontalHeader().setStretchLastSection(True)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.frame_layout.addWidget(self.canvas)
        self.graph_loader = graphLoader(self.canvas)
        self.graph_loader.plot_pie_chart()

        self.functions = ListFunction(self)
        self.function = modalFunction(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.functions.timeClock)
        self.timer.start(1)

        self.btnAddEmployee.clicked.connect(self.functions.open_otherInformationMODAL_add)
        self.btnViewInfo.clicked.connect(self.functions.open_otherInformationMODAL_view)
        self.functions.displayEmployees()
        self.employeeListTable.itemClicked.connect(self.functions.getSelectedRow)
        self.btnClear.clicked.connect(self.functions.clearFunction)
        self.txtSearch.textChanged.connect(self.functions.searchEmployees)
        self.btnExport.clicked.connect(self.export_to_excel)
        self.btnImport = self.findChild(QPushButton, 'btnImport')
        self.btnImport.clicked.connect(lambda: importIntoDB(self, self.functions.displayEmployees))

    def export_to_excel(self):
        data_dict = fetch_personal_information()
        if data_dict:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Excel Files (*.xlsx);;All Files (*)",
                                                       options=options)
            if file_name:
                export_to_excel(data_dict, file_name)