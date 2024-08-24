import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction, timekeepingFunction
from MainFrame.Payroll.payTrans.payTransMailer import EmailerLoader
from MainFrame.Database_Connection.DBConnection import create_connection
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class PayTrans(QMainWindow):
    def __init__(self, from_date, to_date, data):
        super(PayTrans, self).__init__()
        self.setFixedSize(1700, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\paytrans.ui")
        loadUi(ui_file, self)

        self.data = data
        self.original_data = data  # Store original data
        self.from_date = from_date
        self.to_date = to_date

        self.paytransTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.paytransTable.horizontalHeader().setStretchLastSection(True)

        self.searchBioNum = self.findChild(QLineEdit, 'searchBioNum')
        if self.searchBioNum is not None:
            self.searchBioNum.textChanged.connect(lambda: timekeepingFunction.searchBioNumFunction(self))
        else:
            logging.error("Error: txtSearch QLineEdit not found in the UI.")

        self.populatePayTransTable(self.data)
        self.btnPayTrans.clicked.connect(self.export_to_excel)
        self.btnSendToEmail.clicked.connect(self.openEmailLoader)
        self.btnInsertDeduction.clicked.connect(self.insertDeductionToTable)

    def populatePayTransTable(self, data):
        for row in range(self.paytransTable.rowCount()):
            self.paytransTable.setRowHidden(row, False)

        self.paytransTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_no_item = QTableWidgetItem(row['EmpNo'])
            bio_num_item = QTableWidgetItem(row['BioNum'])
            emp_name_item = QTableWidgetItem(row['EmpName'])
            basic_item = QTableWidgetItem(str(row['Basic']))
            present_days_item = QTableWidgetItem(row['Present Days'])
            rate_item = QTableWidgetItem(row.get('Rate', 'Missing'))  # Get rate or 'Missing' if not found
            ordinary_day_ot_item = QTableWidgetItem(row.get('OrdinaryDayOT', 'N/A'))  # Add OrdinaryDayOT
            ot_earn_item = QTableWidgetItem(str(row['OT_Earn']))  # Get OT_Earn or '0.00' if not found

            # Adding deduction items to the table
            pay_ded_items = []
            for j in range(1, 15):
                deduction = row.get(f'Pay Ded {j}', '')
                pay_ded_items.append(QTableWidgetItem(str(deduction)))

            # Center all the items
            for item in [emp_no_item, bio_num_item, emp_name_item, basic_item, present_days_item, rate_item,
                         ordinary_day_ot_item, ot_earn_item] + pay_ded_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Set items in the table. Adjust the column indices as needed.
            self.paytransTable.setItem(i, 0, emp_no_item)
            self.paytransTable.setItem(i, 1, bio_num_item)
            self.paytransTable.setItem(i, 2, emp_name_item)
            self.paytransTable.setItem(i, 3, basic_item)  # Basic
            self.paytransTable.setItem(i, 4, rate_item)   # Rate
            self.paytransTable.setItem(i, 5, present_days_item)  # Present Days
            self.paytransTable.setItem(i, 6, ordinary_day_ot_item)  # OT Hours (add column index here)
            self.paytransTable.setItem(i, 14, ot_earn_item)  # OT Hours (add column index here)

            # Add deduction items to the table in subsequent columns
            for j, pay_ded_item in enumerate(pay_ded_items, start=52): # Pay Ded columns starts at index 52
                self.paytransTable.setItem(i, j, pay_ded_item)

    def export_to_excel(self, checked=False):
        # Define the file name where data will be saved
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "",
                                                   "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
        # file_name = "paytrans_data.xlsx"
            try:
                globalFunction.export_to_excel(self.data, file_name)
                QMessageBox.information(self, "Export Successful", f"Data has been successfully exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"An error occurred while exporting data: {e}")
                logging.error(f"Export error: {e}")
        else:
            QMessageBox.information(self, "No File Selected", "Please export an excel file.")
            return

    def insertDeductionToTable(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            QMessageBox.warning(self, "Connection Error", "Failed to connect to database. Please check your "
                                                          "connection or contact the system administrator")
            return

        cursor = connection.cursor()

        try:

            for index, row in enumerate(self.original_data):
                emp_no = row['EmpNo']
                query = f""" SELECT payDed1, payDed2, payDed3, payDed4, payDed5, payDed6, payDed7, payDed8, payDed9, 
                             payDed10, payDed11, payDed12, payDed13, payDed14 FROM deductions WHERE empNum = %s
                """
                cursor.execute(query, (emp_no,))
                result = cursor.fetchone()

                # Adds the deductions to each dictionary
                for i in range(0, 14):
                    row.update({f'Pay Ded {i + 1}': result[i]})

            QMessageBox.information(self, "Insertion Successful", "Inserting Deduction into the table has been "
                                                                  "successfully added!")
            # repopulate the table with the updated data
            self.populatePayTransTable(self.original_data)

        except Error as e:
            QMessageBox.warning(self, "Insertion Error", f"Error fetching or processing deduction data: {e}")
            print(f"Error fetching or processing deduction data: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def openEmailLoader(self):
        message = QMessageBox.question(self, "Sending Email", "Are you sure you want to send an email?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.emailerLoader = EmailerLoader(self.original_data, self)
            self.emailerLoader.show()