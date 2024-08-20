import sys
import os

from MainFrame.systemFunctions import globalFunction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *

from MainFrame.Database_Connection.DBConnection import create_connection


class ExportProcessor(QObject):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, data_dict, file_name):
        super().__init__()
        self.data_dict = data_dict
        self.file_name = file_name

    def process_export(self):
        """ Processes exporting data to an Excel file with progress updates. """
        try:
            chunksize = 10000  # Adjust this value based on your memory constraints
            combined_df = pd.concat(self.data_dict.values(), axis=1)
            total_rows = len(combined_df)
            current_row = 0

            if self.file_name.endswith('.csv'):
                # Export CSV in chunks
                for i in range(0, len(combined_df), chunksize):
                    mode = 'w' if i == 0 else 'a'
                    combined_df.iloc[i:i + chunksize].to_csv(self.file_name, mode=mode, index=False, header=(i == 0))
                    current_row += len(combined_df.iloc[i:i + chunksize])
                    progress = int((current_row / total_rows) * 100)
                    self.progressChanged.emit(progress)
            else:
                # Export XLSX in chunks
                with pd.ExcelWriter(self.file_name, engine='openpyxl') as writer:
                    for i in range(0, len(combined_df), chunksize):
                        combined_df.iloc[i:i + chunksize].to_excel(
                            writer, sheet_name='Employee Data',
                            startrow=writer.sheets['Employee Data'].max_row if i > 0 else 0,
                            header=(i == 0), index=False
                        )
                        current_row += len(combined_df.iloc[i:i + chunksize])
                        progress = int((current_row / total_rows) * 100)
                        self.progressChanged.emit(progress)

            self.finished.emit(f"Data successfully exported to {self.file_name}")

        except Exception as e:
            self.error.emit(f"Error exporting data to Excel: {e}")

class ExportLoader(QDialog):
    def __init__(self, data_dict, file_name):
        super(ExportLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        self.data_dict = data_dict
        self.file_name = file_name

        # Get UI elements
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = ExportProcessor(self.data_dict, self.file_name)
        self.worker.moveToThread(self.thread)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.worker.finished.connect(self.exportProcessingFinished)
        self.worker.error.connect(self.exportProcessingError)
        self.thread.started.connect(self.worker.process_export)
        self.thread.start()

        self.move_to_bottom_right()
        self.show()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.progressBar.setFormat("Finishing Up..")
        QApplication.processEvents()

    def exportProcessingFinished(self, message):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.information(self, "Export Complete", message)
        self.close()

    def exportProcessingError(self, error):
        self.progressBar.setVisible(False)
        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(self, "Export Error", f"An unexpected error occurred while exporting data:\n{error}")
        self.close()

    def move_to_bottom_right(self):
        """Position the dialog at the bottom right of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)

def fetch_personal_information():
    try:
        connection = create_connection('FILE201')
        if connection is None:
            logging.error("Could not establish database connection.")
            return None

        cursor = connection.cursor()

        tables = [
            "emp_info", "educ_information", "family_background", "emp_list_id",
            "work_exp", "tech_skills", "emp_posnsched", "emergency_list",
            "emp_rate", "emp_status", "vacn_sick_count"
        ]

        data_dict = {}

        for table_name in tables:
            logging.info(f"Fetching data from {table_name} table.")
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            data_dict[table_name] = df

        return data_dict

    except Exception as e:
        logging.error(f"Error fetching employee data: {e}")
        return None

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            logging.info("Database connection closed")

def export_to_excel(data_dict, file_name):
    try:
        # Create and show the progress dialog
        export_loader = ExportLoader(data_dict, file_name)
        export_loader.exec_()
    except Exception as e:
        logging.error(f"Error exporting data to Excel: {e}")