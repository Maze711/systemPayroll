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
