from flask import Flask, request, jsonify
import mysql.connector
import requests
import time
import threading

class NotificationService:
    def __init__(self):
        self.app = Flask(__name__)
        self.mysql_config = {
            'host': 'localhost',
            'database': 'NTP_ACCOUNTANT_NOTIFICATION',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        self.last_checked = 0
        self.app.add_url_rule('/notifications', 'get_notifications', self.get_notifications, methods=['GET'])
        self.app.add_url_rule('/notification_count', 'get_notification_count', self.get_notification_count, methods=['GET'])
        self.app.add_url_rule('/employee_details/<int:employee_id>', 'get_employee_details', self.get_employee_details, methods=['GET'])
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

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
        last_checked = int(request.args.get('last_checked', self.last_checked))
        connection = self.create_mysql_connection()
        if connection is None:
            return jsonify([])

        cursor = connection.cursor()
        query = """
            SELECT id, surname, firstname, mi FROM paymaster_notification_user
            WHERE id > %s ORDER BY id ASC
        """
        cursor.execute(query, (last_checked,))
        notifications = cursor.fetchall()
        cursor.close()
        connection.close()

        if notifications:
            self.last_checked = notifications[-1][0]

        return jsonify(notifications)

    def get_notification_count(self):
        connection = self.create_mysql_connection()
        if connection is None:
            return jsonify({'count': 0})

        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM paymaster_notification_user WHERE id > %s"
        cursor.execute(query, (self.last_checked,))
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
            query = ("SELECT CONCAT(surname, ' ', firstname, ' ', mi) AS fullname FROM paymaster_notification_user "
                     "WHERE id = %s")
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

    def start_server(self):
        self.app.run(port=5000)

    def poll_notifications(self):
        while True:
            try:
                response = requests.get(f"http://localhost:5000/notifications?last_checked={self.last_checked}")
                notifications = response.json()

                if notifications:
                    for notification in notifications:
                        self.last_checked = notification[0]

                time.sleep(5)

            except requests.RequestException as e:
                time.sleep(10)

    def run(self):
        self.poll_notifications()

    def get_last_checked(self):
        return self.last_checked