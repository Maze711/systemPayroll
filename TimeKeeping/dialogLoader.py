import sys
import os
import logging
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QWidget
from PyQt5.uic import loadUi

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='file_import.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')


class dialogModal(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(418, 392)
        loadUi(os.path.join(os.path.dirname(__file__), 'dialogImporter.ui'), self)
        self.importBTN.clicked.connect(self.importTxt)

    def importTxt(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text or DAT File", "",
                                                  "Text Files (*.txt);;DAT Files (*.DAT);;All Files (*)")
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    content = file.read()
                    logging.info(f"File {fileName} content:\n{content}")
                    self.showData(content)
            except Exception as e:
                logging.error(f"Failed to read file {fileName}: {e}")

    def showData(self, content):
        frame = QMainWindow()
        frame.setWindowTitle("Imported Data")
        frame.setGeometry(100, 100, 600, 400)
        central_widget = QWidget(frame)
        layout = QVBoxLayout(central_widget)

        table = QTableWidget()
        table.setRowCount(0)
        table.setColumnCount(4)

        # Set table headers
        headers = ["Bio No.", "TransDate", "Time", "MachCode"]
        table.setHorizontalHeaderLabels(headers)

        # Populate the table with data
        rows = content.strip().split('\n')
        for row in rows:
            columns = row.split('\t')
            bio_no = columns[0].strip()
            trans_date, time = columns[1].strip().split(' ')
            mach_code = columns[2].strip()
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(bio_no))
            table.setItem(row_position, 1, QTableWidgetItem(trans_date))
            table.setItem(row_position, 2, QTableWidgetItem(time))
            table.setItem(row_position, 3, QTableWidgetItem(mach_code))

        layout.addWidget(table)
        frame.setCentralWidget(central_widget)
        frame.show()
        self.frame = frame


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = dialogModal()
    dialog.show()
    sys.exit(app.exec_())
