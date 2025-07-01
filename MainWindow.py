from MainFrame.Resources.lib import *
from MainFrame.main_functions import MainWindowFunctions
from MainFrame.Database_Connection.notification_listener import NotificationService

import time


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

        # Initialize notification service asynchronously for faster startup
        self.notification_service = NotificationService()
        
        # Start service asynchronously to avoid blocking startup
        threading.Thread(
            target=self.notification_service.start_service_async,
            daemon=True
        ).start()

    def closeEvent(self, event):
        """ Stop the notification service when the MainWindow is closed """
        try:
            # Stop the notification service gracefully
            if hasattr(self, 'notification_service'):
                self.notification_service.stop()

            logging.info("NotificationService has stopped.")
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")
        finally:
            event.accept()


if __name__ == "__main__":
    start_time = time.time()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
