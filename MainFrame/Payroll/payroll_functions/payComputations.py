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

    def regularDayEarnComputation(self):
        for item in self.data:
            try:
                daily_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0)
                days_work = float(
                    item.get('Present Days') if item.get(
                        'Present Days') != 'Missing' else 0)
            except ValueError:
                daily_rate = 0
                days_work = 0

            # Compute the regular day earn
            regular_day_earn = daily_rate * days_work

            item['RegDay_Earn'] = round(regular_day_earn, 2)
            logging.info(f"Calculated regular day  for EmpNo {item['EmpNo']}: {item['RegDay_Earn']}")

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

    def regularDayNightDiffComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                reg_day_night_diff_hours = float(
                    item.get('Regular Day Night Diff') if item.get(
                        'Regular Day Night Diff') != 'Missing' else 0)
            except ValueError:
                hourly_rate = 0
                reg_day_night_diff_hours = 0

            # Compute the regular day night differential rate
            night_diff_rate = 1.1  # Night Differential Rate of 10%
            regular_night_diff_rate_per_hour = hourly_rate * night_diff_rate
            regular_night_diff_total = reg_day_night_diff_hours * regular_night_diff_rate_per_hour

            item['RegDayNightDiffEarn'] = round(regular_night_diff_total, 2)
            logging.info(f"Calculated regular day night diff for EmpNo {item['EmpNo']}: {item['RegDayNightDiffEarn']}")

    def regularDayNightDiffOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                reg_day_nd_ot_hours = float(
                    item.get('Regular Day Night Diff OT') if item.get(
                        'Regular Day Night Diff OT') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Reg Day ND OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                reg_day_nd_ot_hours = 0

            # Regular Day Night Differential Overtime Computation
            overtime_rate = 1.25  # Overtime Rate of 120%
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            reg_day_nd_ot_value = hourly_rate * overtime_rate * night_diff_rate * reg_day_nd_ot_hours

            item['RegDayNightDiffOTEarn'] = round(reg_day_nd_ot_value, 2)
            logging.info(f"Calculated reg day nd ot value for EmpNo {item['EmpNo']}: {item['RegDayNightDiffOTEarn']}")

    def lateComputation(self):
        late_rate = 59.875  # Define the late

        for item in self.data:
            hours = item.get('Late')

            logging.info(f"Raw data for EmpNo {item['EmpNo']}: Late={hours}")

            try:
                hours_float = float(hours)
            except ValueError as e:
                logging.error(f"Error converting Late value for EmpNo {item['EmpNo']}: {e}")
                hours_float = 0

            late_undertime_value = hours_float * late_rate

            item['LateUndertime'] = round(late_undertime_value, 2)
            logging.info(f"Calculated late value for EmpNo {item['EmpNo']}: {item['LateUndertime']}")

    def undertimeComputation(self):
        undertime_rate = 59.875  # Define the undertime rate

        for item in self.data:
            hours = item.get('Undertime')

            logging.info(f"Raw data for EmpNo {item['EmpNo']}: Undertime={hours}")

            try:
                hours_float = float(hours)
            except ValueError as e:
                logging.error(f"Error converting Undertime value for EmpNo {item['EmpNo']}: {e}")
                hours_float = 0

            Undertime_value = hours_float * undertime_rate

            item['undertime'] = round(Undertime_value, 2)
            logging.info(f"Calculated late value for EmpNo {item['EmpNo']}: {item['undertime']}")

    def restDayComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_day_hours = float(item.get('Rest Day Hours') if item.get('Rest Day Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Rest Day and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_day_hours = 0

            # Rest Day Rate Computation
            rest_day_rate = 1.3  # rest day rate value (equivalent to 130%)
            rest_day_rate_per_hour = hourly_rate * rest_day_rate

            rest_day_rate_total = rest_day_hours * rest_day_rate_per_hour

            item['RestDay_Earn'] = round(rest_day_rate_total, 2)
            logging.info(f"Calculated rest day value for EmpNo {item['EmpNo']}: {item['RestDay_Earn']}")

    def restDayOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_day_ot_hours = float(
                    item.get('Rest Day OT Hours') if item.get('Rest Day OT Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Rest Day OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_day_ot_hours = 0

            # Rest Day Overtime Rate Computation
            rest_day_ot_rate = 1.69  # rest day ot rate value (equivalent to 169%)
            rest_day_ot_rate_per_hour = hourly_rate * rest_day_ot_rate

            rest_day_ot_rate_total = rest_day_ot_hours * rest_day_ot_rate_per_hour

            item['RestDayOT_Earn'] = round(rest_day_ot_rate_total, 2)
            logging.info(f"Calculated rest day ot value for EmpNo {item['EmpNo']}: {item['RestDayOT_Earn']}")

    def restDayNightDiffComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_day_nd_hours = float(
                    item.get('Rest Day Night Diff Hours') if item.get('Rest Day Night Diff Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Rest Day ND and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_day_nd_hours = 0

            # Rest Day Night Differential Rate Computation
            rest_day_rate = 1.3  # Rest Day Rate value (equivalent to 130%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            rest_day_nd_rate_per_hour = hourly_rate * rest_day_rate * night_diff_rate

            rest_day_nd_rate_total = rest_day_nd_hours * rest_day_nd_rate_per_hour

            item['RestDayND_Earn'] = round(rest_day_nd_rate_total, 2)
            logging.info(f"Calculated rest day nd value for EmpNo {item['EmpNo']}: {item['RestDayND_Earn']}")

    def restDayNightDiffOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_day_nd_ot_hours = float(
                    item.get('Rest Day Night Diff OT') if item.get('Rest Day Night Diff OT') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Rest Day ND OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_day_nd_ot_hours = 0

            # Rest Day Night Differential Overtime Rate Computation
            rest_day_ot_rate = 1.69  # rest day ot rate value (equivalent to 169%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            rest_day_nd_ot_rate_per_hour = hourly_rate * rest_day_ot_rate * night_diff_rate

            rest_day_nd_ot_rate_total = rest_day_nd_ot_hours * rest_day_nd_ot_rate_per_hour

            item['RestDayNDOT_Earn'] = round(rest_day_nd_ot_rate_total, 2)
            logging.info(f"Calculated rest day nd ot value for EmpNo {item['EmpNo']}: {item['RestDayNDOT_Earn']}")

    def regularHolidayComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                holiday_hours = float(item.get('Holiday Hours') if item.get('Holiday Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Holiday and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                holiday_hours = 0

            # Holiday Rate Computation
            holiday_rate = 2  # holiday rate value (equivalent to 200%)
            holiday_rate_per_hour = hourly_rate * holiday_rate

            holiday_rate_total = holiday_hours * holiday_rate_per_hour

            item['HolidayDay_Earn'] = round(holiday_rate_total, 2)
            logging.info(f"Calculated holiday value for EmpNo {item['EmpNo']}: {item['HolidayDay_Earn']}")

    def regularHolidayOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                holiday_ot_hours = float(
                    item.get('Holiday OT Hours') if item.get('Holiday OT Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Holiday OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                holiday_ot_hours = 0

            # Holiday OT Rate Computation
            holiday_ot_rate = 2.6  # holiday ot rate value (equivalent to 260%)
            holiday_ot_rate_per_hour = hourly_rate * holiday_ot_rate

            holiday_ot_rate_total = holiday_ot_hours * holiday_ot_rate_per_hour

            item['HolidayDayOT_Earn'] = round(holiday_ot_rate_total, 2)
            logging.info(f"Calculated holiday ot value for EmpNo {item['EmpNo']}: {item['HolidayDayOT_Earn']}")

    def regularHolidayNightDiffComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                holiday_nd_hours = float(
                    item.get('Holiday Night Diff Hours') if item.get('Holiday Night Diff Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting Holiday OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                holiday_nd_hours = 0

            # Holiday ND Rate Computation
            holiday_rate = 2  # holiday rate value (equivalent to 200%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            holiday_nd_rate_per_hour = hourly_rate * holiday_rate * night_diff_rate

            holiday_nd_rate_total = holiday_nd_hours * holiday_nd_rate_per_hour

            item['HolidayDayND_Earn'] = round(holiday_nd_rate_total, 2)
            logging.info(f"Calculated holiday ot value for EmpNo {item['EmpNo']}: {item['HolidayDayOT_Earn']}")

    def regularHolidayNightDiffOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                holiday_nd_ot_hours = float(
                    item.get('Holiday Night Diff OT') if item.get('Holiday Night Diff OT') != 'Missing' else 0)
            except ValueError as e:
                logging.error(
                    f"Error converting Regular holiday ND OT and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                holiday_nd_ot_hours = 0

            # Regular Holiday Night Differential Overtime Rate Computation
            holiday_ot_rate = 2.6  # holiday ot rate value (equivalent to 260%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            holiday_nd_ot_rate_per_hour = hourly_rate * holiday_ot_rate * night_diff_rate

            holiday_nd_ot_rate_total = holiday_nd_ot_hours * holiday_nd_ot_rate_per_hour

            item['HolidayNDOT_Earn'] = round(holiday_nd_ot_rate_total, 2)
            logging.info(
                f"Calculated regular holiday nd ot value for EmpNo {item['EmpNo']}: {item['HolidayNDOT_Earn']}")

    def restDayHolidayComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_holiday_hours = float(
                    item.get('Rest Holiday Hours') if item.get('Rest Holiday Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting rest holiday and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_holiday_hours = 0

            # Regular Holiday falls on Rest Day Rate Computation
            rest_holiday_rate = 2.6  # rest day holiday rate value (equivalent to 260%)
            rest_holiday_rate_per_hour = hourly_rate * rest_holiday_rate

            rest_holiday_rate_total = rest_holiday_hours * rest_holiday_rate_per_hour

            item['RestHolidayDay_Earn'] = round(rest_holiday_rate_total, 2)
            logging.info(f"Calculated rest holiday value for EmpNo {item['EmpNo']}: {item['RestHolidayDay_Earn']}")

    def restDayHolidayOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_holiday_ot_hours = float(
                    item.get('Rest Holiday OT Hours') if item.get('Rest Holiday OT Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting rest holiday ot and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_holiday_ot_hours = 0

            # Regular Holiday OT falls on Rest Day Rate Computation
            rest_holiday_ot_rate = 3.38  # rest day holiday ot rate value (equivalent to 338%)
            rest_holiday_ot_rate_per_hour = hourly_rate * rest_holiday_ot_rate

            rest_holiday_ot_rate_total = rest_holiday_ot_hours * rest_holiday_ot_rate_per_hour

            item['RestHolidayDayOT_Earn'] = round(rest_holiday_ot_rate_total, 2)
            logging.info(f"Calculated rest holiday ot value for EmpNo {item['EmpNo']}: {item['RestHolidayDayOT_Earn']}")

    def restDayHolidayNDComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_holiday_nd_hours = float(
                    item.get('Rest Holiday Night Diff Hours') if item.get(
                        'Rest Holiday Night Diff Hours') != 'Missing' else 0)
            except ValueError as e:
                logging.error(f"Error converting rest holiday nd and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_holiday_nd_hours = 0

            # Regular Holiday Night Differential falls on Rest Day Rate Computation
            rest_holiday_rate = 2.6  # rest day holiday rate value (equivalent to 260%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            rest_holiday_nd_rate_per_hour = hourly_rate * rest_holiday_rate * night_diff_rate

            rest_holiday_nd_rate_total = rest_holiday_nd_hours * rest_holiday_nd_rate_per_hour

            item['RestHolidayDayND_Earn'] = round(rest_holiday_nd_rate_total, 2)
            logging.info(f"Calculated rest holiday nd value for EmpNo {item['EmpNo']}: {item['RestHolidayDayND_Earn']}")

    def restDayHolidayNDOTComputation(self):
        for item in self.data:
            try:
                hourly_rate = float(item.get('Rate') if item.get('Rate') != 'Missing' else 0) / 8
                rest_holiday_nd_ot_hours = float(
                    item.get('Rest Holiday Night Diff OT') if item.get(
                        'Rest Holiday Night Diff OT') != 'Missing' else 0)
            except ValueError as e:
                logging.error(
                    f"Error converting rest holiday nd ot and hourly rate value for EmpNo {item['EmpNo']}: {e}")
                hourly_rate = 0
                rest_holiday_nd_ot_hours = 0

            # Regular Holiday Night Diff Overtime falls on Rest Day Rate Computation
            rest_holiday_ot_rate = 3.38  # rest day holiday ot rate value (equivalent to 338%)
            night_diff_rate = 1.1  # Night Differential Rate of 110%
            rest_holiday_nd_ot_rate_per_hour = hourly_rate * rest_holiday_ot_rate * night_diff_rate

            rest_holiday_nd_ot_rate_total = rest_holiday_nd_ot_hours * rest_holiday_nd_ot_rate_per_hour

            item['RestHolidayDayNDOT_Earn'] = round(rest_holiday_nd_ot_rate_total, 2)
            logging.info(
                f"Calculated rest holiday nd ot value for EmpNo {item['EmpNo']}: {item['RestHolidayDayNDOT_Earn']}")
