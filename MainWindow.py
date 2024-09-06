from MainFrame.Resources.lib import *
from MainFrame.main_functions import MainWindowFunctions
from MainFrame.Database_Connection.notification_listener import NotificationService
import threading

class MainWindow(MainWindowFunctions):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.log_memory_usage("Before UI load")

        ui_file = self.resource_path("MainFrame/Resources/UI/Main.ui")
        loadUi(ui_file, self)

        self.setFixedSize(800, 600)
        self.initialize_widgets()
        self.setup_connections()
        self.setup_page_buttons()
        self.load_fonts()

    def closeEvent(self, event):
        """ Stop the notification service when the MainWindow is closed """
        if self.notification_thread.is_alive():
            self.notification_service.stop()
            self.notification_thread.join()
        logging.info("NotificationService has stopped.")
        event.accept()



if __name__ == "__main__":
    start_time = time.time()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
