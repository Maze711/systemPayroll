from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.systemFunctions import globalFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class DateChange(QDialog):
    def __init__(self):
        super(DateChange, self).__init__()
        self.setFixedSize(492, 376)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\datechange.ui")
        loadUi(ui_file, self)

        self.connection = create_connection('NTP_HOLIDAY_LIST')
        if not self.connection or not self.connection.is_connected():
            QMessageBox.critical(self, "Error", "Failed to connect to database")
            self.close()
            return

        # Verify database structure
        if not self.verify_database_structure():
            QMessageBox.critical(self, "Error", "Database table structure is incorrect")
            self.close()
            return

        self.add_mode = False
        self.original_items = []

        self.cmbHoliday.currentIndexChanged.connect(self.fetch_holiday_data)
        self.btnUpdate.clicked.connect(self.update_or_cancel)
        self.btnAdd.clicked.connect(self.add_or_save_holiday)

        self.cmbHoliday.setEditable(False)
        self.dateEdit.setEnabled(False)
        self.cmbDateType.setEnabled(False)
        self.btnAdd.setEnabled(True)
        self.btnUpdate.setEnabled(False)

        try:
            self.load_holidays()
            self.load_date_types()
            self.reset_selection()
            self.original_items = [self.cmbHoliday.itemText(i) for i in range(self.cmbHoliday.count())]
        except Exception as e:
            logging.exception("Error during initialization: %s", e)
            QMessageBox.critical(self, "Error", f"Failed to initialize: {str(e)}")
            self.close()
            return

    def load_holidays(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT holidayName FROM type_of_dates")
            holidays = cursor.fetchall()
            cursor.close()
            self.cmbHoliday.clear()
            for holiday in holidays:
                self.cmbHoliday.addItem(holiday[0])
        except Error as e:
            logging.exception("Error while loading holidays from MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to load holidays")

    def load_date_types(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT dateType FROM type_of_dates")
            date_types = cursor.fetchall()
            cursor.close()
            self.cmbDateType.clear()
            for date_type in date_types:
                if date_type[0]:
                    self.cmbDateType.addItem(date_type[0])
        except Error as e:
            logging.exception("Error while loading date types from MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to load date types")

    def reset_selection(self):
        if self.cmbHoliday.count() > 0:
            self.cmbHoliday.setCurrentIndex(0)
        self.dateEdit.setDate(QDate.currentDate())
        if self.cmbDateType.count() > 1:
            self.cmbDateType.setCurrentIndex(1)
        elif self.cmbDateType.count() > 0:
            self.cmbDateType.setCurrentIndex(0)

    def fetch_holiday_data(self, index=None):
        if self.add_mode:
            return

        holiday_name = self.cmbHoliday.currentText()
        if holiday_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT holidayDate, dateType, holidayIsMovable FROM type_of_dates WHERE holidayName = %s",
                               (holiday_name,))
                result = cursor.fetchone()
                cursor.close()
                if result:
                    date_str, date_type, holiday_is_movable = result
                    # Handle date as string since it's stored as varchar in database
                    if isinstance(date_str, str):
                        qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    else:
                        # In case it's somehow a date object
                        date_str = date_str.strftime("%Y-%m-%d")
                        qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    
                    self.dateEdit.setDate(qdate)
                    self.cmbDateType.setCurrentText(date_type)

                    self.dateEdit.setEnabled(holiday_is_movable == 1)
                    self.btnUpdate.setEnabled(holiday_is_movable == 1)

            except Error as e:
                logging.exception("Error while fetching data from MySQL: %s", e)
                QMessageBox.critical(self, "Error", "Failed to load data")

    def toggle_add_mode(self):
        self.add_mode = not self.add_mode
        if self.add_mode:
            self.cmbHoliday.setEditable(True)
            self.cmbHoliday.clearEditText()
            self.cmbHoliday.clear()
            self.dateEdit.setEnabled(True)
            self.cmbDateType.setEnabled(True)
            self.btnUpdate.setText("Cancel")
            self.btnUpdate.setEnabled(True)
            self.btnAdd.setText("Save")

            self.cmbDateType.setCurrentIndex(-1)
        else:
            self.cancel_add_mode()

    def update_or_cancel(self):
        if self.add_mode:
            self.cancel_add_mode()
        else:
            self.update_holiday_date()

    def cancel_add_mode(self):
        self.add_mode = False
        self.cmbHoliday.setEditable(False)
        self.cmbHoliday.clear()
        self.cmbHoliday.addItems(self.original_items)
        self.dateEdit.setEnabled(False)
        self.cmbDateType.setEnabled(False)
        self.btnAdd.setText("Add")
        self.btnUpdate.setText("Update")
        self.btnUpdate.setEnabled(False)
        self.reset_selection()

    def save_new_holiday(self):
        holiday_name = self.cmbHoliday.currentText()
        date_type = self.cmbDateType.currentText()
        new_date = self.dateEdit.date().toString("yyyy-MM-dd")

        if not holiday_name or not date_type:
            QMessageBox.warning(self, "Warning", "Please enter both holiday name and date type")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO type_of_dates (holidayName, holidayDate, dateType, holidayIsMovable) VALUES (%s, %s, %s, %s)",
                (holiday_name, new_date, date_type, 1))
            self.connection.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "New holiday added successfully")

            self.original_items.append(holiday_name)
            self.load_holidays()
            self.cmbHoliday.setCurrentText(holiday_name)

            self.toggle_add_mode()

        except Error as e:
            logging.exception("Error while adding new holiday to MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to add new holiday")

    def update_holiday_date(self, checked=False):
        holiday_name = self.cmbHoliday.currentText()
        new_date = self.dateEdit.date().toString("yyyy-MM-dd")

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE type_of_dates SET holidayDate = %s WHERE holidayName = %s", (new_date, holiday_name))
            self.connection.commit()
            cursor.close()  # Close the cursor
            QMessageBox.information(self, "Success", "Date updated successfully")
        except Error as e:
            logging.exception("Error while updating data in MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to update data")

    def showEvent(self, event):
        super().showEvent(event)
        self.reset_selection()
        if self.add_mode:
            self.cancel_add_mode()

    def add_or_save_holiday(self):
        if self.add_mode:
            self.save_new_holiday()
        else:
            self.toggle_add_mode()

    def verify_database_structure(self):
        """Verify that the database table exists and has the expected structure"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DESCRIBE type_of_dates")
            columns = cursor.fetchall()
            cursor.close()
            
            expected_columns = ['ID', 'holidayName', 'holidayDate', 'dateType', 'holidayIsMovable']
            actual_columns = [col[0] for col in columns]
            
            for expected_col in expected_columns:
                if expected_col not in actual_columns:
                    logging.error(f"Missing column: {expected_col}")
                    return False
            
            logging.info(f"Database structure verified. Columns: {actual_columns}")
            return True
            
        except Error as e:
            logging.exception("Error verifying database structure: %s", e)
            return False