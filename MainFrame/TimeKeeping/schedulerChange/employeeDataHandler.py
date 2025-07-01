from MainFrame.Resources.lib import *
from MainFrame.Database_Connection.DBConnection import create_connection

class EmployeeDataHandler:
    def __init__(self, parent):
        self.parent = parent

    def load_employee_data(self):
        """Fill table with employee data"""
        cnx = create_connection('NTP_EMP_LIST')
        if not cnx:
            print("❌ DB connection failed.")
            return

        try:
            cur = cnx.cursor()
            cur.execute("SELECT idnum, surname, firstname, mi FROM emp_info")
            rows = cur.fetchall()

            self.parent.bankregisterTable.setRowCount(len(rows))
            self.parent.bankregisterTable.setColumnCount(5)

            # Set ComboBox delegate for Leave Type column (column 3)
            leave_types = ["SIL", "ML", "PL", "PL2", "VAWCL", "SLW"]
            combo_delegate = LeaveTypeComboBoxDelegate(leave_types)
            self.parent.bankregisterTable.setItemDelegateForColumn(3, combo_delegate)

            for r, (idnum, sur, fn, mi) in enumerate(rows):
                full_name = f"{sur}, {fn} {mi or ''}".strip()

                # EmpName
                name_item = QTableWidgetItem(full_name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.parent.bankregisterTable.setItem(r, 0, name_item)

                # BioNum
                id_item = QTableWidgetItem(str(idnum or ""))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.parent.bankregisterTable.setItem(r, 1, id_item)

                # Date Applied (empty)
                date_item = QTableWidgetItem("")
                date_item.setTextAlignment(Qt.AlignCenter)
                self.parent.bankregisterTable.setItem(r, 2, date_item)

                # Leave Type (default to SIL with dropdown arrow)
                leave_item = QTableWidgetItem("SIL ▼")
                leave_item.setTextAlignment(Qt.AlignCenter)
                self.parent.bankregisterTable.setItem(r, 3, leave_item)

                # Leave Note (empty)
                note_item = QTableWidgetItem("")
                note_item.setTextAlignment(Qt.AlignCenter)
                self.parent.bankregisterTable.setItem(r, 4, note_item)

        except Exception as e:
            print(f"❌ DB fetch error: {e}")
        finally:
            try:
                cur.close()
                cnx.close()
            except:
                pass


class LeaveTypeComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items):
        super().__init__()
        self.items = items

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.items)
        return combo

    def setEditorData(self, editor, index):
        value = index.data()
        # Remove the arrow symbol for comparison
        clean_value = value.replace(" ▼", "") if value else ""
        if clean_value in self.items:
            editor.setCurrentText(clean_value)
        else:
            editor.setCurrentText("SIL")

    def setModelData(self, editor, model, index):
        # Add arrow symbol to display
        new_value = editor.currentText() + " ▼"
        model.setData(index, new_value)
