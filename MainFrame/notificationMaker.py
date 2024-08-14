import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainFrame.Resources.lib import *
from MainFrame.systemFunctions import globalFunction
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.user_session import UserSession


class notificationLoader(QDialog):
    def __init__(self):
        super(notificationLoader, self).__init__()
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\showNotification.ui")
        loadUi(ui_file, self)
        self.setFixedSize(400, 124)

        # Get UI elements
        self.Message = self.findChild(QLabel, 'lblMessage')
        self.Time = self.findChild(QLabel, 'lblTime')
        self.Username = self.findChild(QLabel, 'lblUsername')

        self.user_role = UserSession().getALLSessionData().get("user_role", "")

        self.load_notifications()
        self.move_to_bottom_right()

    def load_notifications(self):
        """Load and display notifications relevant to the user's role."""
        connection = create_connection('SYSTEM_NOTIFICATION')
        if connection is None:
            logging.error("Failed to connect to SYSTEM_NOTIFICATION database.")
            return

        cursor = connection.cursor()
        try:
            # Query to fetch recent notifications for the current role
            query = """
                SELECT time, message, user_name 
                FROM send_notification 
                WHERE from_role = %s
                ORDER BY time DESC
                LIMIT 1
            """
            cursor.execute(query, (self.user_role,))
            result = cursor.fetchone()

            if result:
                time, message, user_name = result
                self.Time.setText(str(time))
                self.Message.setText(str(message))
                self.Username.setText(str(user_name))
            else:
                self.Message.setText("No new notifications.")
                self.Time.setText("")
                self.Username.setText("")

        except Error as e:
            logging.error(f"Error fetching notifications: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        dialog_rect = self.rect()

        x = screen_rect.width() - dialog_rect.width()
        y = screen_rect.height() - dialog_rect.height() - 40

        self.move(x, y)