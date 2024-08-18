import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import globalFunction, timekeepingFunction


class chkSched(QDialog):
    def __init__(self, data):
        super(chkSched, self).__init__()
        self.setFixedSize(780, 413)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\Schedule.ui")
        loadUi(ui_file, self)

        self.data = data
        self.populate_schedule_with_data(data)

    def populate_schedule_with_data(self, data):
        (empNum, bioNum, empName, trans_date, checkIn, checkOut, sched, total_hours) = data

        self.empNameTxt.setText(empName)
        self.bioNumTxt.setText(bioNum)
        self.dateOfWork.setDate(QDate.fromString(trans_date, "yyyy-MM-dd"))
        self.timeInTxt.setText(checkIn)
        self.timeOutTxt.setText(checkOut)
        self.hoursWorkedTxt.setText(str(total_hours))
        self.holidayNameTxt.setText(self.getHolidayName(trans_date))
        self.typeOfDayCb.setCurrentText(timekeepingFunction.getTypeOfDate(trans_date))

    def getHolidayName(self, trans_date):
        try:
            connection = create_connection('TIMEKEEPING')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return None
            cursor = connection.cursor()

            # Fetches the holiday name in type_of_dates database
            fetch_holiday_name = "SELECT holidayName FROM type_of_dates WHERE date = %s"
            cursor.execute(fetch_holiday_name, (trans_date, ))

            result = cursor.fetchone()
            if result:
                return result[0]

            return "Normal Day"

        except Error as e:
            logging.error(f"Error fetching holiday name: {e}")
            return
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")
