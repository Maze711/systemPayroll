import sys
import os
import mysql.connector
import pandas as pd
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QHeaderView
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
            #host='127.0.0.1',
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
        self.btnImport.clicked.connect(self.importIntoDB)

    def export_to_excel(self):
        data_dict = fetch_personal_information()
        if data_dict:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Excel Files (*.xlsx);;All Files (*)",
                                                       options=options)
            if file_name:
                export_to_excel(data_dict, file_name)

    def format_time(self, time_str):
        # Function to format time strings like "6am" or "2pm" to "6:00 am" or "2:00 pm"
        try:
            time_obj = datetime.strptime(time_str, '%I%p')  # Parse time string
            formatted_time = time_obj.strftime('%I:%M %p')  # Format to "6:00 am" or "2:00 pm"
            return formatted_time
        except ValueError:
            try:
                # Attempt to parse with minutes included
                time_obj = datetime.strptime(time_str, '%I:%M %p')
                formatted_time = time_obj.strftime('%I:%M %p')
                return formatted_time
            except ValueError:
                return time_str

    def importIntoDB(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")

            if not file_name:
                return

            workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
            sheet = workbook.sheet_by_index(0)

            required_personal_columns = [
                'empno', 'surname', 'firstname', 'mi', 'emp_id', 'addr1', 'mobile', 'birthday', 'civil_stat', 'gender',
                'email', 'emer_name', 'height', 'weight', 'birthplace', 'religion', 'citizenship', 'blood_type'
            ]
            required_list_columns = [
                'emp_id', 'sssno', 'tin', 'pagibig', 'philhealth', 'txcode'
            ]
            required_posnsched_columns = [
                'emp_id', 'pos_descr', 'sche_name', 'dept_name'
            ]
            required_empstatus_columns = [
                'emp_id', 'status'
            ]
            required_vacnsic_columns = [
                'emp_id', 'max_vacn', 'max_sick'
            ]

            headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
            missing_columns = [col for col in required_personal_columns + required_list_columns
                               + required_posnsched_columns + required_empstatus_columns + required_vacnsic_columns
                               if col not in headers]

            if missing_columns:
                error_message = f"Missing required columns: {', '.join(missing_columns)}"
                QMessageBox.warning(self, "Missing Columns", error_message)
                return

            connection = create_connection()
            if connection is None:
                return

            cursor = connection.cursor()

            # Original mappings and queries
            acct_no_mapping = {
                'emp_id': 'emp_id',
                'paycode': 'paycode',
                'acct_no': 'acct_no',
                'bank_code': 'bank_code',
                'cola': 'cola'
            }
            personal_column_mapping = {
                'empno': 'empno',
                'surname': 'surname',
                'firstname': 'firstname',
                'mi': 'mi',
                'emp_id': 'emp_id',
                'addr1': 'addr1',
                'mobile': 'mobile',
                'birthday': 'birthday',
                'civil_stat': 'civil_stat',
                'gender': 'gender',
                'email': 'email',
                'emer_name': 'emer_name',
                'height': 'height',
                'weight': 'weight',
                'birthplace': 'birthplace',
                'religion': 'religion',
                'citizenship': 'citizenship',
                'blood_type': 'blood_type'
            }
            list_column_mapping = {
                'emp_id': 'emp_id',
                'sssno': 'sssno',
                'tin': 'tin',
                'pagibig': 'pagibig',
                'philhealth': 'philhealth',
                'txcode': 'txcode'
            }
            posnsched_column_mapping = {
                'emp_id': 'emp_id',
                'pos_descr': 'pos_descr',
                'sche_name': 'sche_name',
                'dept_name': 'dept_name'
            }
            empstatus_column_mapping = {
                'emp_id': 'emp_id',
                'status': 'status'
            }
            vacnsic_column_mapping = {
                'emp_id': 'emp_id',
                'max_vacn': 'max_vacn',
                'max_sick': 'max_sick'
            }

            insert_acc_no_query = """
               INSERT INTO acct_no (emp_id, paycode, acct_no, bank_code, cola)
               VALUES (%s, %s, %s, %s, %s)
               """
            insert_personal_query = """
               INSERT INTO personal_information (empno, surname, firstname, mi, emp_id, addr1, emer_name, mobile, height,
                                                 weight, civil_stat, birthday, birthplace, religion, gender, email,
                                                 blood_type, citizenship)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               """
            insert_list_query = """
               INSERT INTO list_of_id (emp_id, sssno, tin, pagibig, philhealth, txcode)
               VALUES (%s, %s, %s, %s, %s, %s)
               """
            insert_posnsched_query = """
               INSERT INTO emp_posnsched (emp_id, pos_descr, sched_in, sched_out, dept_name)
               VALUES (%s, %s, %s, %s, %s)
               """
            insert_emp_stauts_query = """
               INSERT INTO emp_status (emp_id, status)
               VALUES (%s, %s)
               """
            insert_vacnsic_query = """
               INSERT INTO vacn_sick_count (emp_id, max_vacn, max_sick)
               VALUES (%s, %s, %s)
               """

            for row_idx in range(1, sheet.nrows):
                row = sheet.row_values(row_idx)

                empno = row[headers.index('empno')] if 'empno' in headers else ''
                if not empno:
                    logging.warning(f"Skipping row {row_idx + 1} due to missing empno.")
                    continue

                acc_no = {key: row[headers.index(acct_no_mapping[key])] if key in acct_no_mapping else '' for
                          key in acct_no_mapping.keys()}
                personal_data = {
                    key: row[headers.index(personal_column_mapping[key])] if key in personal_column_mapping else '' for
                    key in personal_column_mapping.keys()}
                list_data = {key: row[headers.index(list_column_mapping[key])] if key in list_column_mapping else '' for
                             key in list_column_mapping.keys()}
                posnsched_data = {
                    key: row[headers.index(posnsched_column_mapping[key])] if key in posnsched_column_mapping else ''
                    for key in posnsched_column_mapping.keys()
                }
                empstatus_data = {
                    key: row[headers.index(empstatus_column_mapping[key])] if key in empstatus_column_mapping else ''
                    for key in empstatus_column_mapping.keys()
                }
                vacnsic_data = {
                    key: row[headers.index(vacnsic_column_mapping[key])] if key in vacnsic_column_mapping else ''
                    for key in vacnsic_column_mapping.keys()
                }

                try:
                    cursor.execute(insert_acc_no_query, tuple(acc_no.values()))
                    cursor.execute(insert_personal_query, tuple(personal_data.values()))
                    cursor.execute(insert_list_query, tuple(list_data.values()))

                    # Split sche_name and remove "sched" if present
                    if 'sche_name' in posnsched_data:
                        sche_name = posnsched_data['sche_name'].strip().lower()
                        if sche_name.endswith(' sched'):
                            sche_name = sche_name[:-6].strip()  # Remove 'sched' and trim whitespace

                        # Split by dash and get the parts
                        sche_name_parts = sche_name.split('-')
                        sched_in = self.format_time(sche_name_parts[0].strip())
                        sched_out = self.format_time(sche_name_parts[1].strip()) if len(sche_name_parts) > 1 else ''

                        cursor.execute(insert_posnsched_query, (
                            posnsched_data['emp_id'], posnsched_data['pos_descr'], sched_in, sched_out,
                            posnsched_data['dept_name']
                        ))

                    cursor.execute(insert_emp_stauts_query, tuple(empstatus_data.values()))
                    cursor.execute(insert_vacnsic_query, tuple(vacnsic_data.values()))

                    connection.commit()

                except Error as e:
                    logging.error(f"Error inserting row {row_idx + 1} into database: {e}")

            print("Data imported successfully")
            self.functions.displayEmployees()

        except Exception as e:
            logging.error(f"Error importing data from {file_name} into MySQL: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()