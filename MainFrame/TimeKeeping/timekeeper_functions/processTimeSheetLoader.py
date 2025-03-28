from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.timeSheet.timeSheet import TimeSheet
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import math
from threading import Lock


class processTimeSheetLoader(QDialog):
    """Dialog with progress bar for timesheet creation"""

    def __init__(self, TimeComputation, timeCardWindow=None):
        super(processTimeSheetLoader, self).__init__(timeCardWindow)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)
        self.setModal(True)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        try:
            self.parent = timeCardWindow
            self.TimeComputation = TimeComputation
            self.progressBar = self.findChild(QProgressBar, 'progressBar')
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)

            self.thread = QThread()
            self.worker = CreateTimeSheetProcessor(self.parent, self.TimeComputation)
            self.worker.moveToThread(self.thread)
            self.worker.progressChanged.connect(self.updateProgressBar)
            self.worker.finished.connect(self.fetchingDataFinished)
            self.worker.error.connect(self.fetchingDataError)
            self.thread.started.connect(self.worker.process_creating_timesheet)
            self.thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Showing processTimeSheetLoader:\n{str(e)}")
            print("Error Showing processTimeSheetLoader: ", e)
            return

    def updateProgressBar(self, value):
        """Optimized progress updates with 5% granularity"""
        if abs(value - self.progressBar.value()) >= 5 or value == 100:
            self.progressBar.setValue(value)
            if value == 100:
                self.progressBar.setFormat("Finishing Up..")
            QApplication.processEvents()

    def fetchingDataFinished(self, metadata):
        """Handle successful completion"""
        try:
            [dataMerge, date_from, date_to, mach_code] = metadata
            self.progressBar.setVisible(False)
            self.thread.quit()
            self.thread.wait()

            dialog = TimeSheet(dataMerge, date_from, date_to, mach_code)
            dialog.exec_()

            self.close()
            self.parent.processTimeSheetLoader = None
        except Exception as e:
            print(f"Finalization error: {e}")

    def fetchingDataError(self, error):
        """Handle processing errors"""
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        QMessageBox.critical(self.parent, "Creating Timesheet Error", error)
        self.close()
        self.parent.processTimeSheetLoader = None


class CreateTimeSheetProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, timeCardWindow, TimeComputation):
        super().__init__()
        self.parent = timeCardWindow
        self.time_computation = TimeComputation
        self.holiday_cache = {}
        self.lock = Lock()
        self.mach_codes = set()

    def process_creating_timesheet(self):
        """Main processing workflow with enhanced error handling"""
        try:
            if not self.validate_input():
                return

            # Precompute holidays for all unique dates
            timesheet_data = self.collect_timesheet_data()
            if not timesheet_data:
                return

            self.precompute_holidays(timesheet_data)

            # Process in optimized batches
            results = self.process_in_batches(timesheet_data)
            if not results:
                self.error.emit("Something went wrong processing timesheet, please try again!")
                return

            # Prepare final output
            meta_data = self.prepare_final_metadata(results)
            if meta_data:
                self.finished.emit(meta_data)

        except Exception as e:
            self.error.emit(f"Processing failed: {str(e)}")

    def validate_input(self):
        """Validate table input before processing"""
        if self.parent.TimeListTable.rowCount() == 0:
            self.error.emit("No rows detected in timesheet table!")
            return False
        return True

    def collect_timesheet_data(self):
        """Collect and validate raw table data with mach_code tracking"""
        timesheet_data = []
        for row in range(self.parent.TimeListTable.rowCount()):
            try:
                items = [self.parent.TimeListTable.item(row, col).text()
                         for col in range(1, 9)]  # Columns 1-8

                if not all(items):
                    continue

                bioNum, emp_name, trans_date, mach_code, check_in, check_out, sched_in, sched_out = items

                # Validate the schedule before adding to timesheet data
                if not self.time_computation.validate_schedule(self, sched_in, sched_out, check_in, check_out,
                                                               bioNum, trans_date):
                    return  # Stop the process if validation fails

                self.mach_codes.add(mach_code)

                late, undertime = self.time_computation.calculate_late_and_undertime(
                    sched_in, sched_out, check_in, check_out)

                timesheet_data.append((
                    bioNum, emp_name, trans_date, mach_code,
                    check_in, check_out, sched_in, sched_out,
                    late, undertime
                ))
            except Exception as e:
                self.error.emit(f"Row {row} error: {str(e)}")
        return timesheet_data

    def precompute_holidays(self, timesheet_data):
        """Batch precompute holiday types for all unique dates"""
        unique_dates = {entry[2] for entry in timesheet_data}  # trans_date is at index 2
        self.holiday_cache = {
            date: self.time_computation.check_holiday_type(date)
            for date in unique_dates
        }

    def process_in_batches(self, timesheet_data):
        """Process data in parallel batches with progress updates"""
        batch_size = 50
        results = []
        total_batches = math.ceil(len(timesheet_data) / batch_size)
        last_reported = 0

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = start_idx + batch_size
            batch_results = list(self.process_batch_parallel(timesheet_data[start_idx:end_idx]))
            results.extend(batch_results)

            # Throttled progress reporting
            current_progress = int((batch_num + 1) / total_batches * 100)
            if current_progress - last_reported >= 5 or current_progress == 100:
                self.progressChanged.emit(current_progress)
                last_reported = current_progress

        return results

    def process_batch_parallel(self, batch):
        """Process batch using thread pool with error handling"""
        with ThreadPoolExecutor() as executor:
            for result in executor.map(self.process_single_entry, batch):
                if result:  # Skip None results from failed entries
                    yield result

    def process_single_entry(self, entry):
        """Process single timesheet entry with comprehensive validation"""
        try:
            bio_num, emp_name, trans_date, mach_code, check_in, check_out, _, _, late, undertime = entry

            # Time calculations with overnight shift handling
            check_in_dt = datetime.strptime(f"{trans_date} {check_in}", "%Y-%m-%d %H:%M:%S")
            check_out_dt = datetime.strptime(f"{trans_date} {check_out}", "%Y-%m-%d %H:%M:%S")

            if check_out_dt < check_in_dt:
                check_out_dt += timedelta(days=1)

            # Calculate ND and NDOT
            _, nd_hours, ndot_hours = self.time_computation.calculate_hours(
                check_in_dt.strftime("%Y-%m-%d %H:%M:%S"),
                check_out_dt.strftime("%Y-%m-%d %H:%M:%S")
            )

            # Calculate total hours worked
            total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600

            # Build result entry
            result_entry = {
                'bio_num': bio_num,
                'emp_name': emp_name,
                'trans_date': trans_date,
                'mach_code': mach_code,
                'total_hours': round(total_hours, 2),
                'nd_hours': round(nd_hours, 2),
                'ndot_hours': round(ndot_hours, 2),
                'late': round(late, 2),
                'undertime': round(undertime, 2),
                'holiday_type': self.holiday_cache.get(trans_date, '')
            }

            # Add holiday-specific calculations
            self.add_holiday_details(result_entry, check_in_dt, check_out_dt)
            return result_entry

        except Exception as e:
            self.error.emit(f"Entry processing error: {str(e)}")
            return None

    def add_holiday_details(self, result_entry, check_in_dt, check_out_dt):
        """Add holiday-specific time calculations"""
        holiday_type = result_entry['holiday_type']
        overtime = self.time_computation.calculate_overtime_hours(
            check_in_dt.strftime("%Y-%m-%d %H:%M:%S"),
            check_out_dt.strftime("%Y-%m-%d %H:%M:%S")
        )

        if holiday_type == 'Regular Holiday':
            result_entry.update({
                'RegHlyday_Hrs': result_entry['total_hours'],
                'RegHlydayOT_Hrs': overtime,
                'RegHlydayND_Hrs': result_entry['nd_hours'],
                'RegHlydayNDOT_Hrs': result_entry['ndot_hours']
            })
        elif holiday_type == 'Special Holiday':
            result_entry.update({
                'SplHlyday_Hrs': result_entry['total_hours'],
                'SplHlydayOT_Hrs': overtime,
                'SplHlydayND_Hrs': result_entry['nd_hours'],
                'SplHlydayNDOT_Hrs': result_entry['ndot_hours']
            })
        else:
            # Align with non-optimized version: cap OrdDay_Hrs at 8 for ordinary days
            result_entry.update({
                'OrdDay_Hrs': min(result_entry['total_hours'], 8),  # Capped at 8
                'OrdDayOT_Hrs': overtime,
                'OrdDayND_Hrs': result_entry['nd_hours'],
                'OrdDayNDOT_Hrs': result_entry['ndot_hours']
            })

    def prepare_final_metadata(self, results):
        """Prepare final output with validation"""
        if not results:
            self.error.emit("No valid results to output")
            return None

        date_from = self.parent.dateFromCC.currentText()
        date_to = self.parent.dateToCC.currentText()
        mach_code = results[0]['mach_code']

        aggregated = self.aggregate_results(results)
        if not aggregated:
            return None

        final_data = self.prepare_final_data(aggregated)
        return [final_data, date_from, date_to, mach_code]

    def aggregate_results(self, results):
        """Thread-safe aggregation of results"""
        aggregated = {}
        for result in results:
            bio_num = result['bio_num']
            with self.lock:
                if bio_num not in aggregated:
                    aggregated[bio_num] = self.init_employee_data(result)
                self.update_employee_data(aggregated[bio_num], result)
        return aggregated

    def init_employee_data(self, result):
        """Initialize employee data structure"""
        return {
            'emp_name': result['emp_name'],
            'total_hours_worked': 0.0,
            'nd_hours': 0.0,
            'ndot_hours': 0.0,
            'late': 0.0,
            'undertime': 0.0,
            'OrdDay_Hrs': 0.0,
            'OrdDayOT_Hrs': 0.0,
            'OrdDayND_Hrs': 0.0,
            'OrdDayNDOT_Hrs': 0.0,
            'RstDay_Hrs': 0.0,
            'RstDayOT_Hrs': 0.0,
            'RstDayND_Hrs': 0.0,
            'RstDayNDOT_Hrs': 0.0,
            'reg_holiday_hours': 0.0,
            'reg_holiday_ot_hours': 0.0,
            'reg_holiday_nd_hours': 0.0,
            'reg_holiday_ndot_hours': 0.0,
            'spl_holiday_hours': 0.0,
            'spl_holiday_ot_hours': 0.0,
            'spl_holiday_nd_hours': 0.0,
            'spl_holiday_ndot_hours': 0.0,
            'days_work': set()
        }

    def update_employee_data(self, employee_data, result):
        """Update aggregated employee data"""
        employee_data['total_hours_worked'] += result['total_hours']
        employee_data['nd_hours'] += result['nd_hours']
        employee_data['ndot_hours'] += result['ndot_hours']
        employee_data['late'] += result['late']
        employee_data['undertime'] += result['undertime']
        employee_data['days_work'].add(result['trans_date'])

        # Update all holiday-related fields
        for key in ['OrdDay', 'RstDay', 'RegHlyday', 'SplHlyday']:
            for suffix in ['_Hrs', 'OT_Hrs', 'ND_Hrs', 'NDOT_Hrs']:
                field = f"{key}{suffix}"
                if field in result:
                    employee_data[field] += result[field]

    def prepare_final_data(self, aggregated):
        """Format final output data"""
        required_fields = [
            'BioNum', 'Employee', 'Total_Hours_Worked',
            'Night_Differential', 'Days_Work'
        ]

        dataMerge = []
        for bio_num, data in aggregated.items():
            entry = {
                'BioNum': bio_num,
                'EmpNumber': bio_num,
                'Employee': data['emp_name'],
                'Total_Hours_Worked': f"{data['total_hours_worked']:.2f}",
                'Night_Differential': f"{data['nd_hours']:.2f}",
                'Night_Differential_OT': f"{data['ndot_hours']:.2f}",
                'Days_Work': len(data['days_work']),
                'Days_Present': len(data['days_work']),
                'Late': f"{data['late']:.2f}",
                'Undertime': f"{data['undertime']:.2f}",
                'OrdDay_Hrs': f"{data['OrdDay_Hrs']:.2f}",  # Added
                'OrdDayOT_Hrs': f"{data['OrdDayOT_Hrs']:.2f}",  # Added
                'OrdDayND_Hrs': f"{data['OrdDayND_Hrs']:.2f}",  # Added
                'OrdDayNDOT_Hrs': f"{data['OrdDayNDOT_Hrs']:.2f}",  # Added
                'RstDay_Hrs': f"{data['RstDay_Hrs']:.2f}",  # Added
                'RstDayOT_Hrs': f"{data['RstDayOT_Hrs']:.2f}",  # Added
                'RstDayND_Hrs': f"{data['RstDayND_Hrs']:.2f}",  # Added
                'RstDayNDOT_Hrs': f"{data['RstDayNDOT_Hrs']:.2f}",  # Added
                'SplHlyday_Hrs': f"{data['spl_holiday_hours']:.2f}",
                'SplHlydayOT_Hrs': data['spl_holiday_ot_hours'],
                'SplHlydayND_Hrs': data['spl_holiday_nd_hours'],
                'SplHlydayNDOT_Hrs': data['spl_holiday_ndot_hours'],
                'RegHlyday_Hrs': f"{data['reg_holiday_hours']:.2f}",
                'RegHlydayOT_Hrs': data['reg_holiday_ot_hours'],
                'RegHlydayND_Hrs': data['reg_holiday_nd_hours'],
                'RegHlydayNDOT_Hrs': data['reg_holiday_ndot_hours'],
                'SplHldyRD_Hrs': 0,
                'SplHldyRDOT_Hrs': 0,
                'SplHldyRDND_Hrs': 0,
                'SplHldyRDNDOT_Hrs': 0,
                'RegHldyRD_Hrs': 0,
                'RegHldyRDOT_Hrs': 0,
                'RegHldyRDND_Hrs': 0,
                'RegHldyRDNDOT_Hrs': 0,
            }

            # Verify required fields
            if not all(field in entry for field in required_fields):
                self.error.emit(f"Incomplete data for employee {bio_num}")
                continue

            dataMerge.append(entry)

        return dataMerge