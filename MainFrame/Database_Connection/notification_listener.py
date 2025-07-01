from flask import Flask, request, jsonify
from MainFrame.Resources.lib import *
import threading
import queue
import time
from contextlib import contextmanager
import logging


class NotificationService:
    def __init__(self):
        # Use lazy initialization for Flask app
        self.app = None
        self.mysql_config = {
            'host': 'localhost',
            #'host': '192.168.68.51',
            'database': 'NTP_ACCOUNTANT_NOTIFICATION',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        self.last_checked = 0
        self.polling = True
        self.server = None
        self.server_thread = None
        self.poll_thread = None
        
        # Connection pool management
        self.connection_pool = queue.Queue(maxsize=5)
        self.pool_lock = threading.Lock()
        self._initialize_connection_pool()
        
        # Event for graceful shutdown
        self.shutdown_event = threading.Event()
        
        # Cache for performance
        self._notification_cache = []
        self._cache_timestamp = 0
        self._cache_duration = 2  # seconds

    def _initialize_connection_pool(self):
        """Initialize database connection pool"""
        try:
            for _ in range(3):  # Start with 3 connections
                conn = self._create_connection()
                if conn:
                    self.connection_pool.put(conn)
        except Exception as e:
            logging.error(f"Failed to initialize connection pool: {e}")

    def _create_connection(self):
        """Create a single database connection"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            if connection.is_connected():
                return connection
            else:
                raise Exception("Failed to connect to MySQL database.")
        except mysql.connector.Error as e:
            logging.error(f"Database connection error: {e}")
            return None

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with pooling"""
        connection = None
        try:
            # Try to get connection from pool
            try:
                connection = self.connection_pool.get_nowait()
                # Test if connection is still valid
                if not connection.is_connected():
                    connection.close()
                    connection = self._create_connection()
            except queue.Empty:
                # Pool is empty, create new connection
                connection = self._create_connection()
            
            if connection is None:
                raise Exception("Could not establish database connection")
                
            yield connection
            
        except Exception as e:
            logging.error(f"Database operation failed: {e}")
            if connection:
                connection.close()
            connection = None
            raise
        finally:
            # Return connection to pool if still valid
            if connection and connection.is_connected():
                try:
                    self.connection_pool.put_nowait(connection)
                except queue.Full:
                    # Pool is full, close this connection
                    connection.close()
            elif connection:
                connection.close()

    def _setup_flask_app(self):
        """Lazy initialization of Flask app"""
        if self.app is None:
            self.app = Flask(__name__)
            self.app.logger.setLevel(logging.WARNING)  # Reduce Flask logging
            
            # Disable Flask startup messages
            import logging as flask_logging
            flask_logging.getLogger('werkzeug').setLevel(flask_logging.WARNING)
            
            self.app.add_url_rule('/notifications', 'get_notifications', self.get_notifications, methods=['GET'])
            self.app.add_url_rule('/notification_count', 'get_notification_count', self.get_notification_count, methods=['GET'])
            self.app.add_url_rule('/employee_details/<int:employee_id>', 'get_employee_details', self.get_employee_details, methods=['GET'])

    def create_mysql_connection(self):
        """Legacy method for backward compatibility"""
        return self._create_connection()

    def get_notifications(self):
        """Get notifications with caching for better performance"""
        last_checked = request.args.get('last_checked', self.last_checked)
        try:
            last_checked = int(last_checked)
        except ValueError:
            last_checked = self.last_checked

        # Check cache first
        current_time = time.time()
        if (current_time - self._cache_timestamp < self._cache_duration and 
            self._notification_cache):
            return jsonify(self._notification_cache)

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                query = """
                    SELECT notif_count, surname, firstname, mi FROM paymaster_notification_user
                    WHERE notif_count > %s ORDER BY notif_count ASC
                """
                cursor.execute(query, (last_checked,))
                notifications = cursor.fetchall()

                # Check if last_checked value exists in the current data
                if notifications:
                    self.last_checked = notifications[-1][0]
                else:
                    # If no notifications found, check if last_checked still exists
                    query_check = "SELECT COUNT(*) FROM paymaster_notification_user WHERE notif_count = %s"
                    cursor.execute(query_check, (last_checked,))
                    if cursor.fetchone()[0] == 0:
                        # Reset to maximum existing notif_count
                        query_max = "SELECT COALESCE(MAX(notif_count), 0) FROM paymaster_notification_user"
                        cursor.execute(query_max)
                        max_notif_count = cursor.fetchone()[0]
                        self.last_checked = max_notif_count

                cursor.close()

                # Update cache
                self._notification_cache = notifications
                self._cache_timestamp = current_time

                return jsonify(notifications)
                
        except Exception as e:
            logging.error(f"Error getting notifications: {e}")
            return jsonify([])

    def get_notification_count(self):
        """Get total notification count with connection pooling"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                query = "SELECT COUNT(*) FROM paymaster_notification_user"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                cursor.close()
                return jsonify({'count': count})
        except Exception as e:
            logging.error(f"Error getting notification count: {e}")
            return jsonify({'count': 0})

    def get_total_notifications_count(self):
        """Get total notifications count (non-Flask method)"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                query = "SELECT COUNT(*) FROM paymaster_notification_user"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                cursor.close()
                return count
        except Exception as e:
            logging.error(f"Error getting total notifications count: {e}")
            return 0

    def get_employee_details(self, employee_id):
        """Get employee details with connection pooling"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                query = ("SELECT empl_id, CONCAT(surname, ' ', firstname, ' ', mi) AS fullname "
                         "FROM paymaster_notification_user WHERE notif_count = %s")
                cursor.execute(query, (employee_id,))
                details = cursor.fetchone()
                cursor.close()
                return details if details else {}
        except Exception as e:
            logging.error(f"Error getting employee details: {e}")
            return {}

    def remove_employee_notification(self, empl_id):
        """Remove employee notification with connection pooling"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                query = "DELETE FROM paymaster_notification_user WHERE empl_id = %s"
                cursor.execute(query, (empl_id,))
                connection.commit()
                cursor.close()
                # Clear cache after modification
                self._cache_timestamp = 0
        except Exception as e:
            logging.error(f"Error removing employee notification: {e}")

    def reorder_notifications(self):
        """Reorder notifications with connection pooling"""
        try:
            with self.get_connection() as connection:
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
                cursor.close()
                
                # Clear cache after modification
                self._cache_timestamp = 0

        except mysql.connector.Error as e:
            logging.error(f"Error reordering notifications: {e}")

        # Reset the last_checked value to ensure all notifications are re-fetched
        self.last_checked = 0

    def start_server(self):
        """Start Flask server asynchronously with better error handling"""
        try:
            if not self.app:
                self._setup_flask_app()
            
            # Start server in background with minimal output
            self.app.run(port=5000, threaded=True, debug=False, use_reloader=False)
        except Exception as e:
            logging.error(f"Error starting Flask server: {e}")

    def start_service_async(self):
        """Start notification service asynchronously for faster startup"""
        if not self.server_thread or not self.server_thread.is_alive():
            self._setup_flask_app()
            self.server_thread = threading.Thread(target=self.start_server, daemon=True)
            self.server_thread.start()
            
        if not self.poll_thread or not self.poll_thread.is_alive():
            self.poll_thread = threading.Thread(target=self.poll_notifications_direct, daemon=True)
            self.poll_thread.start()

    def stop(self):
        """Improved stop method with faster shutdown"""
        logging.info("Stopping NotificationService...")
        
        # Set shutdown flag
        self.polling = False
        self.shutdown_event.set()
        
        # Close all connections in pool
        self._cleanup_connection_pool()
        
        logging.info("NotificationService stopped.")

    def _cleanup_connection_pool(self):
        """Clean up all connections in the pool"""
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                if conn and conn.is_connected():
                    conn.close()
            except queue.Empty:
                break
            except Exception as e:
                logging.error(f"Error closing connection: {e}")

    def poll_notifications_direct(self):
        """Direct database polling instead of HTTP requests for better performance"""
        while self.polling and not self.shutdown_event.is_set():
            try:
                # Check for new notifications directly from database
                with self.get_connection() as connection:
                    cursor = connection.cursor()
                    query = """
                        SELECT notif_count, surname, firstname, mi FROM paymaster_notification_user
                        WHERE notif_count > %s ORDER BY notif_count ASC LIMIT 10
                    """
                    cursor.execute(query, (self.last_checked,))
                    notifications = cursor.fetchall()
                    
                    if notifications:
                        # Update last_checked to the newest notification
                        self.last_checked = notifications[-1][0]
                        logging.info(f"Found {len(notifications)} new notifications")
                    
                    cursor.close()
                
                # Wait before next poll, but check shutdown event
                if self.shutdown_event.wait(timeout=5):  # 5 second polling interval
                    break
                    
            except Exception as e:
                logging.error(f"Error in direct polling: {e}")
                if self.shutdown_event.wait(timeout=10):  # Wait longer on error
                    break

    def poll_notifications(self):
        """Legacy HTTP polling method - kept for backward compatibility"""
        while self.polling and not self.shutdown_event.is_set():
            try:
                response = requests.get(
                    f"http://localhost:5000/notifications?last_checked={self.last_checked}",
                    timeout=5
                )
                notifications = response.json()

                if notifications:
                    self.last_checked = notifications[-1][0]

            except requests.RequestException as e:
                logging.error(f"HTTP polling error: {e}")
            
            # Use shutdown event for better responsiveness
            if self.shutdown_event.wait(timeout=10):
                break

    def get_last_checked(self):
        return self.last_checked

    def get_service_status(self):
        """Get service status for monitoring"""
        return {
            'polling': self.polling,
            'last_checked': self.last_checked,
            'pool_size': self.connection_pool.qsize(),
            'cache_valid': (time.time() - self._cache_timestamp) < self._cache_duration,
            'server_running': self.server_thread and self.server_thread.is_alive() if hasattr(self, 'server_thread') else False,
            'poll_running': self.poll_thread and self.poll_thread.is_alive() if hasattr(self, 'poll_thread') else False
        }

    def health_check(self):
        """Perform a quick health check on the service"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return False

    def restart_if_needed(self):
        """Restart service components if they've failed"""
        try:
            if not self.health_check():
                logging.warning("Health check failed, reinitializing connection pool...")
                self._cleanup_connection_pool()
                self._initialize_connection_pool()
            
            if hasattr(self, 'server_thread') and not self.server_thread.is_alive():
                logging.warning("Server thread died, restarting...")
                self.server_thread = threading.Thread(target=self.start_server, daemon=True)
                self.server_thread.start()
                
            if hasattr(self, 'poll_thread') and not self.poll_thread.is_alive():
                logging.warning("Poll thread died, restarting...")
                self.poll_thread = threading.Thread(target=self.poll_notifications_direct, daemon=True)
                self.poll_thread.start()
                
        except Exception as e:
            logging.error(f"Error in restart_if_needed: {e}")
