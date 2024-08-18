import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection


def fetch_personal_information():
    try:
        connection = create_connection('FILE201')
        if connection is None:
            logging.error("Could not establish database connection.")
            return None, None

        cursor = connection.cursor()

        # Fetch data from personal_information table
        logging.info("Fetching data from emp_info table.")
        cursor.execute("SELECT * FROM emp_info")
        personal_info_data = cursor.fetchall()
        personal_info_columns = [desc[0] for desc in cursor.description]

        # Fetch data from educ_information table
        logging.info("Fetching data from educ_information table.")
        cursor.execute("SELECT * FROM educ_information")
        educ_info_data = cursor.fetchall()
        educ_info_columns = [desc[0] for desc in cursor.description]

        # Fetch data from family_background table
        logging.info("Fetching data from family_background table.")
        cursor.execute("SELECT * FROM family_background")
        family_info_data = cursor.fetchall()
        family_info_columns = [desc[0] for desc in cursor.description]

        # Fetch data from list_of_id table
        logging.info("Fetching data from emp_list_id table.")
        cursor.execute("SELECT * FROM emp_list_id")
        id_info_data = cursor.fetchall()
        id_info_columns = [desc[0] for desc in cursor.description]

        # Fetch data from work_exp table
        logging.info("Fetching data from work_exp table.")
        cursor.execute("SELECT * FROM work_exp")
        work_exp_data = cursor.fetchall()
        work_exp_columns = [desc[0] for desc in cursor.description]

        # Fetch data from tech_skills table
        logging.info("Fetching data from tech_skills table.")
        cursor.execute("SELECT * FROM tech_skills")
        tech_skills_data = cursor.fetchall()
        tech_skills_columns = [desc[0] for desc in cursor.description]

        # Fetch data from ponsched table
        logging.info("Fetching data from posnsched table.")
        cursor.execute("SELECT * FROM emp_posnsched")
        posnsched_data = cursor.fetchall()
        posnsched_columns = [desc[0] for desc in cursor.description]

        # Fetch data from emergency_list table
        logging.info("Fetching data from emergency_list table.")
        cursor.execute("SELECT * FROM emergency_list")
        emergency_data = cursor.fetchall()
        emergency_columns = [desc[0] for desc in cursor.description]

        # Fetch data from emp_rate table
        logging.info("Fetching data from emp_rate table.")
        cursor.execute("SELECT * FROM emp_rate")
        emp_rate_data = cursor.fetchall()
        emp_rate_columns = [desc[0] for desc in cursor.description]

        # Fetch data from emp_status table
        logging.info("Fetching data from emp_status table.")
        cursor.execute("SELECT * FROM emp_status")
        emp_status_data = cursor.fetchall()
        emp_status_columns = [desc[0] for desc in cursor.description]

        # Fetch data from vacn_sick_count table
        logging.info("Fetching data from vacn_sick_count table.")
        cursor.execute("SELECT * FROM vacn_sick_count")
        vacn_sick_count_data = cursor.fetchall()
        vacn_sick_count_columns = [desc[0] for desc in cursor.description]

        # Convert fetched data to pandas DataFrames
        personal_info_df = pd.DataFrame(personal_info_data, columns=personal_info_columns)
        educ_info_df = pd.DataFrame(educ_info_data, columns=educ_info_columns)
        family_info_df = pd.DataFrame(family_info_data, columns=family_info_columns)
        id_info_df = pd.DataFrame(id_info_data, columns=id_info_columns)
        work_exp_df = pd.DataFrame(work_exp_data, columns=work_exp_columns)
        tech_skills_df = pd.DataFrame(tech_skills_data, columns=tech_skills_columns)
        posnsched_df = pd.DataFrame(posnsched_data, columns=posnsched_columns)
        emergency_df = pd.DataFrame(emergency_data, columns=emergency_columns)
        emp_rate_df = pd.DataFrame(emp_rate_data, columns=emp_rate_columns)
        emp_status_df = pd.DataFrame(emp_status_data, columns=emp_status_columns)
        vacn_sick_count_df = pd.DataFrame(vacn_sick_count_data, columns=vacn_sick_count_columns)

        return {
            "Personal Information": personal_info_df,
            "Educational Information": educ_info_df,
            "Family Background": family_info_df,
            "List of IDs": id_info_df,
            "Work Experience": work_exp_df,
            "Technical Skills": tech_skills_df,
            "PosnSched": posnsched_df,
            "Emergency List": emergency_df,
            "Employee Rate": emp_rate_df,
            "Employee Status": emp_status_df,
            "Vacn Sick Count": vacn_sick_count_df
        }

    except Error as e:
        logging.error(f"Error fetching employee data: {e}")
        return None, None

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Database connection closed")


def export_to_excel(data_dict, file_name):
    try:
        combined_df = data_dict["Personal Information"].copy()

        for sheet_name, df in data_dict.items():
            if sheet_name != "Personal Information":
                # Identify columns that are not in the combined_df or are 'empl_id'
                new_columns = [col for col in df.columns if col not in combined_df.columns or col == 'empl_id']

                combined_df = pd.merge(combined_df, df[new_columns], on='empl_id', how='left')

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name="Employee Data", index=False)

        logging.info(f"Data successfully exported to {file_name}")
    except Exception as e:
        logging.error(f"Error exporting data to Excel: {e}")