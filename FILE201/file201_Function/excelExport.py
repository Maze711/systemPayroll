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

        # Convert fetched data to pandas DataFrames
        personal_info_df = pd.DataFrame(personal_info_data, columns=personal_info_columns)
        educ_info_df = pd.DataFrame(educ_info_data, columns=educ_info_columns)
        family_info_df = pd.DataFrame(family_info_data, columns=family_info_columns)
        id_info_df = pd.DataFrame(id_info_data, columns=id_info_columns)
        work_exp_df = pd.DataFrame(work_exp_data, columns=work_exp_columns)
        tech_skills_df = pd.DataFrame(tech_skills_data, columns=tech_skills_columns)

        return {
            "Personal Information": personal_info_df,
            "Educational Information": educ_info_df,
            "Family Background": family_info_df,
            "List of IDs": id_info_df,
            "Work Experience": work_exp_df,
            "Technical Skills": tech_skills_df
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
                combined_df = pd.merge(combined_df, df, on='empl_id', how='left')

                for col in df.columns:
                    if col != 'empl_id':
                        combined_df = combined_df.rename(columns={col: f"{sheet_name}_{col}"})

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name="Employee Data", index=False)

        logging.info(f"Data successfully exported to {file_name}")
    except Exception as e:
        logging.error(f"Error exporting data to Excel: {e}")