from MainFrame.Resources.lib import *

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.file201_Function.modalFunction import modalFunction
from FILE201.file201_Function.excelExport import fetch_personal_information, export_to_excel
from FILE201.file201_Function.excelImporter import importIntoDB

from MainFrame.systemFunctions import globalFunction


class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList.ui"))
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