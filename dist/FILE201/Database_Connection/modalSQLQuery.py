from MainFrame.Database_Connection.DBConnection import create_connection
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
        INSERT INTO personal_information (lastName, firstName, middleName, suffix, street, barangay, city, province, zip, 
                                          phoneNum, height, weight, civilStatus, dateOfBirth, placeOfBirth, gender)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        last_name = data.get('Last Name', '')
        first_name = data.get('First Name', '')
        middle_name = data.get('Middle Name', '')
        suffix = data.get('Suffix', '')
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
        cursor.execute(insert_personal_information, (last_name, first_name, middle_name, suffix, street, barangay, city,
                                                     province, zip_num, phone_num, height, weight, civil_status,
                                                     date_of_birth, place_of_birth, gender))

        row_id = cursor.lastrowid # Retrieves the unformatted id of the new inserted employee

        # Inserting custom generated employee id to the database
        generated_id = get_generated_employee_id(row_id)
        query = "UPDATE personal_information SET empID = %s WHERE empID = %s"
        cursor.execute(query, (generated_id, row_id))

        logger.info("Inserted into personal_information table")

        # Insert into Family Background
        insert_family_background = """
        INSERT INTO family_background (empID, fathersLastName, fathersFirstName, fathersMiddleName, mothersLastName, 
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
        logger.info("Inserted into family_background table")

        # Insert into list_of_id table
        insert_list_of_id = """
        INSERT INTO list_of_id (empID, sssNum, pagibigNum, philhealthNum, tinNum)
        VALUES (%s, %s, %s, %s, %s)
        """
        sss_num = data.get('SSS Number', '')
        pagibig_num = data.get('Pag-IBIG Number', '')
        philhealth_num = data.get('PhilHealth Number', '')
        tin_num = data.get('TIN Number', '')
        cursor.execute(insert_list_of_id, (generated_id, sss_num, pagibig_num, philhealth_num, tin_num))
        logger.info("Inserted into list_of_id table")

        # Insert into work_exp table
        insert_work_exp = """
        INSERT INTO work_exp (empID, fromDate, toDate, companyName, companyAdd, empPosition)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        from_date = data.get('Date From', '')
        to_date = data.get('Date To', '')
        company_name = data.get('Company', '')
        company_add = data.get('Company Address', '')
        position = data.get('Position', '')
        cursor.execute(insert_work_exp, (generated_id, from_date, to_date, company_name, company_add, position))
        logger.info("Inserted into work_exp table")

        # Insert into educ_information table
        insert_educ_information = """
        INSERT INTO educ_information (empID, college, highSchool, elemSchool,
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
        logger.info("Inserted into educ_information table")

        # Insert into tech_skills table
        insert_tech_skills = """INSERT INTO tech_skills(empID, techSkill1, certificate1, validationDate1, techSkill2, 
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
        logger.info("Inserted into tech_skills table")

        # Commit changes to the database
        connection.commit()

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

def save_employee(empID, data):
    try:
        connection = create_connection()
        if connection is None:
            logger.error("Error: Could not establish database connection.")
            return False

        cursor = connection.cursor()

        # Update personal_information table
        update_personal_information = """
        UPDATE personal_information
        SET lastName = %s, firstName = %s, middleName = %s, suffix = %s, street = %s, barangay = %s, city = %s, 
            province = %s, zip = %s, phoneNum = %s, height = %s, weight = %s, civilStatus = %s, dateOfBirth = %s, 
            placeOfBirth = %s, gender = %s
        WHERE empID = %s
        """
        cursor.execute(update_personal_information, (data['lastName'], data['firstName'], data['middleName'], data['suffix'],
                                                     data['Street'], data['Barangay'], data['City'], data['Province'],
                                                     data['ZIP'], data['Phone Number'], data['Height'], data['Weight'],
                                                     data['Civil Status'], data['Date of Birth'], data['Place of Birth'],
                                                     data['Gender'], empID))

        # Update family_background table
        update_family_background = """
        UPDATE family_background
        SET fathersLastName = %s, fathersFirstName = %s, fathersMiddleName = %s, mothersLastName = %s, 
            mothersFirstName = %s, mothersMiddleName = %s, spouseLastName = %s, spouseFirstName = %s, 
            spouseMiddleName = %s, beneficiaryLastName = %s, beneficiaryFirstName = %s, beneficiaryMiddleName = %s, 
            dependentsName = %s
        WHERE empID = %s
        """
        cursor.execute(update_family_background, (data["Father's Last Name"], data["Father's First Name"], data["Father's Middle Name"],
                                                  data["Mother's Last Name"], data["Mother's First Name"], data["Mother's Middle Name"],
                                                  data["Spouse's Last Name"], data["Spouse's First Name"], data["Spouse's Middle Name"],
                                                  data["Beneficiary's Last Name"], data["Beneficiary's First Name"], data["Beneficiary's Middle Name"],
                                                  data["Dependent's Name"], empID))

        # Update list_of_id table
        update_list_of_id = """
        UPDATE list_of_id
        SET sssNum = %s, pagibigNum = %s, philhealthNum = %s, tinNum = %s
        WHERE empID = %s
        """
        cursor.execute(update_list_of_id, (data['SSS Number'], data['Pag-IBIG Number'], data['PhilHealth Number'], data['TIN Number'], empID))

        # Update work_exp table
        update_work_exp = """
        UPDATE work_exp
        SET fromDate = %s, toDate = %s, companyName = %s, companyAdd = %s, empPosition = %s
        WHERE empID = %s
        """
        cursor.execute(update_work_exp, (data['Date From'], data['Date To'], data['Company'], data['Company Address'], data['Position'], empID))

        # Update educ_information table
        update_educ_information = """
        UPDATE educ_information
        SET college = %s, highSchool = %s, elemSchool = %s,
            collegeAdd = %s, highschoolAdd = %s, elemAdd = %s, collegeCourse = %s, highschoolStrand = %s, collegeYear = %s,
            highschoolYear = %s, elemYear = %s
        WHERE empID = %s
        """
        cursor.execute(update_educ_information, (data['College'], data['High-School'], data['Elementary'],
                                                 data['College Address'], data['High-School Address'], data['Elementary Address'],
                                                 data['College Course'], data['High-School Strand'],
                                                 data['College Graduate Year'], data['High-School Graduate Year'], data['Elementary Graduate Year'],
                                                 empID))
        # Update tech_skills table
        update_tech_skills = """
        UPDATE tech_skills 
        SET techSkill1 = %s, certificate1 = %s, validationDate1 = %s, techSkill2 = %s, certificate2 = %s, 
            validationDate2 = %s, techSkill3 = %s, certificate3 = %s, validationDate3 = %s 
        WHERE empID = %s
        """
        cursor.execute(update_tech_skills, (data['Technical Skills #1'], data['Certificate #1'], data['Validation Date #1'],
                                            data['Technical Skills #2'], data['Certificate #2'], data['Validation Date #2'],
                                            data['Technical Skills #3'], data['Certificate #3'], data['Validation Date #3'],
                                            empID))

        # Commit changes to the database
        connection.commit()
        logger.info(f"Employee with ID {empID} updated successfully")
        return True

    except Error as e:
        logger.error(f"Error updating employee with ID {empID}: {e}")
        print(e)
        return False

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def revert_employee():
    pass

def get_generated_employee_id(employee_id):
    # Converts the row_id into string
    str_employee_id = str(employee_id)

    # slicing the employee_id
    year = str_employee_id[:4]
    id_number = str_employee_id[4:]

    current_year = datetime.now().year

    # Validates the format of the employee ID
    if str_employee_id == "1":
        generated_employee_id = int(f"{current_year}{int(str_employee_id):04}")
        return generated_employee_id
    elif str(current_year) != year:
        generated_employee_id = int(f"{current_year}{int(id_number):04}")
        return generated_employee_id
    else:
        return employee_id

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