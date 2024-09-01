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

    def lateUndertimeComputation(self):
        late_and_undertime_rate = 59.875  # Define the late and undertime rate
        for item in self.data:
            days = item.get('Days')
            hours = item.get('Hours')

            try:
                days_float = float(days)
                hours_float = float(hours)
            except ValueError:
                days_float = 0
                hours_float = 0

            if hours_float > 0:
                late_undertime_value = (days_float / hours_float) * late_and_undertime_rate
            else:
                late_undertime_value = 0

            item['LateUndertime'] = round(late_undertime_value, 2)
            logging.info(f"Calculated late and undertime for EmpNo {item['EmpNo']}: {item['LateUndertime']}")