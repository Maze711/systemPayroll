from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import globalFunction
import re


class timecard(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1442, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\timecard.ui")
        loadUi(ui_file, self)

        # Set up table
        self.TimeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.TimeListTable.horizontalHeader().setStretchLastSection(True)

        # Get UI elements
        self.yearCC = self.findChild(QComboBox, 'yearCC')
        self.dateFromCC = self.findChild(QComboBox, 'dateFromCC')
        self.dateToCC = self.findChild(QComboBox, 'dateToCC')

        # Initialize the year combo box
        self.populate_year_combo_box()

        # Connect signals to slots
        self.yearCC.currentTextChanged.connect(self.populate_date_combo_boxes)
        self.dateFromCC.currentTextChanged.connect(self.populate_time_list_table)
        self.dateToCC.currentTextChanged.connect(self.populate_time_list_table)

    def populate_year_combo_box(self):
        """Populate the year combo box with available years from table names."""
        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # Extract years from table names
            years = set()
            year_pattern = re.compile(r'from_(\d{4})')

            for (table_name,) in tables:
                match = year_pattern.search(table_name)
                if match:
                    years.add(match.group(1))

            # Add years to the combo box
            self.yearCC.addItems(sorted(years))

        except Exception as e:
            print(f"Error populating year combo box: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_date_combo_boxes(self):
        """Populate the date combo boxes based on the selected year."""
        selected_year = self.yearCC.currentText()
        if not selected_year:
            return

        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # Extract dates from table names
            date_from_set = set()
            date_to_set = set()

            date_pattern = re.compile(
                rf'from_{selected_year}(\d{{2}})(\d{{2}})_to_{selected_year}(\d{{2}})(\d{{2}})')

            for (table_name,) in tables:
                match = date_pattern.search(table_name)
                if match:
                    from_date = f"{match.group(1)}-{match.group(2)}"
                    to_date = f"{match.group(3)}-{match.group(4)}"

                    date_from_set.add(from_date)
                    date_to_set.add(to_date)

            # Update date combo boxes
            self.dateFromCC.addItems(sorted(date_from_set))
            self.dateToCC.addItems(sorted(date_to_set))

        except Exception as e:
            print(f"Error populating date combo boxes: {e}")

        finally:
            cursor.close()
            connection.close()

    def populate_time_list_table(self):
        """Populate the time list table with check-in and check-out times."""
        selected_year = self.yearCC.currentText()
        from_date = self.dateFromCC.currentText()
        to_date = self.dateToCC.currentText()

        if not selected_year or not from_date or not to_date:
            return

        # Format table name based on selected dates
        table_name = f"from_{selected_year}{from_date.replace('-', '')}_to_{selected_year}{to_date.replace('-', '')}"
        connection = create_connection('LIST_LOG_IMPORT')
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT bioNum, date, time, sched
                FROM `{table_name}`
                ORDER BY bioNum, date, time
            """)
            records = cursor.fetchall()

            # Clear existing rows in the table
            self.TimeListTable.setRowCount(0)
            time_data = {}

            for bio_num, trans_date, trans_time, sched in records:
                if bio_num not in time_data:
                    time_data[bio_num] = {"Check_In": None, "Check_Out": None}

                if sched == "Time IN":
                    time_data[bio_num]["Check_In"] = (trans_date, str(trans_time))
                elif sched == "Time OUT":
                    time_data[bio_num]["Check_Out"] = (trans_date, str(trans_time))

                # Add row to table if both check-in and check-out times are present
                if time_data[bio_num]["Check_In"] or time_data[bio_num]["Check_Out"]:
                    row_position = self.TimeListTable.rowCount()
                    self.TimeListTable.insertRow(row_position)

                    # Create QTableWidgetItem and set text alignment to center
                    def create_centered_item(text):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        return item

                    check_in_time = time_data[bio_num]["Check_In"][1] if time_data[bio_num]["Check_In"] else "Missing"
                    check_out_time = time_data[bio_num]["Check_Out"][1] if time_data[bio_num][
                        "Check_Out"] else "Missing"

                    self.TimeListTable.setItem(row_position, 0, create_centered_item(str(bio_num)))
                    self.TimeListTable.setItem(row_position, 2, create_centered_item(str(trans_date)))
                    self.TimeListTable.setItem(row_position, 4, create_centered_item(check_in_time))
                    self.TimeListTable.setItem(row_position, 5, create_centered_item(check_out_time))

                    # Reset data for this bio_num
                    time_data[bio_num] = {"Check_In": None, "Check_Out": None}

        except Exception as e:
            print(f"Error populating time list table: {e}")

        finally:
            cursor.close()
            connection.close()
