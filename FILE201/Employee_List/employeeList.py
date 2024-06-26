import sys
import os

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.uic import loadUi

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.file201_Function.modalFunction import modalFunction
from FILE201.file201_Function.excelExport import fetch_personal_information, export_to_excel

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
        self.btnClear.clicked.connect(self.functions.clearFunction)

        # Connect search function to QLineEdit
        self.txtSearch.textChanged.connect(self.functions.searchEmployees)

        # Connect export button to the export function
        self.btnExport.clicked.connect(self.export_to_excel)

    def export_to_excel(self):
        data_dict = fetch_personal_information()
        if data_dict:
            # Open a file dialog to select where to save the Excel file
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Excel Files (*.xlsx);;All Files (*)",
                                                       options=options)
            if file_name:
                export_to_excel(data_dict, file_name)