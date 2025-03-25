from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.timeSheet.timeSheet import TimeSheet


class processTimeSheetLoader(QDialog):
    """Displays a dialog with progress bar for visualization of creating timesheet"""
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

            # Get UI elements
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
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def fetchingDataFinished(self, metadata):
        [dataMerge, date_from, date_to, mach_code] = metadata

        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        dialog = TimeSheet(dataMerge, date_from, date_to, mach_code)
        dialog.exec_()

        self.close()
        self.parent.processTimeSheetLoader = None

    def fetchingDataError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self.parent, "Creating Timesheet Error", error)

        # Closes and reset the instance of dialog
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

    def process_creating_timesheet(self):
        """The main processor of timecard data for timesheet conversion"""
        try:
            if self.parent.TimeListTable.rowCount() == 0:
                self.error.emit("No rows detected!")
                return

            timesheet_data = []
            date_from = self.parent.dateFromCC.currentText()
            date_to = self.parent.dateToCC.currentText()

            # Collecting timesheet data
            for row in range(self.parent.TimeListTable.rowCount()):
                try:
                    bioNum = self.parent.TimeListTable.item(row, 1).text()
                    emp_name = self.parent.TimeListTable.item(row, 2).text()
                    trans_date = self.parent.TimeListTable.item(row, 3).text()
                    mach_code = self.parent.TimeListTable.item(row, 4).text()
                    check_in = self.parent.TimeListTable.item(row, 5).text()
                    check_out = self.parent.TimeListTable.item(row, 6).text()
                    sched_in = self.parent.TimeListTable.item(row, 7).text()
                    sched_out = self.parent.TimeListTable.item(row, 8).text()

                    # Validate the schedule before adding to timesheet data
                    # if not self.time_computation.validate_schedule(sched_in, sched_out, check_in, check_out, bioNum,
                    #                                                trans_date):
                    #     return  # Stop the process if validation fails

                    # Calculate late and undertime
                    late, undertime = self.time_computation.calculate_late_and_undertime(sched_in, sched_out, check_in,
                                                                                         check_out)

                    timesheet_data.append(
                        (bioNum, emp_name, trans_date, mach_code, check_in, check_out, sched_in, sched_out, late,
                         undertime)
                    )

                except Exception as e:
                    self.error.emit(f"Error processing row {row}: {e}")

            if not timesheet_data:
                self.error.emit("No valid data could be extracted.")
                return

            # Process timesheet data
            results = self.calculate_timesheet(timesheet_data)

            if not results:
                self.error.emit("No results generated.")
                return

            # Aggregate totals
            aggregated_results = {}
            total_hours_worked = total_nd_hours = total_ndot_hours = total_late = total_undertime = 0

            for result in results:
                bio_num = result['bio_num']
                total_hours_worked += result['total_hours']
                total_nd_hours += result['nd_hours']
                total_ndot_hours += result['ndot_hours']
                # total_late += result['late']
                # total_undertime += result['undertime']

                if bio_num not in aggregated_results:
                    aggregated_results[bio_num] = {
                        'emp_name': result['emp_name'],
                        'total_hours_worked': 0,
                        'nd_hours': 0,
                        'ndot_hours': 0,
                        'late': 0,
                        'undertime': 0,
                        'OrdDay_Hrs': 0,  # Added
                        'OrdDayOT_Hrs': 0,  # Added
                        'OrdDayND_Hrs': 0,  # Added
                        'OrdDayNDOT_Hrs': 0,  # Added
                        'RstDay_Hrs': 0,  # Added
                        'RstDayOT_Hrs': 0,  # Added
                        'RstDayND_Hrs': 0,  # Added
                        'RstDayNDOT_Hrs': 0,  # Added
                        'ordinary_day_hours': 0,
                        'reg_holiday_hours': 0,
                        'reg_holiday_ot_hours': 0,
                        'reg_holiday_nd_hours': 0,
                        'reg_holiday_ndot_hours': 0,
                        'spl_holiday_hours': 0,
                        'spl_holiday_ot_hours': 0,
                        'spl_holiday_nd_hours': 0,
                        'spl_holiday_ndot_hours': 0,
                        'days_work': set()
                    }

                # Modify the aggregation section to include ordinary day and rest day hours:
                # Aggregate results
                aggregated_results[bio_num]['total_hours_worked'] += result['total_hours']
                aggregated_results[bio_num]['nd_hours'] += result['nd_hours']
                aggregated_results[bio_num]['ndot_hours'] += result['ndot_hours']
                # aggregated_results[bio_num]['late'] += result['late']
                # aggregated_results[bio_num]['undertime'] += result['undertime']

                # Aggregate ordinary day hours
                if result.get('OrdDay_Hrs'):
                    aggregated_results[bio_num]['OrdDay_Hrs'] += result['OrdDay_Hrs']
                if result.get('OrdDayOT_Hrs'):
                    aggregated_results[bio_num]['OrdDayOT_Hrs'] += result['OrdDayOT_Hrs']
                if result.get('OrdDayND_Hrs'):
                    aggregated_results[bio_num]['OrdDayND_Hrs'] += result['OrdDayND_Hrs']
                if result.get('OrdDayNDOT_Hrs'):
                    aggregated_results[bio_num]['OrdDayNDOT_Hrs'] += result['OrdDayNDOT_Hrs']

                # Aggregate rest day hours
                if result.get('RstDay_Hrs'):
                    aggregated_results[bio_num]['RstDay_Hrs'] += result['RstDay_Hrs']
                if result.get('RstDayOT_Hrs'):
                    aggregated_results[bio_num]['RstDayOT_Hrs'] += result['RstDayOT_Hrs']
                if result.get('RstDayND_Hrs'):
                    aggregated_results[bio_num]['RstDayND_Hrs'] += result['RstDayND_Hrs']
                if result.get('RstDayNDOT_Hrs'):
                    aggregated_results[bio_num]['RstDayNDOT_Hrs'] += result['RstDayNDOT_Hrs']

                # Aggregate holiday hours directly from results
                if result.get('RegHlyday_Hrs'):
                    aggregated_results[bio_num]['reg_holiday_hours'] += result['RegHlyday_Hrs']
                if result.get('RegHlydayOT_Hrs'):
                    aggregated_results[bio_num]['reg_holiday_ot_hours'] += result['RegHlydayOT_Hrs']
                if result.get('RegHlydayND_Hrs'):
                    aggregated_results[bio_num]['reg_holiday_nd_hours'] += result['RegHlydayND_Hrs']
                if result.get('RegHlydayNDOT_Hrs'):
                    aggregated_results[bio_num]['reg_holiday_ndot_hours'] += result['RegHlydayNDOT_Hrs']
                if result.get('SplHlyday_Hrs'):
                    aggregated_results[bio_num]['spl_holiday_hours'] += result['SplHlyday_Hrs']
                if result.get('SplHlydayOT_Hrs'):
                    aggregated_results[bio_num]['spl_holiday_ot_hours'] += result['SplHlydayOT_Hrs']
                if result.get('SplHlydayND_Hrs'):
                    aggregated_results[bio_num]['spl_holiday_nd_hours'] += result['SplHlydayND_Hrs']
                if result.get('SplHlydayNDOT_Hrs'):
                    aggregated_results[bio_num]['spl_holiday_ndot_hours'] += result['SplHlydayNDOT_Hrs']

                aggregated_results[bio_num]['days_work'].add(result['trans_date'])

            # Prepare data for display
            dataMerge = []
            for i, (bio_num, data) in enumerate(aggregated_results.items()):
                total_aggregated_results = len(aggregated_results)

                dataMerge.append({
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
                })

            meta_data = [dataMerge, date_from, date_to, mach_code]
            self.finished.emit(meta_data)

        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")

    def calculate_timesheet(self, timesheet_data):
        results = []
        total_entries = len(timesheet_data)

        for i, entry in enumerate(timesheet_data):
            bio_num, emp_name, trans_date, mach_code, check_in, check_out, sched_in, sched_out, late, undertime = entry

            check_in_datetime = f"{trans_date} {check_in}"
            check_out_datetime = f"{trans_date} {check_out}"

            if datetime.strptime(check_out, "%H:%M:%S") < datetime.strptime(check_in, "%H:%M:%S"):
                check_out_date = datetime.strptime(trans_date, "%Y-%m-%d") + timedelta(days=1)
                check_out_datetime = f"{check_out_date.strftime('%Y-%m-%d')} {check_out}"

            # Calculate ND and NDOT
            _, nd_hours, ndot_hours = self.time_computation.calculate_hours(check_in_datetime, check_out_datetime)

            # Calculate total hours worked
            total_hours = (datetime.strptime(check_out_datetime, "%Y-%m-%d %H:%M:%S") -
                           datetime.strptime(check_in_datetime, "%Y-%m-%d %H:%M:%S")).total_seconds() / 3600


            # Check the holiday type using check_holiday_type function
            holiday_type = self.time_computation.check_holiday_type(trans_date)

            # Prepare result entry
            result_entry = {
                'bio_num': bio_num,
                'emp_name': emp_name,
                'trans_date': trans_date,
                'check_in': check_in,
                'check_out': check_out,
                'total_hours': round(total_hours, 2),
                'nd_hours': round(nd_hours, 2),
                'ndot_hours': round(ndot_hours, 2),
                'late': round(late, 2),
                'undertime': round(undertime, 2),
                'holiday_type': holiday_type  # Store the holiday type in the result
            }

            # Add holiday specific data if applicable
            holiday_type = self.time_computation.check_holiday_type(trans_date)
            if holiday_type:
                print(f"Found holiday type: {holiday_type} for date: {trans_date}")
                if holiday_type == 'Regular Holiday':
                    reg_hlyday_hours = total_hours
                    reg_hlyday_ot_hours = self.time_computation.calculate_overtime_hours(check_in_datetime,
                                                                                         check_out_datetime)
                    reg_hlyday_nd_hours = nd_hours
                    reg_hlyday_ndot_hours = ndot_hours
                    result_entry.update({
                        'RegHlyday_Hrs': reg_hlyday_hours,
                        'RegHlydayOT_Hrs': reg_hlyday_ot_hours,
                        'RegHlydayND_Hrs': reg_hlyday_nd_hours,
                        'RegHlydayNDOT_Hrs': reg_hlyday_ndot_hours
                    })
                elif holiday_type == 'Special Holiday':
                    spl_hlyday_hours = total_hours
                    spl_hlyday_ot_hours = self.time_computation.calculate_overtime_hours(check_in_datetime,
                                                                                         check_out_datetime)
                    spl_hlyday_nd_hours = nd_hours
                    spl_hlyday_ndot_hours = ndot_hours
                    result_entry.update({
                        'SplHlyday_Hrs': spl_hlyday_hours,
                        'SplHlydayOT_Hrs': spl_hlyday_ot_hours,
                        'SplHlydayND_Hrs': spl_hlyday_nd_hours,
                        'SplHlydayNDOT_Hrs': spl_hlyday_ndot_hours
                    })

                else:  # Ordinary Day
                    ord_day_ot_hours = self.time_computation.calculate_overtime_hours(check_in_datetime,
                                                                                      check_out_datetime)
                    result_entry.update({
                        'OrdDayOT_Hrs': ord_day_ot_hours,
                        'OrdDayND_Hrs': nd_hours,
                        'OrdDayNDOT_Hrs': ndot_hours
                    })

            else:  # Ordinary Day
                # Get total hours, ND hours and NDOT hours using existing calculate_hours method
                total_hours, nd_hours, ndot_hours = self.time_computation.calculate_hours(check_in_datetime,
                                                                                          check_out_datetime)

                # Get overtime hours using existing calculate_overtime_hours method
                overtime_hours = self.time_computation.calculate_overtime_hours(check_in_datetime, check_out_datetime)

                # Calculate regular hours (total hours minus overtime, capped at 8)
                regular_hours = min(total_hours, 8)  # Regular hours capped at 8

                result_entry.update({
                    'OrdDay_Hrs': regular_hours,
                    'OrdDayOT_Hrs': overtime_hours,
                    'OrdDayND_Hrs': nd_hours,
                    'OrdDayNDOT_Hrs': ndot_hours
                })

            results.append(result_entry)

            # Update progress for each entry processed
            progress = int(((i + 1) / total_entries) * 100)
            self.progressChanged.emit(progress)
            QThread.msleep(1)

        return results