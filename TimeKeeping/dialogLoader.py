import sys
import os
import logging
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
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
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Text File", "",
                                                  "DAT Files (*.DAT);;Text Files (*.txt);;All Files (*)")
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    content = file.read()
                    logging.info(f"File {fileName} content:\n{content}")
            except Exception as e:
                logging.error(f"Failed to read file {fileName}: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = dialogModal()
    dialog.show()
    sys.exit(app.exec_())
