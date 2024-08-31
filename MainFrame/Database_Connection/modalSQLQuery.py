import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import DatabaseConnectionError


def add_employee(data):
    try:
        connection = create_connection('FILE201')
        if connection is None:
            raise DatabaseConnectionError("Error: Could not establish database connection.")
        cursor = connection.cursor()

        # Insert employee information
        row_id = insert_personal_information(cursor, data)
        generated_id = get_generated_employee_id(row_id)
        update_employee_id(cursor, generated_id, row_id)

        # Insert other related data
        insert_family_background(cursor, generated_id, data)
        insert_list_of_id(cursor, generated_id, data)
        insert_work_exp(cursor, generated_id, data)
        insert_educ_information(cursor, generated_id, data)
        insert_tech_skills(cursor, generated_id, data)
        insert_emp_rate(cursor, generated_id, data)

        # Commit the changes to the FILE201 database
        connection.commit()
        logging.info("Changes committed successfully")

        # Send notification to the paymaster in the system_notification database
        send_notification(generated_id, data)

        return True

    except Error as e:
        logging.error(f"Error adding employee: {e}")
        return False
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            logging.info("Database connection closed")


def insert_personal_information(cursor, data):
    query = """
    INSERT INTO emp_info (surname, firstname, mi, suffix, street, barangay, city, province, zipcode, mobile, height, 
                          weight, status, birthday, birthplace, sex)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data.get('Last Name', ''), data.get('First Name', ''), data.get('Middle Name', ''), data.get('Suffix', ''),
        data.get('Street', ''), data.get('Barangay', ''), data.get('City', ''), data.get('Province', ''),
        data.get('zipcode', ''), data.get('Phone Number', ''), data.get('Height', ''), data.get('Weight', ''),
        data.get('Civil Status', ''), data.get('Date of Birth', ''), data.get('Place of Birth', ''),
        data.get('Gender', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into emp_info table")
    return cursor.lastrowid


def update_employee_id(cursor, generated_id, row_id):
    query = "UPDATE emp_info SET empl_id = %s WHERE ID = %s"
    cursor.execute(query, (generated_id, row_id))
    logging.info("Updated employee ID")


def insert_family_background(cursor, empl_id, data):
    query = """
    INSERT INTO family_background (empl_id, fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, 
                                   mothersFirstName, mothersMiddleName, spouseLastName, spouseFirstName, 
                                   spouseMiddleName, beneficiaryLastName, beneficiaryFirstName, 
                                   beneficiaryMiddleName, dependentsName)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get("Father's Last Name", ''), data.get("Father's First Name", ''),
        data.get("Father's Middle Name", ''),
        data.get("Mother's Last Name", ''), data.get("Mother's First Name", ''), data.get("Mother's Middle Name", ''),
        data.get("Spouse's Last Name", ''), data.get("Spouse's First Name", ''), data.get("Spouse's Middle Name", ''),
        data.get("Beneficiary's Last Name", ''), data.get("Beneficiary's First Name", ''),
        data.get("Beneficiary's Middle Name", ''),
        data.get("Dependent's Name", '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into family_background table")


def insert_list_of_id(cursor, empl_id, data):
    query = """
    INSERT INTO emp_list_id (empl_id, sss, tin, pagibig, philhealth)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get('SSS Number', ''), data.get('TIN Number', ''), data.get('Pag-IBIG Number', ''),
        data.get('PhilHealth Number', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into emp_list_id table")


def insert_work_exp(cursor, empl_id, data):
    query = """
    INSERT INTO work_exp (empl_id, fromDate, toDate, companyName, companyAdd, empPosition)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get('Date From', ''), data.get('Date To', ''), data.get('Company', ''),
        data.get('Company Address', ''), data.get('Position', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into work_exp table")


def insert_educ_information(cursor, empl_id, data):
    query = """
    INSERT INTO educ_information (empl_id, college, highSchool, elemSchool,
                                  collegeAdd, highschoolAdd, elemAdd, collegeCourse, highschoolStrand, collegeYear,
                                  highschoolYear, elemYear)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get('College', ''), data.get('High-School', ''), data.get('Elementary', ''),
        data.get('College Address', ''), data.get('High-School Address', ''), data.get('Elementary Address', ''),
        data.get('College Course', ''), data.get('High-School Strand', ''), data.get('College Graduate Year', ''),
        data.get('High-School Graduate Year', ''), data.get('Elementary Graduate Year', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into educ_information table")


def insert_tech_skills(cursor, empl_id, data):
    query = """
    INSERT INTO tech_skills(empl_id, techSkill1, certificate1, validationDate1, techSkill2, 
                            certificate2, validationDate2, techSkill3, certificate3, validationDate3)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get('Technical Skills #1', ''), data.get('Certificate #1', ''),
        data.get('Validation Date #1', ''),
        data.get('Technical Skills #2', ''), data.get('Certificate #2', ''), data.get('Validation Date #2', ''),
        data.get('Technical Skills #3', ''), data.get('Certificate #3', ''), data.get('Validation Date #3', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into tech_skills table")


def insert_emp_rate(cursor, empl_id, data):
    query = """
    INSERT INTO emp_rate(empl_id, rph, rate, mth_salary, dailyallow, mntlyallow)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        empl_id, data.get('RPH', ''), data.get('Rate', ''), data.get('Month Salary', ''),
        data.get('Daily Allowance', ''), data.get('Monthly Allowance', '')
    )
    cursor.execute(query, values)
    logging.info("Inserted into emp_rate table")


def send_notification(empl_id, data):
    try:
        notification_connection = create_connection('SYSTEM_NOTIFICATION')
        if notification_connection is None:
            raise DatabaseConnectionError("Error: Could not establish connection to the system_notification database.")

        notification_cursor = notification_connection.cursor()

        query = """
        INSERT INTO paymaster_notification_user(empl_id, surname, firstname, mi)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            empl_id, data.get('Last Name', ''), data.get('First Name', ''), data.get('Middle Name', '')
        )
        notification_cursor.execute(query, values)
        logging.info("Inserted into paymaster_notification_user table")

        notification_connection.commit()
        logging.info("Notification sent successfully")

    except Error as e:
        logging.error(f"Error sending notification: {e}")
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
    finally:
        if notification_cursor is not None:
            notification_cursor.close()
        if notification_connection is not None and notification_connection.is_connected():
            notification_connection.close()
            logging.info("Notification database connection closed")


def get_generated_employee_id(employee_id):
    # Convert the employee_id to a string and pad with zeros if necessary
    str_employee_id = str(employee_id).zfill(8)

    # Extract year and id_number
    year = str_employee_id[:4]
    id_number = str_employee_id[4:]

    current_year = datetime.now().year

    # Validate the format of the employee ID
    if len(str_employee_id) < 8:
        raise ValueError("employee_id must be an integer with at least 4 digits.")

    if year == current_year:
        # If the year matches the current year, return the original ID
        return employee_id
    else:
        # Otherwise, generate a new ID with the current year and padded id_number
        try:
            generated_employee_id = int(f"{current_year}{int(id_number):04}")
            return generated_employee_id
        except ValueError:
            raise ValueError("Invalid id_number format.")


def save_employee(empl_id, data):
    connection = None
    cursor = None

    try:
        connection = create_connection('FILE201')
        if connection is None:
            raise DatabaseConnectionError("Error: Could not establish database connection.")

        cursor = connection.cursor()

        # Update personal_information table
        update_personal_information = """
        UPDATE emp_info
        SET surname = %s, firstname = %s, mi = %s, suffix = %s, street = %s, barangay = %s, city = %s, province = %s, 
            zipcode = %s, mobile = %s, height = %s, weight = %s, status = %s, birthday = %s, birthplace = %s, sex = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_personal_information,
                       (data['lastName'], data['firstName'], data['middleName'], data['suffix'],
                        data['Street'], data['Barangay'], data['City'], data['Province'],
                        data['zipcode'], data['Phone Number'], data['Height'], data['Weight'],
                        data['Civil Status'], data['Date of Birth'], data['Place of Birth'],
                        data['Gender'], empl_id))

        # Update family_background table
        update_family_background = """
        UPDATE family_background
        SET fathersLastName = %s, fathersFirstName = %s, fathersMiddleName = %s, mothersLastName = %s, 
            mothersFirstName = %s, mothersMiddleName = %s, spouseLastName = %s, spouseFirstName = %s, 
            spouseMiddleName = %s, beneficiaryLastName = %s, beneficiaryFirstName = %s, beneficiaryMiddleName = %s, 
            dependentsName = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_family_background,
                       (data["Father's Last Name"], data["Father's First Name"], data["Father's Middle Name"],
                        data["Mother's Last Name"], data["Mother's First Name"], data["Mother's Middle Name"],
                        data["Spouse's Last Name"], data["Spouse's First Name"], data["Spouse's Middle Name"],
                        data["Beneficiary's Last Name"], data["Beneficiary's First Name"],
                        data["Beneficiary's Middle Name"],
                        data["Dependent's Name"], empl_id))

        # Update list_of_id table
        update_list_of_id = """
        UPDATE emp_list_id
        SET sss = %s, tin = %s, pagibig = %s, philhealth = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_list_of_id, (
            data['SSS Number'], data['TIN Number'], data['Pag-IBIG Number'], data['PhilHealth Number'], empl_id))

        # Update work_exp table
        update_work_exp = """
        UPDATE work_exp
        SET fromDate = %s, toDate = %s, companyName = %s, companyAdd = %s, empPosition = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_work_exp, (
            data['Date From'], data['Date To'], data['Company'], data['Company Address'], data['Position'], empl_id))

        # Update educ_information table
        update_educ_information = """
        UPDATE educ_information
        SET college = %s, highSchool = %s, elemSchool = %s,
            collegeAdd = %s, highschoolAdd = %s, elemAdd = %s, collegeCourse = %s, highschoolStrand = %s, collegeYear = %s,
            highschoolYear = %s, elemYear = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_educ_information, (data['College'], data['High-School'], data['Elementary'],
                                                 data['College Address'], data['High-School Address'],
                                                 data['Elementary Address'],
                                                 data['College Course'], data['High-School Strand'],
                                                 data['College Graduate Year'], data['High-School Graduate Year'],
                                                 data['Elementary Graduate Year'],
                                                 empl_id))
        # Update tech_skills table
        update_tech_skills = """
        UPDATE tech_skills 
        SET techSkill1 = %s, certificate1 = %s, validationDate1 = %s, techSkill2 = %s, certificate2 = %s, 
            validationDate2 = %s, techSkill3 = %s, certificate3 = %s, validationDate3 = %s 
        WHERE empl_id = %s
        """
        cursor.execute(update_tech_skills,
                       (data['Technical Skills #1'], data['Certificate #1'], data['Validation Date #1'],
                        data['Technical Skills #2'], data['Certificate #2'], data['Validation Date #2'],
                        data['Technical Skills #3'], data['Certificate #3'], data['Validation Date #3'],
                        empl_id))

        # Commit changes to the database
        connection.commit()
        return True

    except Error as e:
        print(e)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        # Ensure the connection is closed if it was established
        if connection is not None and connection.is_connected():
            connection.close()
            logging.info("Database connection closed")


def revert_employee():
    pass


def executeQuery(query, *args):
    connection = None
    cursor = None

    try:
        connection = create_connection('FILE201')
        if connection is None:
            raise DatabaseConnectionError("Error: Could not establish database connection.")

        cursor = connection.cursor()
        values = args
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    except Error as e:
        logging.error(f"Error executing query: {e}")
        return []

    finally:
        if cursor is not None:
            cursor.close()
        # Ensure the connection is closed if it was established
        if connection is not None and connection.is_connected():
            connection.close()
            logging.info("Database connection closed")
