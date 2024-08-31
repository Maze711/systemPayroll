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
            'database': 'SYSTEM_NOTIFICATION',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        self.last_checked = 0

        self.app.add_url_rule('/notifications', 'get_notifications', self.get_notifications, methods=['GET'])

    def create_mysql_connection(self):
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            if connection.is_connected():
                return connection
            else:
                raise Exception("Failed to connect to MySQL database.")
        except mysql.connector.Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    def get_notifications(self):
        last_checked = int(request.args.get('last_checked', self.last_checked))
        connection = self.create_mysql_connection()
        if connection is None:
            return jsonify([])

        cursor = connection.cursor()
        query = """
            SELECT id, message FROM employee_notifications
            WHERE id > %s ORDER BY id ASC
        """
        cursor.execute(query, (last_checked,))
        notifications = cursor.fetchall()
        cursor.close()
        connection.close()

        if notifications:
            self.last_checked = notifications[-1][0]

        return jsonify(notifications)

    def start_server(self):
        self.app.run(port=5000)

    def poll_notifications(self):
        while True:
            try:
                response = requests.get(f"http://localhost:5000/notifications?last_checked={self.last_checked}")
                notifications = response.json()

                if notifications:
                    for notification in notifications:
                        print(f"New Notification: ID={notification[0]}, Message={notification[1]}")
                        self.last_checked = notification[0]
                else:
                    print("No new notifications.")

                time.sleep(5)

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(10)

    def run(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True
        server_thread.start()

        self.poll_notifications()

# Still using this if statement to run it to console since it's still not integrated in the application itself.
if __name__ == "__main__":
    service = NotificationService()
    service.run()
