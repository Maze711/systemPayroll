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

        # Initialize notification service
        self.notification_service = NotificationService()
        self.notification_thread = threading.Thread(target=self.notification_service.poll_notifications)
        self.server_thread = threading.Thread(target=self.notification_service.start_server)
        self.notification_thread.daemon = True
        self.server_thread.daemon = True
        self.notification_thread.start()
        self.server_thread.start()

    def closeEvent(self, event):
        """ Stop the notification service when the MainWindow is closed """
        try:
            # Stop the notification service
            if hasattr(self, 'notification_service'):
                self.notification_service.stop()

            # Wait for threads to finish (with timeout)
            if hasattr(self, 'notification_thread'):
                self.notification_thread.join(timeout=5)
            if hasattr(self, 'server_thread'):
                self.server_thread.join(timeout=5)

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