from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class earnings(QDialog):
    def __init__(self, parent=None):
        super(earnings, self).__init__(parent)
        self.setFixedSize(1065, 515)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\earnings.ui")
        loadUi(ui_file, self)

        self.parent = parent
        self.setupUIElements()
        self.displaySelectedEmployeeDetails()

    def setupUIElements(self):
        self.empNameTxt = self.findChild(QLabel, 'empNameTxt')
        self.bioNumTxt = self.findChild(QLabel, 'bioNumTxt')

        self.labels = {
            'Regular Day': self.findChild(QLabel, 'lblReg'),
            'Regular OT': self.findChild(QLabel, 'lblRegOT'),
            'Regular ND': self.findChild(QLabel, 'lblRegND'),
            'Regular NDOT': self.findChild(QLabel, 'lblRegNDOT'),
            'Special Hldy Restday': self.findChild(QLabel, 'lblSpclRD'),
            'Restday OT': self.findChild(QLabel, 'lblRDOT'),
            'Restday ND': self.findChild(QLabel, 'lblRDND'),
            'Restday NDOT': self.findChild(QLabel, 'lblRDNDOT'),
            'Holiday': self.findChild(QLabel, 'lblHldy'),
            'Holiday OT': self.findChild(QLabel, 'lblHldyOT'),
            'Holiday ND': self.findChild(QLabel, 'lblHldyND'),
            'Holiday NDOT': self.findChild(QLabel, 'lblHldyNDOT'),
            'SSS': self.findChild(QLabel, 'lblSSS'),
            'Pag-Ibig': self.findChild(QLabel, 'lblPagIbig'),
            'PhilHealth': self.findChild(QLabel, 'lblPhilHealth'),
            'Tax': self.findChild(QLabel, 'lblTax'),
            'SSS Loan': self.findChild(QLabel, 'lblSSSLoan'),
            'Pag-Ibig Loan': self.findChild(QLabel, 'lblPagIbigLoan'),
        }

        self.earningTotal = self.findChild(QLabel, 'earningTotal')
        self.deductionTotal = self.findChild(QLabel, 'deductionTotal')

    def displaySelectedEmployeeDetails(self):
        try:
            selected_row = self.parent.paytransTable.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select an employee from the table first.")
                self.close()
                return

            # Get employee data from the selected row
            employee_data = {}
            for col in range(self.parent.paytransTable.columnCount()):
                header = self.parent.paytransTable.horizontalHeaderItem(col).text()
                item = self.parent.paytransTable.item(selected_row, col)
                if item:
                    employee_data[header] = item.text()

            self.empNameTxt.setText(employee_data.get('Employee Name', ''))
            self.bioNumTxt.setText(employee_data.get('Bio Num', ''))

            earnings_mapping = {
                'Regular Day': ('OrdDay_Earn', 'Basic'),
                'Regular OT': ('OrdDayOT_Earn', None),
                'Regular ND': ('OrdDayND_Earn', None),
                'Regular NDOT': ('OrdDayNDOT_Earn', None),
                'Special Hldy Restday': ('RestHoli_Earn', None),
                'Restday OT': ('RestDayOT_Earn', None),
                'Restday ND': ('RestDayND_Earn', None),
                'Restday NDOT': ('RestDayNDOT_Earn', None),
                'Holiday': ('RegHldy_Earn', None),
                'Holiday OT': ('RegHldyOT_Earn', None),
                'Holiday ND': ('RegHldyND_Earn', None),
                'Holiday NDOT': ('RegHldyNDOT_Earn', None),
                'SSS': ('SSS', None),
                'Pag-Ibig': ('Pagibig', None),
                'PhilHealth': ('Medicare/Philhealth', None),
                'Tax': ('Tax', None),
                'SSS Loan': ('SSS_Loan', None),
                'Pag-Ibig Loan': ('Pagibig_Loan', None),
            }

            earnings_total = 0
            deductions_total = 0

            # Loop through the labels and display earnings/deductions
            for label_text, (key, alt_key) in earnings_mapping.items():
                label = self.labels.get(label_text)
                if label:
                    value = employee_data.get(key, '0')
                    if value == '0' and alt_key:
                        value = employee_data.get(alt_key, '0')

                    try:
                        float_value = float(value)
                    except ValueError:
                        float_value = 0.0

                    label.setText(f"₱{float_value:.2f}")
                    label.setAlignment(Qt.AlignCenter)

                    if label_text in ['SSS', 'Pag-Ibig', 'PhilHealth', 'Tax', 'SSS Loan', 'Pag-Ibig Loan']:
                        deductions_total += float_value
                    else:
                        earnings_total += float_value

            self.earningTotal.setText(f"₱{earnings_total:.2f}")
            self.earningTotal.setAlignment(Qt.AlignCenter)
            self.deductionTotal.setText(f"₱{deductions_total:.2f}")
            self.deductionTotal.setAlignment(Qt.AlignCenter)
            print("Employee data:", employee_data)

        except Exception as e:
            QMessageBox.critical(self, "Data Error", f"An error occurred while displaying employee details: {str(e)}")