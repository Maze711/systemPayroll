from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class TimeSheet(QDialog):
    def __init__(self, data, lblFrom, lblTo, lblMach):
        super(TimeSheet, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = (globalFunction.resource_path("MainFrame\\Resources\\UI\\TimeSheet.ui"))
        loadUi(ui_file, self)

        self.data = data
        self.lblFrom = lblFrom
        self.lblTo = lblTo
        self.lblMach = lblMach
        self.setupTable()
        self.populateTimeSheet()
        self.setupLabels()

        self.btnExport.clicked.connect(self.export_to_excel)

        self.searchBioNum = self.findChild(QLineEdit, 'txtSearch_4')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

    def setupTable(self):
        self.TimeSheetTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeSheetTable.horizontalHeader().setStretchLastSection(True)

    def populateTimeSheet(self, data=None):
        if data is None:
            data = self.data

        self.TimeSheetTable.setRowCount(len(data))

        for i, row in enumerate(data):
            # Create QTableWidgetItems for each column
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_num_item = QTableWidgetItem(row['EmpNumber'])
            emp_name_item = QTableWidgetItem(row['Employee'])
            cost_center = QTableWidgetItem(row.get('Cost_Center', ''))
            days_work_item = QTableWidgetItem(str(row['Days_Work']))
            days_present_item = QTableWidgetItem(str(row['Days_Present']))
            total_hours_work_item = QTableWidgetItem(str(row['Total_Hours_Worked']))
            late_item = QTableWidgetItem(str(row['Late']))
            undertime_item = QTableWidgetItem(str(row['Undertime']))
            ordday_nd_hrs_item = QTableWidgetItem(str(row['Night_Differential']))
            ordday_nd_ot_hrs_item = QTableWidgetItem(str(row['Night_Differential_OT']))

            # Additional fields as per your request
            ordday_hrs_item = QTableWidgetItem(str(row.get('OrdDay_Hrs', 0)))
            ordday_ot_hrs_item = QTableWidgetItem(str(row.get('OrdDayOT_Hrs', 0)))
            rstday_hrs_item = QTableWidgetItem(str(row.get('RstDay_Hrs', 0)))
            rstday_ot_hrs_item = QTableWidgetItem(str(row.get('RstDayOT_Hrs', 0)))
            rstday_nd_hrs_item = QTableWidgetItem(str(row.get('RstDayND_Hrs', 0)))
            rstday_nd_ot_hrs_item = QTableWidgetItem(str(row.get('RstDayNDOT_Hrs', 0)))
            spl_hldy_hrs_item = QTableWidgetItem(str(row.get('SplHlyday_Hrs', 0)))
            spl_hldy_ot_hrs_item = QTableWidgetItem(str(row.get('SplHlydayOT_Hrs', 0)))
            spl_hldy_nd_hrs_item = QTableWidgetItem(str(row.get('SplHlydayND_Hrs', 0)))
            spl_hldy_nd_ot_hrs_item = QTableWidgetItem(str(row.get('SplHlydayNDOT_Hrs', 0)))
            reg_hldy_hrs_item = QTableWidgetItem(str(row.get('RegHlyday_Hrs', 0)))
            reg_hldy_ot_hrs_item = QTableWidgetItem(str(row.get('RegHlydayOT_Hrs', 0)))
            reg_hldy_nd_hrs_item = QTableWidgetItem(str(row.get('RegHlydayND_Hrs', 0)))
            reg_hldy_nd_ot_hrs_item = QTableWidgetItem(str(row.get('RegHlydayNDOT_Hrs', 0)))
            spl_hldy_rd_hrs_item = QTableWidgetItem(str(row.get('SplHldyRD_Hrs', 0)))
            spl_hldy_rd_ot_hrs_item = QTableWidgetItem(str(row.get('SplHldyRDOT_Hrs', 0)))
            spl_hldy_rd_nd_hrs_item = QTableWidgetItem(str(row.get('SplHldyRDND_Hrs', 0)))
            spl_hldy_rd_nd_ot_hrs_item = QTableWidgetItem(str(row.get('SplHldyRDNDOT_Hrs', 0)))
            reg_hldy_rd_hrs_item = QTableWidgetItem(str(row.get('RegHldyRD_Hrs', 0)))
            reg_hldy_rd_ot_hrs_item = QTableWidgetItem(str(row.get('RegHldyRDOT_Hrs', 0)))
            reg_hldy_rd_nd_hrs_item = QTableWidgetItem(str(row.get('RegHldyRDND_Hrs', 0)))
            reg_hldy_rd_nd_ot_hrs_item = QTableWidgetItem(str(row.get('RegHldyRDNDOT_Hrs', 0)))

            # Align all items to the center
            items = [
                bio_num_item, emp_num_item, emp_name_item, days_work_item, days_present_item, late_item, undertime_item,
                total_hours_work_item, cost_center, ordday_hrs_item, ordday_ot_hrs_item, ordday_nd_hrs_item,
                ordday_nd_ot_hrs_item, rstday_hrs_item, rstday_ot_hrs_item, rstday_nd_hrs_item, rstday_nd_ot_hrs_item,
                spl_hldy_hrs_item, spl_hldy_ot_hrs_item, spl_hldy_nd_hrs_item, spl_hldy_nd_ot_hrs_item,
                reg_hldy_hrs_item,
                reg_hldy_ot_hrs_item, reg_hldy_nd_hrs_item, reg_hldy_nd_ot_hrs_item, spl_hldy_rd_hrs_item,
                spl_hldy_rd_ot_hrs_item,
                spl_hldy_rd_nd_hrs_item, spl_hldy_rd_nd_ot_hrs_item, reg_hldy_rd_hrs_item, reg_hldy_rd_ot_hrs_item,
                reg_hldy_rd_nd_hrs_item, reg_hldy_rd_nd_ot_hrs_item
            ]
            for item in items:
                item.setTextAlignment(Qt.AlignCenter)

            # Set table items for each row
            self.TimeSheetTable.setItem(i, 0, bio_num_item)  # Bio No.
            self.TimeSheetTable.setItem(i, 1, emp_num_item)  # Employee No.
            self.TimeSheetTable.setItem(i, 2, emp_name_item)  # Employee Name
            self.TimeSheetTable.setItem(i, 3, cost_center)  # Employee Name
            self.TimeSheetTable.setItem(i, 4, days_work_item)  # Days Worked
            self.TimeSheetTable.setItem(i, 5, days_present_item)  # Days Present
            self.TimeSheetTable.setItem(i, 6, total_hours_work_item)  # Total Hours work
            self.TimeSheetTable.setItem(i, 7, late_item)  # Late
            self.TimeSheetTable.setItem(i, 8, undertime_item)  # Undertime
            self.TimeSheetTable.setItem(i, 9, ordday_hrs_item)  # Ord Day Hrs
            self.TimeSheetTable.setItem(i, 10, ordday_ot_hrs_item)  # Ord Day OT Hrs
            self.TimeSheetTable.setItem(i, 11, ordday_nd_hrs_item)  # Ord Day ND Hrs
            self.TimeSheetTable.setItem(i, 12, ordday_nd_ot_hrs_item)  # Ord Day ND OT Hrs
            self.TimeSheetTable.setItem(i, 13, rstday_hrs_item)  # Rest Day Hrs
            self.TimeSheetTable.setItem(i, 14, rstday_ot_hrs_item)  # Rest Day OT Hrs
            self.TimeSheetTable.setItem(i, 15, rstday_nd_hrs_item)  # Rest Day ND Hrs
            self.TimeSheetTable.setItem(i, 16, rstday_nd_ot_hrs_item)  # Rest Day ND OT Hrs
            self.TimeSheetTable.setItem(i, 17, spl_hldy_hrs_item)  # Special Holiday Hrs
            self.TimeSheetTable.setItem(i, 18, spl_hldy_ot_hrs_item)  # Special Holiday OT Hrs
            self.TimeSheetTable.setItem(i, 19, spl_hldy_nd_hrs_item)  # Special Holiday ND Hrs
            self.TimeSheetTable.setItem(i, 20, spl_hldy_nd_ot_hrs_item)  # Special Holiday ND OT Hrs
            self.TimeSheetTable.setItem(i, 21, reg_hldy_hrs_item)  # Regular Holiday Hrs
            self.TimeSheetTable.setItem(i, 22, reg_hldy_ot_hrs_item)  # Regular Holiday OT Hrs
            self.TimeSheetTable.setItem(i, 23, reg_hldy_nd_hrs_item)  # Regular Holiday ND Hrs
            self.TimeSheetTable.setItem(i, 24, reg_hldy_nd_ot_hrs_item)  # Regular Holiday ND OT Hrs
            self.TimeSheetTable.setItem(i, 25, spl_hldy_rd_hrs_item)  # Special Holiday Rest Day Hrs
            self.TimeSheetTable.setItem(i, 26, spl_hldy_rd_ot_hrs_item)  # Special Holiday Rest Day OT Hrs
            self.TimeSheetTable.setItem(i, 27, spl_hldy_rd_nd_hrs_item)  # Special Holiday Rest Day ND Hrs
            self.TimeSheetTable.setItem(i, 28, spl_hldy_rd_nd_ot_hrs_item)  # Special Holiday Rest Day ND OT Hrs
            self.TimeSheetTable.setItem(i, 29, reg_hldy_rd_hrs_item)  # Regular Holiday Rest Day Hrs
            self.TimeSheetTable.setItem(i, 30, reg_hldy_rd_ot_hrs_item)  # Regular Holiday Rest Day OT Hrs
            self.TimeSheetTable.setItem(i, 31, reg_hldy_rd_nd_hrs_item)  # Regular Holiday Rest Day ND Hrs
            self.TimeSheetTable.setItem(i, 32, reg_hldy_rd_nd_ot_hrs_item)  # Regular Holiday Rest Day ND OT Hrs

    def setupLabels(self):
        lblFrom_widget = self.findChild(QLabel, 'lblFrom')
        lblTo_widget = self.findChild(QLabel, 'lblTo')
        lblMach_widget = self.findChild(QLabel, 'lblMach')

        if lblFrom_widget is not None:
            lblFrom_widget.setText(self.lblFrom)
        else:
            logging.error("Error: lblFrom QLabel not found in the UI.")

        if lblTo_widget is not None:
            lblTo_widget.setText(self.lblTo)
        else:
            logging.error("Error: lblTo QLabel not found in the UI.")

        if lblMach_widget is not None:
            lblMach_widget.setText(self.lblMach)
        else:
            logging.error("Error: lblMach QLabel not found in the UI.")

    def export_to_excel(self):
        try:
            # Collect data from the table
            rows = self.TimeSheetTable.rowCount()
            columns = self.TimeSheetTable.columnCount()
            data = []

            for i in range(rows):
                row_data = []
                for j in range(columns):
                    item = self.TimeSheetTable.item(i, j)
                    row_data.append(item.text() if item is not None else "")
                data.append(row_data)

            header_columns = [self.TimeSheetTable.horizontalHeaderItem(i).text() for i in range(columns)]

            # Create a DataFrame from the collected data
            df = pd.DataFrame(data, columns=header_columns)

            # Prompt user to select the save location and filename
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "",
                                                       "Excel Files (*.xlsx);;All Files (*)", options=options)

            if file_path:
                # Save the DataFrame to an Excel file
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Data exported successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Export canceled.")
        except Exception as e:
            logging.error(f"Export to Excel failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while exporting the data:\n{str(e)}")