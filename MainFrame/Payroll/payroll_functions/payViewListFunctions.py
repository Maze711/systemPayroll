from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class viewListFunctions:
    def __init__(self, parent):
        self.parent = parent
        self.data = []  # Initialize empty data

    def getEmpRate(self):
        """Retrieves salary details from emp_rate and employee info from emp_info"""
        connection = create_connection('NTP_EMP_LIST')

        if connection is None:
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database.")
            return []

        query = """
            SELECT 
                er.empl_id, 
                ei.empl_id AS bio_num,
                CONCAT(ei.surname, ', ', ei.firstname, ' ', COALESCE(ei.mi, '')) AS emp_name,
                er.rph, 
                er.rate, 
                er.mth_salary, 
                er.dailyallow, 
                er.mntlyallow
            FROM emp_rate er
            LEFT JOIN emp_info ei ON er.empl_id = ei.empl_id
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

                self.data = [
                    {
                        'EmpNo': str(row[0]),
                        'BioNum': str(row[1]) if row[1] else '',
                        'EmpName': row[2] if row[2] else '',
                        'RPH': row[3],
                        'Rate': row[4],
                        'Monthly Salary': row[5],
                        'Daily Allowance': row[6],
                        'Monthly Allowance': row[7],
                        'Basic': 0,
                        'SSS Loaned': 0,
                        'SSS Loan Amount': 0,
                        'Pag-Ibig Amount': 0
                    }
                    for row in results
                ]
        except Exception as e:
            QMessageBox.warning(self.parent, "Fetch Error", f"Error fetching salary details: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()

    def populateEmpSalaryList(self):
        if not self.data:
            self.getEmpRate()

        # Set the new row count
        self.parent.empSalaryList.setRowCount(len(self.data))

        for i, row in enumerate(self.data):
            emp_num = QTableWidgetItem(row['EmpNo'])
            bio_num = QTableWidgetItem(row['BioNum'])
            emp_name = QTableWidgetItem(row['EmpName'])
            rph = QTableWidgetItem(str(row['RPH']))
            rate = QTableWidgetItem(str(row['Rate']))
            basic = QTableWidgetItem(str(row['Basic']))
            monthly_salary = QTableWidgetItem(str(row['Monthly Salary']))
            daily_allowance = QTableWidgetItem(str(row['Daily Allowance']))
            monthly_allowance = QTableWidgetItem(str(row['Monthly Allowance']))
            sss_loaned = QTableWidgetItem(str(row['SSS Loaned']))
            sss_loan_amount = QTableWidgetItem(str(row['SSS Loan Amount']))
            pagibig_amount = QTableWidgetItem(str(row['Pag-Ibig Amount']))

            # Align all text to center
            for item in [emp_num, bio_num, emp_name, rph, rate, basic, monthly_salary, daily_allowance,
                         monthly_allowance, sss_loaned, sss_loan_amount, pagibig_amount]:
                item.setTextAlignment(Qt.AlignCenter)

            # Set tooltip for employee name
            emp_name.setToolTip(row['EmpName'])

            # Add items to the table
            self.parent.empSalaryList.setItem(i, 0, emp_num)
            self.parent.empSalaryList.setItem(i, 1, bio_num)
            self.parent.empSalaryList.setItem(i, 2, emp_name)
            self.parent.empSalaryList.setItem(i, 3, rph)
            self.parent.empSalaryList.setItem(i, 4, rate)
            self.parent.empSalaryList.setItem(i, 5, basic)
            self.parent.empSalaryList.setItem(i, 6, monthly_salary)
            self.parent.empSalaryList.setItem(i, 7, daily_allowance)
            self.parent.empSalaryList.setItem(i, 8, monthly_allowance)
            self.parent.empSalaryList.setItem(i, 9, sss_loaned)
            self.parent.empSalaryList.setItem(i, 10, sss_loan_amount)
            self.parent.empSalaryList.setItem(i, 11, pagibig_amount)

    def exportEmpRateList(self):
        """Exports the employee salary list to an Excel file."""
        if not self.data:
            QMessageBox.warning(self.parent, "Export Error", "No data available to export.")
            return

        df = pd.DataFrame(self.data)

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent, "Save As", "",
            "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if file_name:
            try:
                df.to_excel(file_name, index=False, sheet_name='EmployeeSalaryList')
                QMessageBox.information(self.parent, "Export Successful",
                                        f"Employee salary list has been successfully exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {e}")