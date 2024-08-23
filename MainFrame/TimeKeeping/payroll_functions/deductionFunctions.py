import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.paytimeSheet.storeDeductionLoader import StoreDeductionLoader
from MainFrame.Database_Connection.user_session import UserSession

class DeductionUI:
    def __init__(self, parent):
        self.parent = parent
        self.user_session = UserSession().getALLSessionData()

    def populatePaytimeSheetTable(self, data):
        self.parent.paytimesheetTable.setRowCount(len(data) - 1)
        for row in range(self.parent.paytimesheetTable.rowCount()):
            self.parent.paytimesheetTable.setRowHidden(row, False)

        column_names = {
            'Emp Number': 'empnumber',
            'Bio Num': 'empnumber',
            'Employee Name': 'empname',
            'Late/Absent': 'late_absent',
            'SSS_Loan': 'sss_loan',
            'Pag_Ibig_Loan': 'pag_ibig_loan',
            'Cash_Advance': 'cash_advance',
            'Canteen': 'canteen',
            'Tax': 'tax',
            'SSS': 'sss',
            'Medicare/PhilHealth': 'medicare_philhealth',
            'PAGIBIG': 'pag_ibig',
            'Clinic': 'clinic',
            'Arayata_Annual': 'arayata_manual',
            'HMI': 'hmi',
            'Funeral': 'funeral',
            'Voluntary': 'voluntary'
        }

        headers = [col.lower().strip() if col else 'unknown' for col in data[0]]
        col_indices = {name: headers.index(col_name) for name, col_name in column_names.items() if col_name in headers}

        if not col_indices:
            logging.error("No matching columns found in headers.")
            return

        for i, row in enumerate(data[1:]):
            for field_name, col_name in column_names.items():
                col_idx = col_indices.get(field_name)
                if col_idx is not None:
                    item = QTableWidgetItem(str(row[col_idx]))
                    if field_name in column_names:
                        item.setTextAlignment(Qt.AlignCenter)
                    if field_name == 'Employee Name':
                        item.setToolTip(row[col_idx])
                    self.parent.paytimesheetTable.setItem(i, list(column_names.keys()).index(field_name), item)
                else:
                    logging.warning(f"Column '{field_name}' not found in data.")
            logging.info(f"Adding row {i}: {row}")

    def filterTable(self):
        search_text = self.parent.txtSearch.text().strip().lower()
        row_count = self.parent.paytimesheetTable.rowCount()

        for row in range(row_count):
            item = self.parent.paytimesheetTable.item(row, 1)  # Bio Num column is assumed to be index 1
            if item and search_text in item.text().strip().lower():
                self.parent.paytimesheetTable.setRowHidden(row, False)
            else:
                self.parent.paytimesheetTable.setRowHidden(row, True)

    def showDeductionUI(self):
        selected_row = self.parent.paytimesheetTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
            return

        try:
            emp_name_item = self.parent.paytimesheetTable.item(selected_row, 2)
            bio_num_item = self.parent.paytimesheetTable.item(selected_row, 1)

            # Fetch all deductions
            late_absent_item = self.parent.paytimesheetTable.item(selected_row, 3)
            sss_loan_item = self.parent.paytimesheetTable.item(selected_row, 4)
            pagibig_loan_item = self.parent.paytimesheetTable.item(selected_row, 5)
            cash_advance_item = self.parent.paytimesheetTable.item(selected_row, 6)
            canteen_item = self.parent.paytimesheetTable.item(selected_row, 7)
            tax_item = self.parent.paytimesheetTable.item(selected_row, 8)
            sss_item = self.parent.paytimesheetTable.item(selected_row, 9)
            medicare_philhealth_item = self.parent.paytimesheetTable.item(selected_row, 10)
            pagibig_item = self.parent.paytimesheetTable.item(selected_row, 11)
            clinic_item = self.parent.paytimesheetTable.item(selected_row, 12)
            arayata_annual_item = self.parent.paytimesheetTable.item(selected_row, 13)
            hmi_item = self.parent.paytimesheetTable.item(selected_row, 14)
            funeral_item = self.parent.paytimesheetTable.item(selected_row, 15)
            voluntary_item = self.parent.paytimesheetTable.item(selected_row, 16)

            # Each column/cell values
            emp_name = emp_name_item.text() if emp_name_item else ""
            bio_num = bio_num_item.text() if bio_num_item else ""

            deduction_values_mapping = {
                1: late_absent_item.text() if late_absent_item else "",
                2: sss_loan_item.text() if sss_loan_item else "",
                3: pagibig_loan_item.text() if pagibig_loan_item else "",
                4: cash_advance_item.text() if cash_advance_item else "",
                5: canteen_item.text() if canteen_item else "",
                6: tax_item.text() if tax_item else "",
                7: sss_item.text() if sss_item else "",
                8: medicare_philhealth_item.text() if medicare_philhealth_item else "",
                9: pagibig_item.text() if pagibig_item else "",
                10: clinic_item.text() if clinic_item else "",
                11: arayata_annual_item.text() if arayata_annual_item else "",
                12: hmi_item.text() if hmi_item else "",
                13: funeral_item.text() if funeral_item else "",
                14: voluntary_item.text() if voluntary_item else ""
            }

            ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\deduction.ui")
            self.deductionQDialog = QDialog()
            self.deductionQDialog.setFixedSize(780, 413)
            loadUi(ui_file, self.deductionQDialog)

            empNameTxt = self.deductionQDialog.findChild(QLabel, 'empNameTxt')
            bioNumTxt = self.deductionQDialog.findChild(QLabel, 'bioNumTxt')

            if empNameTxt:
                empNameTxt.setText(emp_name)
            if bioNumTxt:
                bioNumTxt.setText(bio_num)

            # Adding the values to each input fields (if there's any)
            for i in range(1, 15):
                self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}').setText(deduction_values_mapping[i])

            self.placeBTN = self.deductionQDialog.findChild(QPushButton, 'placeBTN')
            if self.placeBTN:
                self.placeBTN.clicked.connect(lambda: self.placeDeductions(self.deductionQDialog))
            else:
                logging.error("Error: placeBTN QPushButton not found in the deduction UI.")

            self.deductionQDialog.show()
            logging.info("Deduction UI loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load deduction UI: {e}")
            print(f"Failed to load deduction UI: {e}")

    def placeDeductions(self, dialog):
        try:
            selected_row = self.parent.paytimesheetTable.currentRow()
            if selected_row == -1:
                logging.warning("No row selected.")
                QMessageBox.warning(self.parent, "No Selection", "Please select a row from the table first.")
                return

            deductions_mapping = {
                1: 'Late/Absent',
                2: 'SSS_Loan',
                3: 'Pag_Ibig_Loan',
                4: 'Cash_Advance',
                5: 'Canteen',
                6: 'Tax',
                7: 'SSS',
                8: 'Medicare/PhilHealth',
                9: 'PAGIBIG',
                10: 'Clinic',
                11: 'Arayata_Annual',
                12: 'HMI',
                13: 'Funeral',
                14: 'Voluntary'
            }

            for i in range(1, 15):
                deduction_field = self.deductionQDialog.findChild(QLineEdit, f'txtDed{i}')

                if deduction_field and deduction_field.text().isdigit():
                    deduction_value = deduction_field.text()
                    deduction_column = self.getColumnIndex(deductions_mapping[i])

                    if deduction_column is not None:
                        item = QTableWidgetItem(deduction_value)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.parent.paytimesheetTable.setItem(selected_row, deduction_column, item)
                        logging.info(
                            f"Updated deduction {deductions_mapping[i]} for row {selected_row} with value {deduction_value}")
                    else:
                        logging.warning(f"Column for {deductions_mapping[i]} not found in the table.")

            QMessageBox.information(dialog, "Added Successfully", "Deduction/s was added successfully")
        except Exception as e:
            logging.error(f"Failed to place deductions: {e}")
            print(f"Failed to place deductions: {e}")

    def get_deduction_table_data(self):
        deduction_data = []

        row_count = self.parent.paytimesheetTable.rowCount()
        column_count = self.parent.paytimesheetTable.columnCount()

        deductions_column_mapping = {
            1: 'Late/Absent',
            2: 'SSS_Loan',
            3: 'Pag_Ibig_Loan',
            4: 'Cash_Advance',
            5: 'Canteen',
            6: 'Tax',
            7: 'SSS',
            8: 'Medicare/PhilHealth',
            9: 'PAGIBIG',
            10: 'Clinic',
            11: 'Arayata_Annual',
            12: 'HMI',
            13: 'Funeral',
            14: 'Voluntary'
        }

        for row_index in range(row_count):
            row_data = {}

            for column_index in range(column_count):
                column_name = self.parent.paytimesheetTable.horizontalHeaderItem(column_index).text()
                cell_item = self.parent.paytimesheetTable.item(row_index, column_index)
                cell_data = cell_item.text() if cell_item else None

                if column_name in deductions_column_mapping.values():
                    row_data[column_name] = int(cell_data) if cell_data else 0
                else:
                    row_data[column_name] = cell_data

            deduction_data.append(row_data)

        return deduction_data

    def showStoreDeductionLoader(self):
        message = QMessageBox.question(self.parent, "Storing Deduction into Database",
                                       "Are you sure you want to store all the data into database "
                                       "even though not all data has deductions?",
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if message == QMessageBox.Yes:
            self.deduction_data = self.get_deduction_table_data()
            self.storeDeductionLoader = StoreDeductionLoader(self.deduction_data, self.parent)
            self.storeDeductionLoader.show()

    def getColumnIndex(self, column_name):
        header_items = [self.parent.paytimesheetTable.horizontalHeaderItem(i).text()
                        for i in range(self.parent.paytimesheetTable.columnCount())]
        if column_name in header_items:
            return header_items.index(column_name)
        return -1

    def getBioNum(self, row):
        bio_num_item = self.parent.paytimesheetTable.item(row, 1)
        return bio_num_item.text() if bio_num_item else "Unknown"