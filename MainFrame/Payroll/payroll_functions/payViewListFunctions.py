from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import ValidInteger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class viewListFunctions:
    def __init__(self, parent):
        self.parent = parent
        self.data = []  # Initialize empty data
        self.validator = ValidInteger()
        self.setup_double_click_handler()

    def getEmpRate(self):
        """Retrieves salary details from emp_rate and employee info from emp_info"""
        connection = create_connection('NTP_EMP_LIST')

        if connection is None:
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database.")
            return []

        query = """
            SELECT 
                er.empl_id, 
                ei.empid AS bio_num,
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

    def populateEmpSalaryList(self, data=None):
        if data is None:
            if not self.data:  # Ensure data is populated
                self.getEmpRate()
            data = self.data

        self.parent.empSalaryList.setRowCount(len(data))

        for i, row in enumerate(data):
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

            for item in [emp_num, bio_num, emp_name, rph, rate, basic, monthly_salary, daily_allowance,
                         monthly_allowance, sss_loaned, sss_loan_amount, pagibig_amount]:
                item.setTextAlignment(Qt.AlignCenter)

            emp_name.setToolTip(row['EmpName'])

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

    def setup_double_click_handler(self):
        """Sets up double-click handler for the table widget"""
        if hasattr(self.parent, 'empSalaryList'):
            self.parent.empSalaryList.cellDoubleClicked.connect(self.handle_cell_double_click)

    def handle_cell_double_click(self, row, column):
        """Handles double-click events on editable cells"""
        # Only allow editing for specific columns (3-RPH to 11-Pag-Ibig Amount)
        if 3 <= column <= 11:
            table = self.parent.empSalaryList
            item = table.item(row, column)

            if item is None:
                return

            # Get employee ID from the first column
            emp_id_item = table.item(row, 0)
            if emp_id_item is None:
                return

            emp_id = emp_id_item.text()
            column_name = self.get_column_name(column)

            # Create line edit for editing
            line_edit = QLineEdit(table)
            line_edit.setText(item.text())
            line_edit.setAlignment(Qt.AlignCenter)
            self.validator.set_validators(line_edit)

            # Set the line edit as the cell widget
            table.setCellWidget(row, column, line_edit)
            line_edit.setFocus()

            # Connect editing finished signal
            line_edit.editingFinished.connect(
                lambda: self.handle_edit_finished(row, column, line_edit, emp_id, column_name)
            )

    def get_column_name(self, column):
        """Maps column index to database column name"""
        column_map = {
            3: 'rph',
            4: 'rate',
            5: 'Basic',
            6: 'mth_salary',
            7: 'dailyallow',
            8: 'mntlyallow',
            9: 'SSS Loaned',
            10: 'SSS Loan Amount',
            11: 'Pag-Ibig Amount'
        }
        return column_map.get(column, '')

    def handle_edit_finished(self, row, column, line_edit, emp_id, column_name):
        """Handles when editing is finished (saves to database)"""
        table = self.parent.empSalaryList
        new_value = line_edit.text()

        # Remove the line edit widget
        table.removeCellWidget(row, column)

        # Update the table item
        item = QTableWidgetItem(new_value)
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, column, item)

        # Update the data structure
        if 0 <= row < len(self.data):
            self.data[row][column_name] = int(new_value) if new_value else 0

        # Update database
        self.update_database_value(emp_id, column_name, new_value)

    def update_database_value(self, emp_id, column_name, new_value):
        """Updates the database with the new value"""
        # Skip if it's one of the non-database columns (Basic, SSS, Pag-Ibig)
        if column_name in ['Basic', 'SSS Loaned', 'SSS Loan Amount', 'Pag-Ibig Amount']:
            return

        connection = create_connection('NTP_EMP_LIST')
        if connection is None:
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database.")
            return

        try:
            with connection.cursor() as cursor:
                # Convert empty string to NULL
                db_value = int(new_value) if new_value else None

                query = f"UPDATE emp_rate SET {column_name} = %s WHERE empl_id = %s"
                cursor.execute(query, (db_value, emp_id))
                connection.commit()

                QMessageBox.information(self.parent, "Update Successful",
                                        f"Updated {column_name} for employee {emp_id}")
        except Exception as e:
            QMessageBox.warning(self.parent, "Update Error", f"Error updating database: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()