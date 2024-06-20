import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from Database_Connection.DBConnection import create_connection
from Employee_List.employeeList import EmployeeList
from FILE201.fontLoader import load_fonts

def main():
    app = QApplication(sys.argv)
    connection = create_connection()
    load_fonts()

    # Check if the connection was successful
    if connection is None:
        QMessageBox.critical(None, "Database Connection Error",
                             "Failed to connect to the database. The application will exit.")
        sys.exit(1)  # Exit the application
    else:
        ui = EmployeeList()
        ui.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
