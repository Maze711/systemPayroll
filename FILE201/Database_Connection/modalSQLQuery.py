from FILE201.Database_Connection.DBConnection import create_connection
from mysql.connector import Error
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
        logger.info("Changes committed successfully")
        return True

    except Error as e:
        logger.error(f"Error adding employee: {e}")
        return False

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