from FILE201.Database_Connection.DBConnection import create_connection
from mysql.connector import Error
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

def add_employee(data):
    try:
        connection = create_connection()
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return False

        cursor = connection.cursor()

        # Insert into personal_information table
        insert_personal_information = """
        INSERT INTO personal_information (lastName, firstName, middleName, street, barangay, city, province, zip, 
                                          phoneNum, height, weight, civilStatus, dateOfBirth, placeOfBirth, gender)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        last_name = data.get('Last Name', '')
        first_name = data.get('First Name', '')
        middle_name = data.get('Middle Name', '')
        # suffix = data.get('Suffix', '')
        street = data.get('Street', '')
        barangay = data.get('Barangay', '')
        city = data.get('City', '')
        province = data.get('Province', '')
        zip_num = data.get('ZIP', '')
        phone_num = data.get('Phone Number', '')
        height = data.get('Height', '')
        weight = data.get('Weight', '')
        civil_status = data.get('Civil Status', '')
        date_of_birth = data.get('Date of Birth', '')
        place_of_birth = data.get('Place of Birth', '')
        gender = data.get('Gender', '')
        cursor.execute(insert_personal_information, (last_name, first_name, middle_name, street, barangay, city,
                                                     province, zip_num, phone_num, height, weight, civil_status,
                                                     date_of_birth, place_of_birth, gender))

        row_id = cursor.lastrowid # Retrieves the id of the new inserted employee

        logger.info("Inserted into personal_information table")

        # Insert into Family Background
        insert_family_background = """
        INSERT INTO family_background (fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, 
                                       mothersFirstName, mothersMiddleName, spouseLastName, spouseFirstName, 
                                       spouseMiddleName, beneficiaryLastName, beneficiaryFirstName, 
                                       beneficiaryMiddleName, dependentsName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        cursor.execute(insert_family_background, (fathers_lname, fathers_fname, fathers_mname, mothers_lname,
                                                  mothers_fname, mothers_mname, spouse_lname, spouse_fname,
                                                  spouse_mname, beneficiary_lname, beneficiary_fname, beneficiary_mname,
                                                  dependent_name))
        logger.info("Inserted into family_background table")

        # Insert into list_of_id table
        insert_list_of_id = """
        INSERT INTO list_of_id (sssNum, pagibigNum, philhealthNum, tinNum)
        VALUES (%s, %s, %s, %s)
        """
        sss_num = data.get('SSS Number', '')
        pagibig_num = data.get('Pag-IBIG Number', '')
        philhealth_num = data.get('PhilHealth Number', '')
        tin_num = data.get('TIN Number', '')
        cursor.execute(insert_list_of_id, (sss_num, pagibig_num, philhealth_num, tin_num))
        logger.info("Inserted into list_of_id table")

        # Insert into work_exp table
        insert_work_exp = """
        INSERT INTO work_exp (fromDate, toDate, companyName, companyAdd, empPosition)
        VALUES (%s, %s, %s, %s, %s)
        """
        from_date = data.get('Date From', '')
        to_date = data.get('Date To', '')
        company_name = data.get('Company', '')
        company_add = data.get('Company Address', '')
        position = data.get('Position', '')
        cursor.execute(insert_work_exp, (from_date, to_date, company_name, company_add, position))
        logger.info("Inserted into work_exp table")

        # Insert into educ_information table
        insert_educ_information = """
        INSERT INTO educ_information (techSkill, certificateSkill, validationDate, college, highSchool, elemSchool,
                                      collegeAdd, highschoolAdd, elemAdd, collegeCourse, highschoolStrand, collegeYear,
                                      highschoolYear, elemYear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        tech_skill = data.get('Technical Skills #1', '')
        certificate_skill = data.get('Certificate #1', '')
        validation_date = data.get('Validation Date #1', '')
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
        cursor.execute(insert_educ_information, (tech_skill, certificate_skill, validation_date, college, high_school,
                                                elem_school, college_add, highschool_add, elem_add, college_course,
                                                highschool_strand, college_year, highschool_year, elem_year))
        logger.info("Inserted into educ_information table")

        # Commit changes to the database
        connection.commit()

        # Inserting custom generated employee id to the database
        insert_generated_employee_id(row_id)

        logger.info("Changes committed successfully")
        return True

    except Error as e:
        logger.error(f"Error adding employee: {e}")
        print(e)
        return False

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def get_generated_employee_id(employee_id): #20240010
    # Converts the row_id into string
    str_employee_id = str(employee_id) #20240010

    # slicing the employee_id
    year = str_employee_id[:4] #2024
    id_number = str_employee_id[4:] #0010

    current_year = datetime.now().year #2025

    # Validates the format of the employee ID
    if str_employee_id == "1":
        generated_employee_id = f"{current_year}{int(str_employee_id):04}"
        return int(generated_employee_id)
    elif str(current_year) != year:
        generated_employee_id = f"{current_year}{int(id_number):04}"
        return int(generated_employee_id)
    else:
        return employee_id

def insert_generated_employee_id(row_id):
    try:
        connection = create_connection()
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return None
        cursor = connection.cursor()
        generated_id = get_generated_employee_id(row_id)
        query = "UPDATE personal_information SET empID = %s WHERE empID = %s"
        cursor.execute(query, (generated_id, row_id))
        connection.commit()

    except Error as e:
        logger.error(f"Error inserting generated employee ID: {e}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def edit_employee():
    pass

def save_employee():
    pass

def revert_employee():
    pass

def executeSearchQuery(query):
    try:
        connection = create_connection()
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return []

        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    except Error as e:
        logger.error(f"Error executing search query: {e}")
        return []

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")