from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, ValidInteger
from MainFrame.Database_Connection.notification_listener import NotificationService
from MainFrame.Payroll.payroll_functions.payaddEmpFunction import PayAddEmpFunction

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class payAddEmployee(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1065, 506)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\employeeList_Accountant.ui")
        loadUi(ui_file, self)
        validator = ValidInteger()

        validator.set_validators(self.dailyAllowTxt, self.monthlyAllowanceTxt, self.monthlySalaryTxt,
                                 self.rateTxt, self.rphTxt, self.sssTextEdit, self.pagibigTextEdit,
                                 self.philHealthTextEdit, self.tinTextEdit, self.txtTaxstat, self.txtAccount,
                                 self.txtBank, self.txtCola)

        self.notification_service = NotificationService()
        self.emp_functionality = PayAddEmpFunction(self.notification_service, self)

        self.emp_functionality.load_existing_employees()

        # Timer to check for new employees
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.emp_functionality.check_for_new_employees)
        self.timer.start(1000)

        self.pushButton.clicked.connect(self.add_employee_to_database)

    def add_employee_to_database(self):
        try:
            # Check if all required fields have valid data
            empl_id = self.bioNumTxt.text().strip()
            fullname = self.empNameTxt.text().strip()
            daily_allow = self.dailyAllowTxt.text().strip()
            monthly_allow = self.monthlyAllowanceTxt.text().strip()
            monthly_salary = self.monthlySalaryTxt.text().strip()
            rate = self.rateTxt.text().strip()
            rph = self.rphTxt.text().strip()

            if not all([empl_id, fullname, daily_allow, monthly_allow, monthly_salary, rate, rph]):
                QMessageBox.warning(self, "Invalid Input", "Please fill in all required fields.")
                return

            # Validate numeric inputs
            numeric_fields = {
                "Daily Allowance": daily_allow,
                "Monthly Allowance": monthly_allow,
                "Monthly Salary": monthly_salary,
                "Rate": rate,
                "Rate Per Hour": rph
            }

            for field_name, value in numeric_fields.items():
                try:
                    float(value)
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"{field_name} must be a valid number.")
                    return

            # Split the fullname into surname, firstname, and mi
            name_parts = fullname.split()
            surname = name_parts[0] if len(name_parts) > 0 else ""
            firstname = name_parts[1] if len(name_parts) > 1 else ""
            mi = name_parts[2] if len(name_parts) > 2 else ""

            # Database connection configuration
            db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'database': 'ntp_emp_rate'
            }

            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            try:
                # Step 1: Insert into user_info table
                query_user_info = """
                INSERT INTO user_info (empl_no, empl_id, empid, idnum, surname, firstname, mi)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_user_info, (
                    empl_id, empl_id, empl_id, empl_id, surname, firstname, mi
                ))

                # Step 2: Insert into emp_rate table
                query_emp_rate = """
                INSERT INTO emp_rate (empl_no, empl_id, empid, idnum, rph, rate, mth_salary, dailyallow, mntlyallow)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_emp_rate, (
                    empl_id, empl_id, empl_id, empl_id, rph, rate, monthly_salary, daily_allow, monthly_allow
                ))

                connection.commit()

                # Step 3: Use NotificationService to remove the employee and update notifications
                self.notification_service.remove_employee_notification(empl_id)
                self.notification_service.reorder_notifications()

                # Step 4: Refresh the employee list in the UI
                self.emp_functionality.load_existing_employees()

                QMessageBox.information(self, "Success",
                                        "Employee added to the database and notifications updated successfully!")

                # Clear the input fields after successful addition
                self.bioNumTxt.clear()
                self.empNameTxt.clear()
                self.dailyAllowTxt.clear()
                self.monthlyAllowanceTxt.clear()
                self.monthlySalaryTxt.clear()
                self.rateTxt.clear()
                self.rphTxt.clear()

            except mysql.connector.Error as err:
                connection.rollback()
                QMessageBox.critical(self, "Database Error", f"An error occurred while adding the employee: {err}")
            finally:
                cursor.close()
                connection.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")