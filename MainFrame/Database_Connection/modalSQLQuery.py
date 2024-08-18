import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection

def add_employee(data):
    try:
        connection = create_connection('FILE201')
        if connection is None:
            return False

        cursor = connection.cursor()

        # Insert into personal_information table
        insert_personal_information = """
        INSERT INTO emp_info (surname, firstname, mi, suffix, street, barangay, city, province, zipcode, mobile, height, 
                                weight, status, birthday, birthplace, sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        surname = data.get('Last Name', '')
        first_name = data.get('First Name', '')
        middle_name = data.get('Middle Name', '')
        suffix = data.get('Suffix', '')
        street = data.get('Street', '')
        barangay = data.get('Barangay', '')
        city = data.get('City', '')
        province = data.get('Province', '')
        zipcode = data.get('zipcode', '')
        phone_num = data.get('Phone Number', '')
        height = data.get('Height', '')
        weight = data.get('Weight', '')
        civil_status = data.get('Civil Status', '')
        birthday = data.get('Date of Birth', '')
        place_of_birth = data.get('Place of Birth', '')
        gender = data.get('Gender', '')
        cursor.execute(insert_personal_information, (surname, first_name, middle_name, suffix, street, barangay, city, province, zipcode, phone_num,
                                                     height, weight, civil_status, birthday, place_of_birth, gender))

        row_id = cursor.lastrowid # Retrieves the unformatted id of the new inserted employee

        # Inserting custom generated employee id to the database
        generated_id = get_generated_employee_id(row_id)
        query = "UPDATE emp_info SET empl_id = %s WHERE ID = %s"
        cursor.execute(query, (generated_id, row_id))

        logging.info("Inserted into personal_information table")

        # Insert into Family Background
        insert_family_background = """
        INSERT INTO family_background (empl_id, fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, 
                                       mothersFirstName, mothersMiddleName, spouseLastName, spouseFirstName, 
                                       spouseMiddleName, beneficiaryLastName, beneficiaryFirstName, 
                                       beneficiaryMiddleName, dependentsName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        fathers_lname = data.get("Father's Last Name", '')
        fathers_fname = data.get("Father's First Name", '')
        fathers_mname = data.get("Father's Middle Name", '')
        mothers_lname = data.get("Mother's Last Name", '')
        mothers_fname = data.get("Mother's First Name", '')
        mothers_mname = data.get("Mother's Middle Name", '')
        spouse_lname = data.get("Spouse's Last Name", '')
        spouse_fname = data.get("Spouse's First Name", '')
        spouse_mname = data.get("Spouse's Middle Name", '')
        beneficiary_lname = data.get("Beneficiary's Last Name", '')
        beneficiary_fname = data.get("Beneficiary's First Name", '')
        beneficiary_mname = data.get("Beneficiary's Middle Name", '')
        dependent_name = data.get("Dependent's Name", '')
        cursor.execute(insert_family_background, (generated_id, fathers_lname, fathers_fname, fathers_mname, mothers_lname,
                                                  mothers_fname, mothers_mname, spouse_lname, spouse_fname,
                                                  spouse_mname, beneficiary_lname, beneficiary_fname, beneficiary_mname,
                                                  dependent_name))
        logging.info("Inserted into family_background table")

        # Insert into list_of_id table
        insert_list_of_id = """
        INSERT INTO emp_list_id (empl_id, sss, tin, pagibig, philhealth)
        VALUES (%s, %s, %s, %s, %s)
        """
        sss_num = data.get('SSS Number', '')
        pagibig_num = data.get('Pag-IBIG Number', '')
        philhealth_num = data.get('PhilHealth Number', '')
        tin_num = data.get('TIN Number', '')
        cursor.execute(insert_list_of_id, (generated_id, sss_num, tin_num, pagibig_num, philhealth_num))
        logging.info("Inserted into list_of_id table")

        # Insert into work_exp table
        insert_work_exp = """
        INSERT INTO work_exp (empl_id, fromDate, toDate, companyName, companyAdd, empPosition)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        from_date = data.get('Date From', '')
        to_date = data.get('Date To', '')
        company_name = data.get('Company', '')
        company_add = data.get('Company Address', '')
        position = data.get('Position', '')
        cursor.execute(insert_work_exp, (generated_id, from_date, to_date, company_name, company_add, position))
        logging.info("Inserted into work_exp table")

        # Insert into educ_information table
        insert_educ_information = """
        INSERT INTO educ_information (empl_id, college, highSchool, elemSchool,
                                      collegeAdd, highschoolAdd, elemAdd, collegeCourse, highschoolStrand, collegeYear,
                                      highschoolYear, elemYear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        college = data.get('College', '')
        high_school = data.get('High-School', '')
        elem_school = data.get('Elementary', '')
        college_add = data.get('College Address', '')
        highschool_add = data.get('High-School Address', '')
        elem_add = data.get('Elementary Address', '')
        college_course = data.get('College Course', '')
        highschool_strand = data.get('High-School Strand', '')
        college_year = data.get('College Graduate Year', '')
        highschool_year = data.get('High-School Graduate Year', '')
        elem_year = data.get('Elementary Graduate Year', '')
        cursor.execute(insert_educ_information, (generated_id, college, high_school, elem_school, college_add,
                                                 highschool_add, elem_add, college_course, highschool_strand,
                                                 college_year, highschool_year, elem_year))
        logging.info("Inserted into educ_information table")

        # Insert into tech_skills table
        insert_tech_skills = """INSERT INTO tech_skills(empl_id, techSkill1, certificate1, validationDate1, techSkill2, 
        certificate2, validationDate2, techSkill3, certificate3, validationDate3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        tech_skill1 = data.get('Technical Skills #1', '')
        certificate_skill1 = data.get('Certificate #1', '')
        validation_date1 = data.get('Validation Date #1', '')
        tech_skill2 = data.get('Technical Skills #2', '')
        certificate_skill2 = data.get('Certificate #2', '')
        validation_date2 = data.get('Validation Date #2', '')
        tech_skill3 = data.get('Technical Skills #3', '')
        certificate_skill3 = data.get('Certificate #3', '')
        validation_date3 = data.get('Validation Date #3', '')
        cursor.execute(insert_tech_skills, (generated_id, tech_skill1, certificate_skill1, validation_date1,
                                            tech_skill2, certificate_skill2, validation_date2,
                                            tech_skill3, certificate_skill3, validation_date3))
        logging.info("Inserted into tech_skills table")

        # Commit changes to the database
        connection.commit()

        logging.info("Changes committed successfully")
        return True

    except Error as e:
        logging.error(f"Error adding employee: {e}")
        print(e)
        return False
    except Exception as ex:
        logging.error(f"Error adding employee: {ex}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def save_employee(empl_id, data):
    try:
        connection = create_connection('FILE201')
        if connection is None:
            logging.error("Error: Could not establish database connection.")
            return False

        cursor = connection.cursor()

        # Update personal_information table
        update_personal_information = """
        UPDATE emp_info
        SET surname = %s, firstname = %s, mi = %s, suffix = %s, street = %s, barangay = %s, city = %s, province = %s, 
            zipcode = %s, mobile = %s, height = %s, weight = %s, status = %s, birthday = %s, birthplace = %s, sex = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_personal_information, (data['lastName'], data['firstName'], data['middleName'], data['suffix'],
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
        cursor.execute(update_family_background, (data["Father's Last Name"], data["Father's First Name"], data["Father's Middle Name"],
                                                  data["Mother's Last Name"], data["Mother's First Name"], data["Mother's Middle Name"],
                                                  data["Spouse's Last Name"], data["Spouse's First Name"], data["Spouse's Middle Name"],
                                                  data["Beneficiary's Last Name"], data["Beneficiary's First Name"], data["Beneficiary's Middle Name"],
                                                  data["Dependent's Name"], empl_id))

        # Update list_of_id table
        update_list_of_id = """
        UPDATE emp_list_id
        SET sss = %s, tin = %s, pagibig = %s, philhealth = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_list_of_id, (data['SSS Number'], data['TIN Number'], data['Pag-IBIG Number'], data['PhilHealth Number'], empl_id))

        # Update work_exp table
        update_work_exp = """
        UPDATE work_exp
        SET fromDate = %s, toDate = %s, companyName = %s, companyAdd = %s, empPosition = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_work_exp, (data['Date From'], data['Date To'], data['Company'], data['Company Address'], data['Position'], empl_id))

        # Update educ_information table
        update_educ_information = """
        UPDATE educ_information
        SET college = %s, highSchool = %s, elemSchool = %s,
            collegeAdd = %s, highschoolAdd = %s, elemAdd = %s, collegeCourse = %s, highschoolStrand = %s, collegeYear = %s,
            highschoolYear = %s, elemYear = %s
        WHERE empl_id = %s
        """
        cursor.execute(update_educ_information, (data['College'], data['High-School'], data['Elementary'],
                                                 data['College Address'], data['High-School Address'], data['Elementary Address'],
                                                 data['College Course'], data['High-School Strand'],
                                                 data['College Graduate Year'], data['High-School Graduate Year'], data['Elementary Graduate Year'],
                                                 empl_id))
        # Update tech_skills table
        update_tech_skills = """
        UPDATE tech_skills 
        SET techSkill1 = %s, certificate1 = %s, validationDate1 = %s, techSkill2 = %s, certificate2 = %s, 
            validationDate2 = %s, techSkill3 = %s, certificate3 = %s, validationDate3 = %s 
        WHERE empl_id = %s
        """
        cursor.execute(update_tech_skills, (data['Technical Skills #1'], data['Certificate #1'], data['Validation Date #1'],
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
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def revert_employee():
    pass

def get_generated_employee_id(employee_id):
    # Convert the employee_id to a string and pad with zeros if necessary
    str_employee_id = str(employee_id).zfill(8)

    # Extract year and id_number
    year = str_employee_id[:4]
    id_number = str_employee_id[4:]

    current_year = str(2024)

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

def executeQuery(query, *args):
    try:
        connection = create_connection('FILE201')
        if connection is None:
            logging.error("Error: Could not establish database connection.")
            return []

        cursor = connection.cursor()
        values = args
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    except Error as e:
        logging.error(f"Error executing query: {e}")
        return []

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()