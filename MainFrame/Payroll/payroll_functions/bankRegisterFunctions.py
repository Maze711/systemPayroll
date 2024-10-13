from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class BankRegisterFunctions:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data
        self.getAccountNumber(self.data)

    def getAccountNumber(self, paytrans_data):
        """Retrieves the account_no from emp_list_id table"""
        connection = create_connection('NTP_EMP_LIST')
        if connection is None:
            print("Failed to connect to NTP_EMP_LIST database.")
            QMessageBox.warning(self.parent, "Connection Error",
                                "Failed to connect to database. Please check your "
                                "connection or contact the system administrator")
            return

        cursor = connection.cursor()
        query = 'SELECT account_no FROM emp_list_id WHERE empl_id = %s'
        try:
            for i, row in enumerate(paytrans_data):
                bio_num = int(row['BioNum'].strip())
                cursor.execute(query, (bio_num,))
                result = cursor.fetchone()
                row['AccountNo'] = result[0] if result is not None else 0

        except Exception as e:
            QMessageBox.warning(self.parent, "Fetch Error", f"Error fetching "
                                                                           f"Account number: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def getGrandTotal(self, paytrans_data):
        """Retrieves the grand total of all net pays"""
        netpays = []
        for row in paytrans_data:
            eachNetpay = float(row['Gross_Income'])
            netpays.append(eachNetpay)

        grand_total = sum(netpays)

        return round(grand_total, 2)

    def populateBankRegisterTable(self, data):
        for row in range(self.parent.bankregisterTable.rowCount()):
            self.parent.bankregisterTable.setRowHidden(row, False)

        self.parent.bankregisterTable.setRowCount(len(data))

        for i, row in enumerate(data):
            emp_num = QTableWidgetItem(row['EmpNo'])
            bio_num = QTableWidgetItem(row['BioNum'])
            emp_name = QTableWidgetItem(row['EmpName'])
            account_num = QTableWidgetItem(str(row['AccountNo']))
            net_pay = QTableWidgetItem(str(row['Gross_Income'])) # Tentatively Gross pay but should be net pay value

            for item in [emp_num, bio_num, emp_name, account_num, net_pay]:
                item.setTextAlignment(Qt.AlignCenter)
                if item == emp_name:
                    item.setToolTip(row['EmpName'])

            self.parent.bankregisterTable.setItem(i, 0, emp_num)
            self.parent.bankregisterTable.setItem(i, 1, bio_num)
            self.parent.bankregisterTable.setItem(i, 2, emp_name)
            self.parent.bankregisterTable.setItem(i, 3, account_num)
            self.parent.bankregisterTable.setItem(i, 4, net_pay)

    def exportBankRegisterToExcel(self):
        """Exports the bankRegister data into excel file"""
        try:
            rows = self.parent.bankregisterTable.rowCount()
            columns = self.parent.bankregisterTable.columnCount()

            # Gets the header columns
            headers = [self.parent.bankregisterTable.horizontalHeaderItem(i).text() for i in range(columns)]

            table_data = []

            # Iterate over rows and columns to retrieve data in the table UI
            for row in range(rows):
                row_data = []
                for col in range(columns):
                    item = self.parent.bankregisterTable.item(row, col)
                    if item:
                        item_text = item.text().strip()
                        # Converts the numeric text to float or integer
                        try:
                            value = float(item_text) if '.' in item_text else int(item_text)
                        except ValueError:
                            value = item_text
                        row_data.append(value)
                table_data.append(row_data)

            # Create the DataFrame from the table data
            df = pd.DataFrame(table_data, columns=headers)

            grand_total = float(self.parent.grandTotal.text().replace(',', ''))  # Get the grand total

            # Add the grand total in the last row
            total_row = [''] * (columns - 2) + ['Grand Total', grand_total]
            df.loc[len(df)] = total_row

            # Prompt the user to save the data to a specified file path
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self.parent, "Save As", "",
                                                       "Excel Files (*.xlsx);;Excel 97-2003 Files (*.xls);;"
                                                       "CSV Files (*.csv);;All Files (*)",
                                                       options=options)

            if file_name:
                try:
                    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='BankRegister')

                        workbook = writer.book
                        worksheet = writer.sheets['BankRegister']

                        # Creates a format for the 'Grand Total' row
                        format_grand_total = workbook.add_format({'align': 'right', 'bold': True, 'bottom': 6})
                        format_total_value = workbook.add_format({'bottom': 6,
                                                                  'num_format': '#,##0.00', 'bold': True})

                        # Apply the format to the 'Grand Total' row (last row of the DataFrame)
                        worksheet.write(f'D{len(df) + 1}', 'Grand Total', format_grand_total)
                        worksheet.write(f'E{len(df) + 1}', grand_total, format_total_value)

                    QMessageBox.information(self.parent, "Export Successful",
                                            f"BankRegister has been successfully exported to {file_name}")
                except Exception as e:
                    QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {e}")

        except Exception as es:
            QMessageBox.warning(self.parent, "Export Error", f"An error occurred while exporting data: {es}")
            print(f"Exporting Bank Register Error: {es}")