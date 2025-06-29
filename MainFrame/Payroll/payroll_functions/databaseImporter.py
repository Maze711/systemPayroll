from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from PyQt5.QtWidgets import QFrame, QGridLayout

class DatabaseImporter(QDialog):
    def __init__(self, parent=None, callback_handler=None):
        super(DatabaseImporter, self).__init__(parent)
        self.parent = parent
        self.callback_handler = callback_handler
        self.selected_table = None
        self.tables_info = []
        self.setupUI()
        self.loadTimesheetTables()
        
    def setupUI(self):
        self.setWindowTitle("Database Importer")
        self.setMinimumSize(850, 650)
        self.resize(900, 700)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #dee2e6;
                border-radius: 15px;
            }
            QLabel {
                color: #495057;
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
                min-width: 160px;
                margin: 5px;
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
            QPushButton:disabled {
                background: #6c757d !important;
                color: #adb5bd !important;
                border: 2px solid transparent !important;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                background-color: white;
                selection-background-color: #e3f2fd;
                gridline-color: #e9ecef;
                font-size: 13px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #e9ecef;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QHeaderView::section {
                background-color: #495057;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            .import-button {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #007bff, stop: 1 #3498db);
            }
            .import-button:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0056b3, stop: 1 #2980b9);
            }
            .cancel-button {
                background-color: rgb(255, 110, 112);
            }
            .cancel-button:hover {
                background-color: rgb(255, 80, 83);
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title_label = QLabel("Database Importer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 8px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Select a timesheet table to import")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6c757d;
                margin-bottom: 15px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(subtitle_label)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["📋 Table Name", "📅 Date Range", "📊 Records"])
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        
        # Set column widths proportionally
        self.table_widget.setColumnWidth(0, 350)
        self.table_widget.setColumnWidth(1, 200)
        self.table_widget.setColumnWidth(2, 120)
        
        main_layout.addWidget(self.table_widget)
        
        # Button layout with proper spacing
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background: rgba(248, 249, 250, 0.9);
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                margin-top: 15px;
            }
        """)
        
        # Create a horizontal layout for the two buttons
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(15, 15, 15, 15)
        
        # Import button (blue)
        self.import_btn = QPushButton("📥 Import Selected")
        self.import_btn.setProperty("class", "import-button")
        self.import_btn.setStyleSheet(self.import_btn.styleSheet() + " .import-button")
        self.import_btn.setEnabled(False)
        self.import_btn.setToolTip("Import the selected timesheet table")
        
        # Cancel button (red)
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setProperty("class", "cancel-button")
        cancel_btn.setStyleSheet(cancel_btn.styleSheet() + " .cancel-button")
        cancel_btn.setToolTip("Close this dialog")
        
        # Add buttons to layout
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.table_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.import_btn.clicked.connect(self.import_selected_table)
        cancel_btn.clicked.connect(self.reject)
        
        # Set window properties for proper display
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setModal(True)
        
    def loadTimesheetTables(self):
        """Load available timesheet tables"""
        try:
            self.tables_info = self.getAvailableTimesheetTables()
            
            if not self.tables_info:
                self.show_no_tables_dialog()
                return
            
            # Populate table widget
            self.table_widget.setRowCount(len(self.tables_info))
            for row, (table_name, date_range, record_count) in enumerate(self.tables_info):
                # Table name
                name_item = QTableWidgetItem(table_name)
                name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                name_item.setFont(QFont("Arial", 10, QFont.Bold))
                
                # Date range
                date_item = QTableWidgetItem(date_range)
                date_item.setTextAlignment(Qt.AlignCenter)
                
                # Record count
                count_item = QTableWidgetItem(str(record_count))
                count_item.setTextAlignment(Qt.AlignCenter)
                count_item.setFont(QFont("Arial", 10, QFont.Bold))
                
                self.table_widget.setItem(row, 0, name_item)
                self.table_widget.setItem(row, 1, date_item)
                self.table_widget.setItem(row, 2, count_item)
                
                # Add row height for better spacing
                self.table_widget.setRowHeight(row, 40)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")
    
    def on_selection_changed(self):
        """Handle table selection change"""
        has_selection = self.table_widget.currentRow() >= 0
        self.import_btn.setEnabled(has_selection)
        
        if has_selection:
            current_row = self.table_widget.currentRow()
            self.selected_table = self.tables_info[current_row][0]
    
    def import_selected_table(self):
        """Import data from selected table"""
        if not self.selected_table:
            return
            
        try:
            # Show progress dialog
            progress_dialog = self.create_progress_dialog()
            progress_dialog.show()
            QApplication.processEvents()
            
            # Fetch data from selected table
            data = self.fetchDataFromTable(self.selected_table)
            
            progress_dialog.close()
            
            if data:
                # Signal successful import - call callback handler
                if self.callback_handler:
                    self.callback_handler.handle_database_import(self.selected_table, data)
                else:
                    # Fallback - just show success message
                    QMessageBox.information(self, "Import Successful", 
                                          f"Data imported successfully from {self.selected_table}!\nRecords: {len(data)-1}")
                
                # Signal successful import
                self.accept()
            else:
                QMessageBox.warning(self, "Import Failed", f"No data found in table {self.selected_table}.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import table data: {e}")
    
    def create_progress_dialog(self):
        """Create a modern progress dialog"""
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Importing Data")
        progress_dialog.setFixedSize(400, 150)
        progress_dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        label = QLabel("Importing data from database...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: #495057; margin-bottom: 20px;")
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate progress
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 5px;
                text-align: center;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        progress_dialog.setLayout(layout)
        
        return progress_dialog
    
    def getAvailableTimesheetTables(self):
        """Get list of available timesheet tables with their info"""
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ntp_post_timesheet"
            )
            cursor = conn.cursor()
            
            # Get all tables that start with 'timesheet_'
            cursor.execute("SHOW TABLES LIKE 'timesheet_%'")
            tables = cursor.fetchall()
            
            tables_info = []
            
            for table_tuple in tables:
                table_name = table_tuple[0]
                
                try:
                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    record_count = cursor.fetchone()[0]
                    
                    # Extract date range from table name
                    parts = table_name.split('_')
                    if len(parts) >= 6:
                        # Try to parse different possible formats
                        if len(parts) == 6:
                            # Format: timesheet_YYYY_MM_YYYY_MM_DD
                            date_range = f"{parts[1]}-{parts[2]} to {parts[3]}-{parts[4]}-{parts[5]}"
                        elif len(parts) >= 8:
                            # Format: timesheet_YYYY_MM_YYYY_MM_DD_YYYY_MM_DD
                            from_date = f"{parts[1]}-{parts[2]}-{parts[5]}"
                            to_date = f"{parts[6]}-{parts[7]}-{parts[8]}"
                            date_range = f"{from_date} to {to_date}"
                        else:
                            date_range = "Unknown format"
                    else:
                        date_range = "Unknown"
                    
                    tables_info.append((table_name, date_range, record_count))
                    
                except Exception as e:
                    # If there's an error getting info for this table, skip it
                    print(f"Error getting info for table {table_name}: {e}")
                    continue
            
            # Sort by table name (newest first)
            tables_info.sort(key=lambda x: x[0], reverse=True)
            
            return tables_info
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Database error: {err}")
            return []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error getting table list: {e}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    def fetchDataFromTable(self, table_name):
        """Fetch data from specific table"""
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ntp_post_timesheet"
            )
            cursor = conn.cursor()
            
            # Fetch data
            query = f"""
            SELECT 
                bio_num as BioNum,
                emp_num as EmpNumber,
                emp_name as Employee,
                cost_center as Cost_Center,
                days_work as Days_Work,
                days_present as Days_Present,
                total_hours_work as Total_Hours_Worked,
                late as Late,
                undertime as Undertime,
                ordday_hrs as OrdDay_Hrs,
                ordday_ot_hrs as OrdDayOT_Hrs,
                ordday_nd_hrs as Night_Differential,
                ordday_nd_ot_hrs as Night_Differential_OT,
                rstday_hrs as RstDay_Hrs,
                rstday_ot_hrs as RstDayOT_Hrs,
                rstday_nd_hrs as RstDayND_Hrs,
                rstday_nd_ot_hrs as RstDayNDOT_Hrs,
                spl_hldy_hrs as SplHlyday_Hrs,
                spl_hldy_ot_hrs as SplHlydayOT_Hrs,
                spl_hldy_nd_hrs as SplHlydayND_Hrs,
                spl_hldy_nd_ot_hrs as SplHlydayNDOT_Hrs,
                reg_hldy_hrs as RegHlyday_Hrs,
                reg_hldy_ot_hrs as RegHlydayOT_Hrs,
                reg_hldy_nd_hrs as RegHlydayND_Hrs,
                reg_hldy_nd_ot_hrs as RegHlydayNDOT_Hrs,
                spl_hldy_rd_hrs as SplHldyRD_Hrs,
                spl_hldy_rd_ot_hrs as SplHldyRDOT_Hrs,
                spl_hldy_rd_nd_hrs as SplHldyRDND_Hrs,
                spl_hldy_rd_nd_ot_hrs as SplHldyRDNDOT_Hrs,
                reg_hldy_rd_hrs as RegHldyRD_Hrs,
                reg_hldy_rd_ot_hrs as RegHldyRDOT_Hrs,
                reg_hldy_rd_nd_hrs as RegHldyRDND_Hrs,
                reg_hldy_rd_nd_ot_hrs as RegHldyRDNDOT_Hrs,
                absent as Absent,
                date_posted as Date_Posted,
                remarks as Remarks,
                emp_company as Emp_Company,
                legal_holiday as Legal_Holiday
            FROM `{table_name}`
            ORDER BY bio_num
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            data = []
            # Add header row
            data.append(columns)
            
            # Add data rows
            for row in rows:
                data.append(row)
            
            return data
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Database error: {err}")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error fetching data: {e}")
            return None
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    def show_no_tables_dialog(self):
        """Show a custom styled 'No Tables' dialog"""
        no_tables_dialog = QDialog(self)
        no_tables_dialog.setWindowTitle("No Tables")
        no_tables_dialog.setFixedSize(500, 300)
        no_tables_dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 3px solid #dee2e6;
                border-radius: 15px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
            QPushButton {
                border: 2px solid transparent;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                min-height: 40px;
                min-width: 120px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #007bff, stop: 1 #3498db);
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0056b3, stop: 1 #2980b9);
                border: 2px solid #ffffff;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Warning icon
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 64px;
                margin-bottom: 20px;
                color: #ffc107;
                font-weight: bold;
            }
        """)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("No Tables Found")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Main message
        message_label = QLabel("No timesheet tables found in the database.\nPlease check your database connection.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #495057;
                margin-bottom: 25px;
                padding: 10px;
                line-height: 1.6;
                font-weight: normal;
            }
        """)
        layout.addWidget(message_label)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(no_tables_dialog.accept)
        ok_button.setFixedWidth(140)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        no_tables_dialog.setLayout(layout)
        
        # Set window properties
        no_tables_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        no_tables_dialog.setModal(True)
        
        no_tables_dialog.exec_()
