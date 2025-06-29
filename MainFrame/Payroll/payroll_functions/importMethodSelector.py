from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

class ImportMethodSelector(QDialog):
    def __init__(self, parent=None):
        super(ImportMethodSelector, self).__init__(parent)
        self.parent = parent
        self.selected_method = None
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Import Method")
        self.setMinimumSize(550, 450)
        self.resize(550, 450)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #dee2e6;
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            QPushButton {
                border: 2px solid transparent;
                border-radius: 12px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                min-height: 45px;
                margin: 8px 0px;
                text-align: center;
            }
            QPushButton:hover {
                border: 2px solid #ffffff;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                border: 2px solid #cccccc;
                transform: scale(0.98);
            }
            .import-excel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #28a745, stop: 1 #20c997);
            }
            .import-excel:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #218838, stop: 1 #1fa085);
            }
            .import-database {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #007bff, stop: 1 #3498db);
            }
            .import-database:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0056b3, stop: 1 #2980b9);
            }
            .cancel-button {
                background-color: rgb(255, 110, 112);
                min-height: 35px;
            }
            .cancel-button:hover {
                background-color: rgb(255, 80, 83);
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Choose Import Method")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Select your preferred data source")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 15px;
                padding: 3px;
            }
        """)
        main_layout.addWidget(subtitle_label)
        
        # Spacer
        main_layout.addStretch(1)
        
        # Excel import button
        excel_btn = QPushButton("📊 Import from Excel File")
        excel_btn.setProperty("class", "import-excel")
        excel_btn.setStyleSheet(excel_btn.styleSheet() + " .import-excel")
        excel_btn.setToolTip("Import timesheet data from Excel files (.xls, .xlsx)")
        excel_btn.clicked.connect(lambda: self.select_method("excel"))
        main_layout.addWidget(excel_btn)
        
        # Database import button
        database_btn = QPushButton("🗄️ Import from Database")
        database_btn.setProperty("class", "import-database")
        database_btn.setStyleSheet(database_btn.styleSheet() + " .import-database")
        database_btn.setToolTip("Import timesheet data from the database")
        database_btn.clicked.connect(lambda: self.select_method("database"))
        main_layout.addWidget(database_btn)
        
        # Spacer
        main_layout.addStretch(2)
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setProperty("class", "cancel-button")
        cancel_btn.setStyleSheet(cancel_btn.styleSheet() + " .cancel-button")
        cancel_btn.clicked.connect(self.reject)
        main_layout.addWidget(cancel_btn)
        
        self.setLayout(main_layout)
        
        # Set window properties for proper display
        self.setWindowFlags(Qt.Dialog)
        self.setModal(True)
        
    def select_method(self, method):
        self.selected_method = method
        self.accept()
        
    def get_selected_method(self):
        return self.selected_method
