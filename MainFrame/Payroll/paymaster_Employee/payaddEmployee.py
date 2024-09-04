from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.notification_listener import NotificationService

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class payAddEmployee(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1065, 506)
        ui_file = globalFunction.resource_path("MainFrame/Resources/UI/employeeList_Accountant.ui")
        loadUi(ui_file, self)

        self.notification_service = NotificationService()
        self.emp_buttons = {}

        self.start_x = 20
        self.start_y = 60
        self.button_width = 223
        self.button_height = 50
        self.spacing = 10

        self.load_existing_employees()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_new_employees)
        self.timer.start(1000)

    def load_existing_employees(self):
        total_notifications_count = self.notification_service.get_total_notifications_count()
        for emp_id in range(1, total_notifications_count + 1):
            if emp_id not in self.emp_buttons:
                self.add_employee_button(emp_id)

    def add_employee_button(self, employee_id):
        y_position = self.start_y + (len(self.emp_buttons) * (self.button_height + self.spacing))
        emp_button = QPushButton(f"Employee {employee_id}", self)
        emp_button.setGeometry(self.start_x, y_position, self.button_width, self.button_height)
        emp_button.clicked.connect(lambda: self.on_empIDBtn_clicked(employee_id))
        self.emp_buttons[employee_id] = emp_button
        emp_button.show()
        self.update()

    def check_for_new_employees(self):
        total_notifications_count = self.notification_service.get_total_notifications_count()
        existing_ids = set(self.emp_buttons.keys())
        new_ids = set(range(1, total_notifications_count + 1)) - existing_ids
        for emp_id in new_ids:
            self.add_employee_button(emp_id)

    def on_empIDBtn_clicked(self, employee_id):
        try:
            details = self.notification_service.get_employee_details(employee_id)
            if details and 'fullname' in details:
                self.show_employee_details(details['fullname'])
            else:
                self.empNameTxt.setText(f"No details found for Employee ID {employee_id}")
        except Exception as e:
            self.empNameTxt.setText(f"Error fetching details for Employee ID {employee_id}")

    def show_employee_details(self, fullname):
        try:
            details_text = f"{fullname}"
            self.empNameTxt.setText(details_text)
        except Exception as e:
            self.empNameTxt.setText("Error displaying employee details")

    def add_new_employee(self, employee_id):
        self.add_employee_button(employee_id)
