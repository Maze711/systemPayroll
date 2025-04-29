from flask import Flask, request, jsonify
from MainFrame.Resources.lib import *


class NotificationService:
    def __init__(self):
        self.app = Flask(__name__)
        self.mysql_config = {
            # 'host': 'localhost',
            'host': '192.168.68.51',
            'database': 'NTP_ACCOUNTANT_NOTIFICATION',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        self.last_checked = 0
        self.polling = True
        self.server = None
        self.app.add_url_rule('/notifications', 'get_notifications', self.get_notifications, methods=['GET'])
        self.app.add_url_rule('/notification_count', 'get_notification_count', self.get_notification_count,
                              methods=['GET'])
        self.app.add_url_rule('/employee_details/<int:employee_id>', 'get_employee_details', self.get_employee_details,
                              methods=['GET'])

    def create_mysql_connection(self):
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            if connection.is_connected():
                return connection
            else:
                raise Exception("Failed to connect to MySQL database.")
        except mysql.connector.Error as e:
            return None

    def get_notifications(self):
        last_checked = request.args.get('last_checked', self.last_checked)
        try:
            last_checked = int(last_checked)
        except ValueError:
            last_checked = self.last_checked  # Fallback to the previous valid value

        connection = self.create_mysql_connection()
        if connection is None:
            return jsonify([])

        cursor = connection.cursor()
        query = """
            SELECT notif_count, surname, firstname, mi FROM paymaster_notification_user
            WHERE notif_count > %s ORDER BY notif_count ASC
        """
        cursor.execute(query, (last_checked,))
        notifications = cursor.fetchall()

        # Check if last_checked value exists in the current data
        if notifications:
            self.last_checked = notifications[-1][0]  # Update last_checked to the most recent value
        else:
            # If no notifications found, check if last_checked still exists
            query_check = "SELECT COUNT(*) FROM paymaster_notification_user WHERE notif_count = %s"
            cursor.execute(query_check, (last_checked,))
            if cursor.fetchone()[0] == 0:
                # If last_checked does not exist anymore, reset it to the maximum existing notif_count
                query_max = "SELECT COALESCE(MAX(notif_count), 0) FROM paymaster_notification_user"
                cursor.execute(query_max)
                max_notif_count = cursor.fetchone()[0]
                self.last_checked = max_notif_count

        cursor.close()
        connection.close()

        print(f"Requested last_checked: {last_checked}")
        print(f"Fetched notifications: {notifications}")
        print(f"Updated last_checked: {self.last_checked}")

        return jsonify(notifications)

    def get_notification_count(self):
        connection = self.create_mysql_connection()
        if connection is None:
            return jsonify({'count': 0})

        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM paymaster_notification_user"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return jsonify({'count': count})

    def get_total_notifications_count(self):
        try:
            connection = self.create_mysql_connection()
            if connection is None:
                return 0

            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM paymaster_notification_user"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            connection.close()

            return count
        except Exception as e:
            return 0

    def get_employee_details(self, employee_id):
        try:
            connection = self.create_mysql_connection()
            if connection is None:
                return None

            cursor = connection.cursor(dictionary=True)
            query = ("SELECT empl_id, CONCAT(surname, ' ', firstname, ' ', mi) AS fullname "
                     "FROM paymaster_notification_user WHERE notif_count = %s")
            cursor.execute(query, (employee_id,))
            details = cursor.fetchone()
            cursor.close()
            connection.close()

            if details:
                return details
            else:
                return {}
        except Exception as e:
            return {}

    def remove_employee_notification(self, empl_id):
        connection = self.create_mysql_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        query = "DELETE FROM paymaster_notification_user WHERE empl_id = %s"
        cursor.execute(query, (empl_id,))
        connection.commit()
        cursor.close()
        connection.close()

    def reorder_notifications(self):
        connection = self.create_mysql_connection()
        if connection is None:
            return

        try:
            cursor = connection.cursor()

            # Step 1: Create a variable to count and update each row in sequence
            query = "SET @count = 0;"
            cursor.execute(query)

            # Step 2: Update the notif_count for each row in the correct order
            query = """
            UPDATE paymaster_notification_user
            SET notif_count = (@count := @count + 1)
            ORDER BY id;
            """
            cursor.execute(query)

            connection.commit()

        except mysql.connector.Error as e:
            print(f"Error reordering notifications: {e}")
        finally:
            cursor.close()
            connection.close()

        # Reset the last_checked value to ensure all notifications are re-fetched
        self.last_checked = 0

    def start_server(self):
        self.server = self.app.run(port=5000, threaded=True)

    def stop(self):
        self.polling = False
        if self.server:
            # Shutdown the Flask server
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
        logging.info("NotificationService is stopping...")

    def poll_notifications(self):
        while self.polling:
            try:
                response = requests.get(f"http://localhost:5000/notifications?last_checked={self.last_checked}")
                notifications = response.json()

                if notifications:
                    for notification in notifications:
                        self.last_checked = notification[0]

            except requests.RequestException as e:
                time.sleep(10)

    def get_last_checked(self):
        return self.last_checked
