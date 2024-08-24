import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Payroll.payTrans.payTransMailer import EmailerLoader
from MainFrame.Database_Connection.DBConnection import create_connection
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

class PayTransFunctions:
    def __init__(self, parent):
        self.parent = parent

    def populatePayTransTable(self, data):
        for row in range(self.parent.paytransTable.rowCount()):
            self.parent.paytransTable.setRowHidden(row, False)

        self.parent.paytransTable.setRowCount(len(data))

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
            self.parent.paytransTable.setItem(i, 0, emp_no_item)
            self.parent.paytransTable.setItem(i, 1, bio_num_item)
            self.parent.paytransTable.setItem(i, 2, emp_name_item)
            self.parent.paytransTable.setItem(i, 3, basic_item)  # Basic
            self.parent.paytransTable.setItem(i, 4, rate_item)   # Rate
            self.parent.paytransTable.setItem(i, 5, present_days_item)  # Present Days
            self.parent.paytransTable.setItem(i, 6, ordinary_day_ot_item)  # OT Hours (add column index here)
            self.parent.paytransTable.setItem(i, 14, ot_earn_item)  # OT Hours (add column index here)

            # Add deduction items to the table in subsequent columns
            for j, pay_ded_item in enumerate(pay_ded_items, start=52): # Pay Ded columns starts at index 52
                self.parent.paytransTable.setItem(i, j, pay_ded_item)

    def export_to_excel(self, checked=False):
        # Define the file name where data will be saved
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self.parent, "Save As", "",
                                                   "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                globalFunction.export_to_excel(self.parent.data, file_name)
                QMessageBox.information(self.parent, "Export Successful", f"Data has been successfully exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {e}")
                logging.error(f"Export error: {e}")
        else:
            QMessageBox.information(self.parent, "No File Selected", "Please export an excel file.")
            return

    def checkIfDeductionTableNotExist(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database. Please check your "
                                                                 "connection or contact the system administrator")
            return

        cursor = connection.cursor()

        try:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if len(tables) > 0:
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return
        finally:
            cursor.close()
            connection.close()

    def insertDeductionToTable(self):
        connection = create_connection('SYSTEM_STORE_DEDUCTION')
        if connection is None:
            print("Failed to connect to SYSTEM_STORE_DEDUCTION database.")
            QMessageBox.warning(self.parent, "Connection Error", "Failed to connect to database. Please check your "
                                                          "connection or contact the system administrator")
            return

        if self.checkIfDeductionTableNotExist():
            print("Deduction table does not exist in SYSTEM_STORE_DEDUCTION database.")
            QMessageBox.warning(self.parent, "Insert Error", "There are no processed deductions available. "
                                                             "Please contact Pay Master 2")
            return

        cursor = connection.cursor()

        try:

            for index, row in enumerate(self.parent.original_data):
                emp_no = row['EmpNo']
                query = f""" SELECT payDed1, payDed2, payDed3, payDed4, payDed5, payDed6, payDed7, payDed8, payDed9, 
                             payDed10, payDed11, payDed12, payDed13, payDed14 FROM deductions WHERE empNum = %s
                """
                cursor.execute(query, (emp_no,))
                result = cursor.fetchone()

                # Adds the deductions to each dictionary
                for i in range(0, 14):
                    row.update({f'Pay Ded {i + 1}': result[i]})

            QMessageBox.information(self.parent, "Insertion Successful", "Inserting Deduction into the table has been "
                                                                  "successfully added!")
            # repopulate the table with the updated data
            self.populatePayTransTable(self.parent.original_data)

        except Error as e:
            QMessageBox.warning(self.parent, "Insertion Error", f"Error fetching or processing deduction data: {e}")
            print(f"Error fetching or processing deduction data: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def openEmailLoader(self):
        message = QMessageBox.question(self.parent, "Sending Email", "Are you sure you want to send an email?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.emailerLoader = EmailerLoader(self.parent.original_data, self.parent)
            self.emailerLoader.show()