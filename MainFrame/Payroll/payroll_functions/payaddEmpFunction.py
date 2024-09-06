from MainFrame.Resources.lib import *


class PayAddEmpFunction:
    def __init__(self, notification_service, parent):
        self.notification_service = notification_service
        self.emp_buttons = {}
        self.parent = parent  # Reference to the payAddEmployee UI

        # Button configuration properties
        self.start_x = 20
        self.start_y = 60
        self.button_width = 223
        self.button_height = 50
        self.spacing = 10

    def load_existing_employees(self):
        total_notifications_count = self.notification_service.get_total_notifications_count()
        for emp_id in range(1, total_notifications_count + 1):
            if emp_id not in self.emp_buttons:
                self.add_employee_button(emp_id)

    def add_employee_button(self, employee_id):
        y_position = self.start_y + (len(self.emp_buttons) * (self.button_height + self.spacing))
        emp_button = QPushButton(f"Employee {employee_id}", self.parent)
        emp_button.setGeometry(self.start_x, y_position, self.button_width, self.button_height)
        emp_button.clicked.connect(lambda: self.on_empIDBtn_clicked(employee_id))
        self.emp_buttons[employee_id] = emp_button
        emp_button.show()

    def check_for_new_employees(self):
        total_notifications_count = self.notification_service.get_total_notifications_count()
        existing_ids = set(self.emp_buttons.keys())
        new_ids = set(range(1, total_notifications_count + 1)) - existing_ids
        for emp_id in new_ids:
            self.add_employee_button(emp_id)

    def on_empIDBtn_clicked(self, employee_id):
        try:
            details = self.notification_service.get_employee_details(employee_id)
            if details and 'fullname' in details and 'empl_id' in details:
                self.show_employee_details(details['fullname'], details['empl_id'])
            else:
                self.parent.empNameTxt.setText(f"No details found for Employee ID {employee_id}")
                self.parent.bioNumTxt.setText("")  # Clear bioNumTxt if no details found
        except Exception as e:
            self.parent.empNameTxt.setText(f"Error fetching details for Employee ID {employee_id}")
            self.parent.bioNumTxt.setText("")

    def show_employee_details(self, fullname, empl_id):
        try:
            details_text = f"{fullname}"
            self.parent.empNameTxt.setText(details_text)
            self.parent.bioNumTxt.setText(str(empl_id))
        except Exception as e:
            self.parent.empNameTxt.setText("Error displaying employee details")
            self.parent.bioNumTxt.setText("Error displaying employee ID")
