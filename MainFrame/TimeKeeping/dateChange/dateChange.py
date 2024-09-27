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
        self.cmbHoliday.currentIndexChanged.connect(self.fetch_holiday_data)
        self.btnUpdate.clicked.connect(self.update_or_cancel)
        self.btnAdd.clicked.connect(self.add_or_save_holiday)

        self.cmbHoliday.setEditable(False)
        self.dateEdit.setEnabled(False)
        self.cmbDateType.setEnabled(False)
        self.btnAdd.setEnabled(True)
        self.btnUpdate.setEnabled(False)

        self.add_mode = False

        self.load_holidays()
        self.load_date_types()

        self.reset_selection()

        self.original_items = [self.cmbHoliday.itemText(i) for i in range(self.cmbHoliday.count())]

    def load_holidays(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT holidayName FROM type_of_dates")
            holidays = cursor.fetchall()
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
            self.cmbDateType.clear()
            for date_type in date_types:
                if date_type[0]:
                    self.cmbDateType.addItem(date_type[0])
        except Error as e:
            logging.exception("Error while loading date types from MySQL: %s", e)
            QMessageBox.critical(self, "Error", "Failed to load date types")

    def reset_selection(self):
        self.cmbHoliday.setCurrentIndex(0)
        self.dateEdit.setDate(QDate.currentDate())
        self.cmbDateType.setCurrentIndex(1)

    def fetch_holiday_data(self, index=None):
        if self.add_mode:
            return

        holiday_name = self.cmbHoliday.currentText()
        if holiday_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT date, dateType, holidayIsMovable FROM type_of_dates WHERE holidayName = %s",
                               (holiday_name,))
                result = cursor.fetchone()
                cursor.fetchall()
                cursor.close()
                if result:
                    date, date_type, holiday_is_movable = result
                    date_str = date.strftime("%Y-%m-%d")
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
                "INSERT INTO type_of_dates (holidayName, date, dateType, holidayIsMovable) VALUES (%s, %s, %s, %s)",
                (holiday_name, new_date, date_type, 1))
            self.connection.commit()
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
            cursor.execute("UPDATE type_of_dates SET date = %s WHERE holidayName = %s", (new_date, holiday_name))
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