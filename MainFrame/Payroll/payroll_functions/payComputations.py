import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

class PayComputation:
    def __init__(self, data):
        self.data = data

    def basicComputation(self):
        for item in self.data:
            days_work = item.get('Present Days')
            rate = item.get('Rate')

            try:
                days_work_int = int(float(days_work))
                rate_int = int(float(rate))
            except ValueError:
                days_work_int = 0
                rate_int = 0

            basic = days_work_int * rate_int
            item['Basic'] = basic
            logging.info(f"Calculated basic for EmpNo {item['EmpNo']}: {basic}")

    def overtimeComputation(self):
        overtime_rate = 74.844  # Define the overtime rate
        for item in self.data:
            ordinary_day_ot = item.get('OrdinaryDayOT')

            try:
                ordinary_day_ot_float = float(ordinary_day_ot)
            except ValueError:
                ordinary_day_ot_float = 0

            overtime_value = ordinary_day_ot_float * overtime_rate
            item['OT_Earn'] = round(overtime_value, 2)
            logging.info(f"Calculated overtime for EmpNo {item['EmpNo']}: {item['OT_Earn']}")

    def lateComputation(self):
        late_rate = 59.875  # Define the late
        scaling_factor = 10  # Define the scaling factor to adjust 'Late' values

        for item in self.data:
            hours = item.get('Late')

            logging.info(f"Raw data for EmpNo {item['EmpNo']}: Late={hours}")

            try:
                hours_float = float(hours)
            except ValueError as e:
                logging.error(f"Error converting Late value for EmpNo {item['EmpNo']}: {e}")
                hours_float = 0

            # Adjust the hours value using the scaling factor
            scaled_hours = hours_float * scaling_factor
            late_undertime_value = scaled_hours * late_rate

            item['LateUndertime'] = round(late_undertime_value, 2)
            logging.info(f"Calculated late value for EmpNo {item['EmpNo']}: {item['LateUndertime']}")

    def undertimeComputation(self):
        undertime_rate = 59.875  # Define the undertime rate
        scaling_factor = 10  # Define the scaling factor to adjust 'Late' values

        for item in self.data:
            hours = item.get('Undertime')

            logging.info(f"Raw data for EmpNo {item['EmpNo']}: Undertime={hours}")

            try:
                hours_float = float(hours)
            except ValueError as e:
                logging.error(f"Error converting Undertime value for EmpNo {item['EmpNo']}: {e}")
                hours_float = 0

            # Adjust the hours value using the scaling factor
            scaled_hours = hours_float * scaling_factor
            Undertime_value = scaled_hours * undertime_rate

            item['undertime'] = round(Undertime_value, 2)
            logging.info(f"Calculated late value for EmpNo {item['EmpNo']}: {item['undertime']}")
