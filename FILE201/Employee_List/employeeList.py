import sys
import os
import mysql.connector
import pandas as pd
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

from FILE201.file201_Function.pieGraph import MplCanvas, graphLoader
from FILE201.file201_Function.listFunction import ListFunction
from FILE201.file201_Function.modalFunction import modalFunction
from FILE201.file201_Function.excelExport import fetch_personal_information, export_to_excel

logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='file201',
            user='root',
            password=''
        )
        if connection.is_connected():
            logging.info("Connected to MySQL database")
            return connection
        else:
            logging.info("Failed to connect to MySQL database")
            return None
    except Error as e:
        logging.exception("Error while connecting to MySQL: %s", e)
        return None

def parse_birthday(birthday, workbook_datemode):
    if birthday in ('', '-', '-   -', ' ', '  -   -', '-   -  ', ' -   -', '--'):
        return '0000-00-00'
    try:
        if isinstance(birthday, float):  # Excel date format
            return xlrd.xldate.xldate_as_datetime(birthday, workbook_datemode).strftime('%Y-%m-%d')
        elif isinstance(birthday, str) and birthday.strip():
            return datetime.strptime(birthday.strip(), '%d-%b-%y').strftime('%Y-%m-%d')
    except Exception as e:
        logging.warning(f"Error converting date: {e}")
    return '0000-00-00'

class EmployeeList(QMainWindow):
    def __init__(self):
        super(EmployeeList, self).__init__()
        self.setFixedSize(1280, 685)
        ui_file = resource_path("FILE201\\Employee_List\\employeeList.ui")
        loadUi(ui_file, self)

        self.frame_layout = QVBoxLayout(self.frameAnnualSummary)

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
        self.btnImport.clicked.connect(self.importIntoDB)

    def export_to_excel(self):
        data_dict = fetch_personal_information()
        if data_dict:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Excel Files (*.xlsx);;All Files (*)",
                                                       options=options)
            if file_name:
                export_to_excel(data_dict, file_name)

    def importIntoDB(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")

            if not file_name:
                return

            workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
            sheet = workbook.sheet_by_index(0)

            required_personal_columns = [
                'empl_no', 'empl_id', 'idnum', 'empl_name', 'street', 'city', 'zipcode', 'birthday', 'telephone',
                'status'
            ]
            required_list_columns = [
                'empl_no', 'taxstat', 'sss', 'tin', 'pagibig', 'philhealth'
            ]

            headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
            missing_columns = [col for col in required_personal_columns + required_list_columns if col not in headers]

            if missing_columns:
                error_message = f"Missing required columns: {', '.join(missing_columns)}"
                QMessageBox.warning(self, "Missing Columns", error_message)
                return

            personal_column_mapping = {
                'empl_no': 'empl_no',
                'empl_id': 'empl_id',
                'idnum': 'idnum',
                'empl_name': 'empl_name',
                'street': 'street',
                'city': 'city',
                'zipcode': 'zipcode',
                'birthday': 'birthday',
                'telephone': 'telephone',
                'status': 'status',
            }
            list_column_mapping = {
                'empl_no': 'empl_no',
                'taxstat': 'taxstat',
                'sss': 'sss',
                'tin': 'tin',
                'pagibig': 'pagibig',
                'philhealth': 'philhealth',
            }

            connection = create_connection()
            if connection is None:
                return

            cursor = connection.cursor()

            insert_personal_query = """
            INSERT INTO personal_information (empl_no, empl_id, idnum, lastName, firstName, street, city, zipcode,
                                              birthday, phoneNum, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_list_query = """
            INSERT INTO list_of_id (empl_no, taxstat, sss, tin, pagibig, philhealth)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            for row_idx in range(1, sheet.nrows):
                row = sheet.row_values(row_idx)

                empl_no = row[headers.index('empl_no')] if 'empl_no' in headers else ''
                if not empl_no:
                    logging.warning(f"Skipping row {row_idx + 1} due to missing empl_no.")
                    continue

                personal_data = {key: row[headers.index(personal_column_mapping[key])] if key in personal_column_mapping else '' for key in personal_column_mapping.keys()}
                list_data = {key: row[headers.index(list_column_mapping[key])] if key in list_column_mapping else '' for key in list_column_mapping.keys()}

                full_name = personal_data.get('empl_name', '')
                if ',' in full_name:
                    personal_data['lastName'], personal_data['firstName'] = map(str.strip, full_name.split(',', 1))
                else:
                    personal_data['lastName'] = full_name
                    personal_data['firstName'] = ''

                personal_data['birthday'] = parse_birthday(personal_data.get('birthday', ''), workbook.datemode)

                try:
                    cursor.execute(insert_personal_query, (
                        personal_data['empl_no'], personal_data['empl_id'], personal_data['idnum'],
                        personal_data['lastName'], personal_data['firstName'], personal_data['street'],
                        personal_data['city'], personal_data['zipcode'], personal_data['birthday'],
                        personal_data['telephone'], personal_data['status']))
                    cursor.execute(insert_list_query, (
                        list_data['empl_no'], list_data['taxstat'], list_data['sss'], list_data['tin'],
                        list_data['pagibig'], list_data['philhealth']))

                    connection.commit()

                except Error as e:
                    logging.error(f"Error inserting row {row_idx + 1} into database: {e}")

            cursor.close()
            connection.close()

            print("Data imported successfully")
            self.functions.displayEmployees()

        except Exception as e:
            logging.error(f"Error importing data from {file_name} into MySQL: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
