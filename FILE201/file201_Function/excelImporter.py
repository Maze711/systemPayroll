import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import xlrd
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from MainFrame.Database_Connection.DBConnection import create_connection

def format_birthday(birthday_str):
    try:
        date_obj = datetime.strptime(birthday_str, '%d-%b-%y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date
    except ValueError:
        return '0000-00-00'

def importIntoDB(parent, display_employees_callback):
    try:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(parent, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")
        if not file_name:
            return

        workbook = xlrd.open_workbook(file_name, encoding_override="cp1252")
        sheet = workbook.sheet_by_index(0)

        required_personal_columns = [
            'empl_no', 'empl_id', 'idnum', 'empl_name', 'street', 'city', 'zipcode',
            'birthday', 'status', 'sex', 'telephone'
        ]
        required_emergency_columns = [
            'empl_no', 'empl_id'
        ]
        required_list_columns = [
            'empl_no', 'empl_id', 'taxstat', 'sss', 'tin', 'pagibig', 'philhealth', 'account_no'
        ]
        required_empstatus_columns = [
            'empl_no', 'empl_id', 'compcode', 'dept_code', 'position', 'emp_stat', 'date_hired', 'resigned', 'dtresign'
        ]
        required_rate_columns = [
            'empl_no', 'empl_id', 'rph', 'rate', 'mth_salary', 'dailyallow', 'mntlyallow', 'ssloanded',
            'ssloanamt', 'lovelnded', 'lovelnamt'
        ]

        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        missing_columns = [col for col in required_personal_columns + required_emergency_columns + required_list_columns
                           + required_empstatus_columns + required_rate_columns
                           if col not in headers]

        if missing_columns:
            error_message = f"Missing required columns: {', '.join(missing_columns)}"
            QMessageBox.warning(parent, "Missing Columns", error_message)
            return

        connection = create_connection('FILE201')
        if connection is None:
            return

        cursor = connection.cursor()

        emergency_list_mapping = {
            'empl_no': 'empl_no',
            'empl_id': 'empl_id',
        }
        emp_info_column_mapping = {
            'empl_no': 'empl_no',
            'empl_id': 'empl_id',
            'idnum': 'idnum',
            'empl_name': 'empl_name',
            'street': 'street',
            'city': 'city',
            'zipcode': 'zipcode',
            'birthday': 'birthday',
            'status': 'status',
            'sex': 'sex',
            'telephone': 'telephone',
        }
        list_column_mapping = {
            'empl_no': 'empl_no',
            'empl_id': 'empl_id',
            'taxstat': 'taxstat',
            'sss': 'sss',
            'tin': 'tin',
            'pagibig': 'pagibig',
            'philhealth': 'philhealth',
            'account_no': 'account_no',
        }

        empstatus_column_mapping = {
            'empl_no': 'empl_no',
            'empl_id': 'empl_id',
            'compcode': 'compcode',
            'dept_code': 'dept_code',
            'position': 'position',
            'emp_stat': 'emp_stat',
            'date_hired': 'date_hired',
            'resigned': 'resigned',
            'dtresign': 'dtresign',
        }

        insert_emergency_query = """
            INSERT INTO emergency_list (empl_no, empl_id)
            VALUES (%s, %s)
        """
        insert_personal_query = """
            INSERT INTO emp_info (empl_no, empl_id, idnum, surname, firstname, street, city, zipcode,
                                  birthday, status, sex, telephone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        insert_list_query = """
            INSERT INTO emp_list_id (empl_no, empl_id, taxstat, sss, tin, pagibig, philhealth, account_no)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        insert_emp_status_query = """
            INSERT INTO emp_status (empl_no, empl_id, compcode, dept_code, position, emp_stat, date_hired, resigned, dtresign)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)

            empno = row[headers.index('empl_no')] if 'empl_no' in headers else ''
            if not empno:
                logging.warning(f"Skipping row {row_idx + 1} due to missing empl_no.")
                continue

            # Process empl_name into surname and firstname
            empl_name = row[headers.index('empl_name')] if 'empl_name' in headers else ''
            surname, firstname = '', ''
            if ',' in empl_name:
                surname, firstname = [name.strip() for name in empl_name.split(',', 1)]
            else:
                surname = empl_name.strip()

            # Process birthday into YYYY-MM-DD format
            birthday = row[headers.index('birthday')] if 'birthday' in headers else ''
            formatted_birthday = format_birthday(birthday)

            emer_data = {
                key: row[headers.index(emergency_list_mapping[key])] if key in emergency_list_mapping else ''
                for key in emergency_list_mapping.keys()
            }
            personal_data = {
                key: row[headers.index(emp_info_column_mapping[key])] if key in emp_info_column_mapping else ''
                for key in emp_info_column_mapping.keys()
            }
            personal_data['surname'] = surname
            personal_data['firstname'] = firstname
            personal_data['birthday'] = formatted_birthday

            list_data = {
                key: row[headers.index(list_column_mapping[key])] if key in list_column_mapping else ''
                for key in list_column_mapping.keys()
            }
            empstatus_data = {
                key: row[headers.index(empstatus_column_mapping[key])] if key in empstatus_column_mapping else ''
                for key in empstatus_column_mapping.keys()
            }

            try:
                cursor.execute(insert_emergency_query, (emer_data['empl_no'], emer_data['empl_id']))
                cursor.execute(insert_personal_query, (
                    personal_data['empl_no'], personal_data['empl_id'], personal_data['idnum'],
                    personal_data['surname'], personal_data['firstname'], personal_data['street'],
                    personal_data['city'], personal_data['zipcode'], personal_data['birthday'],
                    personal_data['status'], personal_data['sex'], personal_data['telephone']
                ))
                cursor.execute(insert_list_query, (
                    list_data['empl_no'], list_data['empl_id'], list_data['taxstat'],
                    list_data['sss'], list_data['tin'], list_data['pagibig'],
                    list_data['philhealth'], list_data['account_no']
                ))
                cursor.execute(insert_emp_status_query, (
                    empstatus_data['empl_no'], empstatus_data['empl_id'], empstatus_data['compcode'],
                    empstatus_data['dept_code'], empstatus_data['position'], empstatus_data['emp_stat'],
                    empstatus_data['date_hired'], empstatus_data['resigned'], empstatus_data['dtresign']
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
