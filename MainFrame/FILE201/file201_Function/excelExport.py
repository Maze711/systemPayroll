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
            return None

        cursor = connection.cursor()

        tables = [
            "emp_info", "educ_information", "family_background", "emp_list_id",
            "work_exp", "tech_skills", "emp_posnsched", "emergency_list",
            "emp_rate", "emp_status", "vacn_sick_count"
        ]

        data_dict = {}

        for table_name in tables:
            logging.info(f"Fetching data from {table_name} table.")
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            data_dict[table_name] = df

        return data_dict

    except Error as e:
        logging.error(f"Error fetching employee data: {e}")
        return None

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