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
            required_acct_columns = [
                'emp_id', 'paycode', 'acct_no', 'bank_code', 'cola'
            ]

            headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
            missing_columns = [col for col in required_acct_columns + required_personal_columns + required_list_columns
                               + required_posnsched_columns + required_empstatus_columns + required_vacnsic_columns
                               if col not in headers]

            if missing_columns:
                error_message = f"Missing required columns: {', '.join(missing_columns)}"
                QMessageBox.warning(self, "Missing Columns", error_message)
                return

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
            posnnsched_column_mapping = {
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

            connection = create_connection()
            if connection is None:
                return

            cursor = connection.cursor()

            insert_acc_no_query = """
            INSERT INTO acct_no (emp_id, paycode, acct_no, bank_code, cola)
            VALUES (%s, %s, %s, %s, %s)
            """
            insert_personal_query = """INSERT INTO personal_information (empno, surname, firstname, mi, emp_id, 
            addr1, emer_name, mobile, height, weight, civil_stat, birthday, birthplace, religion, gender, email, 
            blood_type, citizenship) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            insert_list_query = """
            INSERT INTO list_of_id (emp_id, sssno, tin, pagibig, philhealth, txcode)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            insert_posnsched_query = """
            INSERT INTO emp_posnsched (emp_id, pos_descr, sche_name, dept_name)
            VALUES (%s, %s, %s, %s)
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
                    key: row[headers.index(posnnsched_column_mapping[key])] if key in posnnsched_column_mapping else ''
                    for key in posnnsched_column_mapping.keys()
                }
                empstatus_data = {
                    key: row[headers.index(empstatus_column_mapping[key])] if key in empstatus_column_mapping else ''
                    for key in empstatus_column_mapping.keys()
                }
                vacnsic_data = {
                    key: row[headers.index(vacnsic_column_mapping[key])] if key in vacnsic_column_mapping else ''
                    for key in vacnsic_column_mapping.keys()
                }

                birthday = personal_data.get('birthday', '')
                if birthday and isinstance(birthday, str):
                    birthday = birthday.split(' ')[0]  # Remove time part if present
                    try:
                        birthday_date = datetime.strptime(birthday, '%m/%d/%Y')
                        birthday = birthday_date.strftime('%Y-%m-%d')
                    except ValueError:
                        birthday = '0000-00-00'  # Set default value if parsing fails
                elif isinstance(birthday, float):
                    birthday = xlrd.xldate.xldate_as_datetime(birthday, workbook.datemode).strftime('%Y-%m-%d')
                else:
                    birthday = '0000-00-00'

                personal_data['birthday'] = birthday

                try:
                    cursor.execute(insert_personal_query, (
                        personal_data['empno'], personal_data['surname'], personal_data['firstname'],
                        personal_data['mi'], personal_data['emp_id'], personal_data['addr1'],
                        personal_data['emer_name'],
                        personal_data['mobile'], personal_data['height'], personal_data['weight'],
                        personal_data['birthday'],
                        personal_data['birthplace'], personal_data['religion'], personal_data['citizenship'],
                        personal_data['blood_type'], personal_data['civil_stat'], personal_data['gender'],
                        personal_data['email']
                    ))
                    cursor.execute(insert_acc_no_query, (
                        acc_no['emp_id'], acc_no['paycode'], acc_no['acct_no'], acc_no['bank_code'],
                        acc_no['cola']
                    ))
                    cursor.execute(insert_list_query, (
                        list_data['emp_id'], list_data['sssno'], list_data['tin'], list_data['pagibig'],
                        list_data['philhealth'], list_data['txcode']
                    ))
                    cursor.execute(insert_posnsched_query, (
                        posnsched_data['emp_id'], posnsched_data['pos_descr'], posnsched_data['sche_name'],
                        posnsched_data['dept_name']
                    ))
                    cursor.execute(insert_emp_stauts_query, (
                        empstatus_data['emp_id'],
                        empstatus_data['status']
                    ))
                    cursor.execute(insert_vacnsic_query, (
                        vacnsic_data['emp_id'], vacnsic_data['max_vacn'],
                        vacnsic_data['max_sick']
                    ))

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
