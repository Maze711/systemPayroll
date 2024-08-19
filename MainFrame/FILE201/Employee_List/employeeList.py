import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from MainFrame.FILE201.file201_Function.listFunction import ListFunction
from MainFrame.FILE201.file201_Function.modalFunction import modalFunction
from MainFrame.FILE201.file201_Function.excelExport import fetch_personal_information, export_to_excel
from MainFrame.FILE201.file201_Function.excelImporter import importIntoDB, update_db_for_missing_row_columns

from MainFrame.systemFunctions import globalFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


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
        #self.btnImport.clicked.connect(lambda: importIntoDB(self, self.functions.displayEmployees))
        self.btnImport.clicked.connect(lambda: update_db_for_missing_row_columns(self))

    @single_function_logger.log_function
    def export_to_excel(self, checked):
        try:
            data_dict = fetch_personal_information()
            if data_dict:
                options = QFileDialog.Options()
                file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "",
                                                           "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;CSV Files (*.csv);;All Files (*)",
                                                           options=options)
                if file_name:
                    try:
                        if file_name.endswith('.csv'):
                            self.export_combined_csv(data_dict, file_name)
                        elif file_name.endswith('.xls'):
                            self.export_combined_xls(data_dict, file_name)
                        else:  # Default to .xlsx
                            self.export_combined_xlsx(data_dict, file_name)
                        QMessageBox.information(self, "Export Successful", f"Data successfully exported to {file_name}")
                    except PermissionError:
                        QMessageBox.warning(self, "Permission Denied",
                                            "Unable to save the file. Please ensure the file is not open in another program and you have write permissions for the selected location.")
                    except Exception as e:
                        QMessageBox.critical(self, "Export Error", f"An error occurred while exporting: {str(e)}")
        except Exception as e:
            logging.error(f"Error in export_to_excel: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Error", f"An error occurred while preparing data for export: {str(e)}")

    @single_function_logger.log_function
    def export_combined_csv(self, data_dict, file_name):
        try:
            self.export_data_in_chunks(data_dict, file_name, 'csv')
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}", exc_info=True)

    @single_function_logger.log_function
    def export_combined_xlsx(self, data_dict, file_name):
        try:
            self.export_data_in_chunks(data_dict, file_name, 'xlsx')
        except Exception as e:
            logging.error(f"Error exporting to XLSX: {e}", exc_info=True)

    @single_function_logger.log_function
    def export_combined_xls(self, data_dict, file_name):
        try:
            self.export_data_in_chunks(data_dict, file_name, 'xls')
        except Exception as e:
            logging.error(f"Error exporting to XLS: {e}", exc_info=True)

    @single_function_logger.log_function
    def export_data_in_chunks(self, data_dict, file_name, file_format):
        chunksize = 10000  # Adjust this value based on your memory constraints

        # Combine all dataframes
        combined_df = pd.concat(data_dict.values(), axis=1)

        try:
            if file_format == 'csv':
                for i in range(0, len(combined_df), chunksize):
                    mode = 'w' if i == 0 else 'a'
                    combined_df.iloc[i:i + chunksize].to_csv(file_name, mode=mode, index=False, header=(i == 0))
            else:
                with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                    for i in range(0, len(combined_df), chunksize):
                        if i == 0:
                            combined_df.iloc[i:i + chunksize].to_excel(writer, sheet_name='Employee Data', index=False)
                        else:
                            combined_df.iloc[i:i + chunksize].to_excel(writer, sheet_name='Employee Data',
                                                                       startrow=writer.sheets['Employee Data'].max_row,
                                                                       header=False, index=False)

            logging.info(f"Data successfully exported to {file_name}")
        except PermissionError:
            logging.error(f"Permission denied when writing to {file_name}")
            raise
        except Exception as e:
            logging.error(f"Error exporting data: {e}")
            raise