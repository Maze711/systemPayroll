import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from MainFrame.Database_Connection.DBConnection import create_connection

def convert_to_24hour(time_str):
    try:
        if isinstance(time_str, str):
            if ':' in time_str:
                in_time = datetime.strptime(time_str, "%I:%M %p")
            else:
                in_time = datetime.strptime(time_str, "%I%p")
            return in_time.strftime("%H:%M")
        return None
    except ValueError:
        logging.warning(f"Unable to convert time: {time_str}")
        return None

def split_schedule(sche_name):
    if isinstance(sche_name, str) and '-' in sche_name:
        parts = sche_name.split('-')
        if len(parts) == 2:
            sched_in = convert_to_24hour(parts[0].strip())
            sched_out = convert_to_24hour(parts[1].strip().replace("sched", "").strip())
            return sched_in, sched_out
    return None, None

def importIntoDB(parent, display_employees_callback):
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")
        if not file_name:
            return

        workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
        sheet = workbook.sheet_by_index(0)

        required_personal_columns = [
            'empno', 'emp_id', 'surname', 'firstname', 'mi', 'addr1', 'birthday', 'birthplace', 'religion',
            'civil_stat', 'gender', 'height', 'weight', 'mobile', 'blood_type', 'email'
        ]
        required_emergency_columns = [
            'empno', 'emp_id', 'emer_name'
        ]
        required_list_columns = [
            'empno', 'emp_id', 'txcode', 'sssno', 'tin', 'pagibig', 'philhealth', 'bank_code', 'cola'
        ]
        required_posnsched_columns = [
            'empno', 'emp_id', 'pos_descr', 'sche_name', 'dept_name'
        ]

        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        missing_columns = [col for col in required_personal_columns +
                           required_emergency_columns + required_list_columns +
                           required_posnsched_columns if col not in headers]

        if missing_columns:
            error_message = f"Missing required columns: {', '.join(missing_columns)}"
            QMessageBox.warning(parent, "Missing Columns", error_message)
            return

        connection = create_connection('FILE201')
        if connection is None:
            return

        cursor = connection.cursor()

        emergency_list_mapping = {
            'empl_no': 'empno',
            'empl_id': 'emp_id',
            'emer_name': 'emer_name'
        }
        emp_info_column_mapping = {
            'empl_no': 'empno',
            'empl_id': 'emp_id',
            'surname': 'surname',
            'firstname': 'firstname',
            'mi': 'mi',
            'addr1': 'addr1',
            'birthday': 'birthday',
            'birthplace': 'birthplace',
            'religion': 'religion',
            'status': 'civil_stat',
            'sex': 'gender',
            'height': 'height',
            'weight': 'weight',
            'mobile': 'mobile',
            'blood_type': 'blood_type',
            'email': 'email'
        }
        list_column_mapping = {
            'empl_no': 'empno',
            'empl_id': 'emp_id',
            'taxstat': 'txcode',
            'sss': 'sssno',
            'tin': 'tin',
            'pagibig': 'pagibig',
            'philhealth': 'philhealth',
            'bank_code': 'bank_code',
            'cola': 'cola'
        }
        posnsched_column_mapping = {
            'empl_no': 'empno',
            'empl_id': 'emp_id',
            'pos_descr': 'pos_descr',
            'sche_name': 'sche_name',
            'dept_name': 'dept_name'
        }

        insert_emergency_query = """
            INSERT INTO emergency_list (empl_no, empl_id, emer_name)
            VALUES (%s, %s, %s)
        """
        insert_personal_query = """
            INSERT INTO emp_info (empl_no, empl_id, surname, firstname, mi, addr1, birthday, birthplace,
            religion, status, sex, height, weight, mobile, blood_type, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        insert_list_query = """
            INSERT INTO emp_list_id (empl_no, empl_id, taxstat, sss, tin, pagibig, philhealth, bank_code, cola)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        insert_posnsched_query = """
            INSERT INTO emp_posnsched (empl_no, empl_id, pos_descr, dept_name, sched_in, sched_out)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)

            empno = str(row[headers.index('empno')]) if 'empno' in headers and isinstance(
                row[headers.index('empno')], (str, float)) else ''
            if not empno:
                logging.warning(f"Skipping row {row_idx + 1} due to missing empno.")
                continue


            emer_data = {
                key: str(row[headers.index(emergency_list_mapping[key])]) if key in emergency_list_mapping and isinstance(
                    row[headers.index(emergency_list_mapping[key])], (str, float)) else ''
                for key in emergency_list_mapping.keys()
            }
            personal_data = {
                key: str(row[headers.index(emp_info_column_mapping[key])]) if key in emp_info_column_mapping and isinstance(
                    row[headers.index(emp_info_column_mapping[key])], (str, float)) else ''
                for key in emp_info_column_mapping.keys()
            }

            list_data = {
                key: str(row[headers.index(list_column_mapping[key])]) if key in list_column_mapping and isinstance(
                    row[headers.index(list_column_mapping[key])], (str, float)) else ''
                for key in list_column_mapping.keys()
            }

            sche_name = str(row[headers.index('sche_name')]) if 'sche_name' in headers and isinstance(
                row[headers.index('sche_name')], (str, float)) else ''
            sched_in, sched_out = split_schedule(sche_name)
            posnsched_data = {
                key: str(row[headers.index(posnsched_column_mapping[key])]) if key in posnsched_column_mapping and isinstance(
                    row[headers.index(posnsched_column_mapping[key])], (str, float)) else ''
                for key in posnsched_column_mapping.keys()
            }
            posnsched_data['sched_in'] = sched_in
            posnsched_data['sched_out'] = sched_out

            logging.debug(f"Inserting into emergency_list: {emer_data}")
            logging.debug(f"Inserting into emp_info: {personal_data}")
            logging.debug(f"Inserting into emp_list_id: {list_data}")
            logging.debug(f"Inserting into emp_posnsched: {posnsched_data}")

            try:
                cursor.execute(insert_emergency_query, (
                    emer_data['empl_no'], emer_data['empl_id'], emer_data['emer_name']))
                cursor.execute(insert_personal_query, (
                    personal_data['empl_no'], personal_data['empl_id'], personal_data['surname'],
                    personal_data['firstname'], personal_data['mi'], personal_data['addr1'],
                    personal_data['birthday'], personal_data['birthplace'], personal_data['religion'],
                    personal_data['status'], personal_data['sex'], personal_data['height'],
                    personal_data['weight'], personal_data['mobile'], personal_data['blood_type'],
                    personal_data['email']
                ))
                cursor.execute(insert_list_query, (
                    list_data['empl_no'], list_data['empl_id'], list_data['taxstat'],
                    list_data['sss'], list_data['tin'], list_data['pagibig'],
                    list_data['philhealth'], list_data['bank_code'], list_data['cola']
                ))
                cursor.execute(insert_posnsched_query, (
                    posnsched_data['empl_no'], posnsched_data['empl_id'], posnsched_data['pos_descr'],
                    posnsched_data['dept_name'], posnsched_data['sched_in'], posnsched_data['sched_out']
                ))

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
