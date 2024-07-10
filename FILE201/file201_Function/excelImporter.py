import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from MainFrame.Database_Connection.DBConnection import create_connection

def format_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, '%I%p')
        formatted_time = time_obj.strftime('%I:%M %p')
        return formatted_time
    except ValueError:
        try:
            time_obj = datetime.strptime(time_str, '%I:%M %p')
            formatted_time = time_obj.strftime('%I:%M %p')
            return formatted_time
        except ValueError:
            return time_str

def importIntoDB(parent, display_employees_callback):
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")

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
            QMessageBox.warning(parent, "Missing Columns", error_message)
            return

        connection = create_connection('FILE201')
        if connection is None:
            return

        cursor = connection.cursor()

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
                                             weight, civil_stat, birthday, birthplace, gender, email, religion, 
                                             citizenship, blood_type)
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

                if 'sche_name' in posnsched_data:
                    sche_name = posnsched_data['sche_name'].strip().lower()
                    if sche_name.endswith(' sched'):
                        sche_name = sche_name[:-6].strip()

                    sche_name_parts = sche_name.split('-')
                    sched_in = format_time(sche_name_parts[0].strip())
                    sched_out = format_time(sche_name_parts[1].strip()) if len(sche_name_parts) > 1 else ''

                    cursor.execute(insert_posnsched_query, (
                        posnsched_data['emp_id'], posnsched_data['pos_descr'], sched_in, sched_out,
                        posnsched_data['dept_name']
                    ))

                cursor.execute(insert_emp_stauts_query, tuple(empstatus_data.values()))
                cursor.execute(insert_vacnsic_query, tuple(vacnsic_data.values()))

                connection.commit()

            except Error as e:
                logging.error(f"Error inserting row {row_idx + 1}: {e}")
                connection.rollback()

        QMessageBox.information(parent, "Success", "Data imported successfully.")
        cursor.close()
        connection.close()

        # Call the callback function to display employees
        display_employees_callback()

    except Error as e:
        logging.error(f"Error: {e}")
        QMessageBox.warning(parent, "Error", f"An error occurred while importing data:\n{e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        QMessageBox.warning(parent, "Error", f"An unexpected error occurred:\n{e}")
