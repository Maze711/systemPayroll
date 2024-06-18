import sys
from PyQt5.QtWidgets import QApplication
from Employee_List.employeeList import EmployeeList

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = EmployeeList()
    ui.show()
    sys.exit(app.exec_())