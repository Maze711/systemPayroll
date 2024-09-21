import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import DatabaseConnectionError
from MainFrame.Database_Connection.DBConnection import create_connection
from MainFrame.Database_Connection.user_session import UserSession


class UserAuthorization:
    def getUserRole(self, username):
        connection = None
        cursor = None

        try:
            connection = create_connection('NTP_EMP_AUTH')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            fetch_user_role_in_users_table = "SELECT user_role FROM users WHERE BINARY user_name = %s"
            cursor.execute(fetch_user_role_in_users_table, (username,))
            result = cursor.fetchone()

            return result[0]

        except Error as e:
            QMessageBox.critical(None, "Error Fetching User Role",
                                 f"An error occurred while fetching the user role: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")


class UserAuthentication(UserAuthorization):
    def __init__(self):
        self.verifiedUsername = None
        self.user_id = None
        self.user_session = UserSession()

    """LOG IN USER"""
    def logInUser(self, instance):
        try:
            username = instance.txtUsername.text()
            password = instance.txtPassword.text()

            # Input Validations
            if not username.strip() or not password.strip():
                QMessageBox.warning(instance, "Input Error", "Please input all fields!")
                return
            elif self.isUsernameNotExist(username):
                QMessageBox.warning(instance, "Username does not exist",
                                    "Username does not exist, please sign up first!")
                return
            elif not self.isCorrectPassword(username, password):
                QMessageBox.warning(instance, "Incorrect Password",
                                    "The password you entered is incorrect. Please try again!")
                return

            QMessageBox.information(instance, "Success", "Login Successful")

            self.isUserAlreadyLoggedIn(instance, True)

            # Enable navigation buttons based on the user's role
            user_role = self.getUserRole(username)
            if user_role == 'HR':
                instance.enableNavButton('btnEmployeeList')
            elif user_role == 'TimeKeeper':
                instance.enableNavButton('btnTimeKeeping')
            elif user_role in ['Accountant', 'Pay Master 1', 'Pay Master 2', 'Pay Master 3']:
                instance.enableNavButton('btnPayRoll')

            self.fetchLoggedInUserInfo(username) # Retrieves all user info to store in session
            instance.btnLogin.setEnabled(False)  # Disable the btnLogin button
            return
        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(instance, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

    """SIGN UP USER"""
    def signUpUser(self, instance):
        connection = None
        cursor = None

        try:
            username = instance.txtUsernameSignUp.text()
            pre_password = instance.txtPrePassword.text()
            password = instance.txtSignUpPassword.text()

            # Input Validations
            if not username.strip() or not pre_password.strip() or not password.strip():
                QMessageBox.warning(instance, "Input Error", "Please input all fields!")
                return
            elif not self.isUsernameNotExist(username):
                QMessageBox.warning(instance, "Input Error", "Username already exist!")
                return
            elif not self.isPasswordMatch(pre_password, password):
                QMessageBox.warning(instance, "Input Error", "Passwords do not match!")
                return

            connection = create_connection('NTP_EMP_AUTH')

            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            insert_user_in_users_table = "INSERT INTO users (user_name, user_password) VALUES (%s, %s)"
            hashedPassword = self.getGeneratedHashPassword(password)
            values = (username, hashedPassword)

            cursor.execute(insert_user_in_users_table, values)
            connection.commit()

            QMessageBox.information(instance, "Success", "Your account has been successfully created!")
            instance.switchPageAndResetInputs(instance.loginPage)
            return

        except Error as e:
            logging.error(f"Error Signing Up/Inserting User: {e}")
            return
        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(instance, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")
            return
        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")

    """RESET USER PASSWORD"""
    def verifyExistingUser(self, instance):
        try:
            username = instance.txtUsernameForgot.text()

            # Input Validations
            if not username.strip():
                QMessageBox.warning(instance, "Input Error", "Please enter your username!")
                return
            elif self.isUsernameNotExist(username):
                QMessageBox.warning(instance, "Input Error", "Username does not exist!")
                return

            QMessageBox.information(instance, "Success", "Your account has been verfied!")
            instance.switchPageAndResetInputs(instance.resetPassPage)
            self.setVerifiedUserName(username)

        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(instance, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")

    def resetUserPassword(self, instance):
        connection = None
        cursor = None

        try:
            pre_new_password = instance.txtPreNewPassword.text()
            new_password = instance.txtNewPassword.text()

            # Input Validations
            if not pre_new_password.strip() or not new_password.strip():
                QMessageBox.warning(instance, "Input Error", "Please input all fields!")
                return
            elif not self.isPasswordMatch(pre_new_password, new_password):
                QMessageBox.warning(instance, "Input Error", "Passwords do not match!")
                return

            connection = create_connection('NTP_EMP_AUTH')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            update_user_password_in_users_table = "UPDATE users SET user_password = %s WHERE BINARY user_name = %s"
            username = self.getVerifiedUserName()
            hashedPassword = self.getGeneratedHashPassword(new_password)
            values = (hashedPassword, username)

            cursor.execute(update_user_password_in_users_table, values)
            connection.commit()

            QMessageBox.information(instance, "Success", "Your password has been reset successfully!")
            instance.switchPageAndResetInputs(instance.loginPage)
            return

        except Error as e:
            logging.error(f"Error Resetting user password: {e}")
            return
        except DatabaseConnectionError as dce:
            logging.error(f"Database Connection Error: {dce}")
            QMessageBox.critical(instance, "Database Connection Error",
                                 "An unexpected disconnection has occurred. Please check your network connection or "
                                 "contact the system administrator.")
        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")

    def setVerifiedUserName(self, username):
        self.verifiedUsername = username

    def getVerifiedUserName(self):
        return self.verifiedUsername


    """Validation Functions"""
    def isUsernameNotExist(self, username):
        connection = None
        cursor = None

        try:
            connection = create_connection('NTP_EMP_AUTH')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            fetch_username_in_users_table = "SELECT user_name FROM users WHERE BINARY user_name = %s"
            cursor.execute(fetch_username_in_users_table, (username,))
            result = cursor.fetchone()

            if result:
                return False

            return True

        except Error as e:
            logging.error(f"Error fetching username: {e}")
            return False

        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")

    def isCorrectPassword(self, username, password):
        connection = None
        cursor = None

        try:
            connection = create_connection('NTP_EMP_AUTH')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            fetch_password_in_users_table = "SELECT user_password FROM users WHERE BINARY user_name = %s"
            cursor.execute(fetch_password_in_users_table, (username, ))
            result = cursor.fetchone()

            # Fetch and encoded stored hashed password
            stored_hashed_password = result[0].encode('utf-8')

            # Checks the inputted password and the hash password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                return True
            else:
                return False

        except Error as e:
            logging.error(f"Error fetching user password: {e}")

        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")

    def isPasswordMatch(self, pre_password, password):
        if pre_password != password:
            return False

        return True

    def isUserAlreadyLoggedIn(self, instance, isLoggedIn):
        if isLoggedIn is False:
            instance.btnLogOut.setVisible(False)
            instance.btnReportBug.setVisible(False)
            instance.btnNotification.setVisible(False)
            instance.disableAllNavButtons()
            instance.mainBody.setVisible(True)
        else:
            instance.btnLogOut.setVisible(True)
            instance.btnReportBug.setVisible(True)
            instance.btnNotification.setVisible(True)
            instance.mainBody.setVisible(False)

    def getGeneratedHashPassword(self, password):
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashedPassword.decode('utf-8')

    def fetchLoggedInUserInfo(self, user_name):
        connection = None
        cursor = None

        try:
            connection = create_connection('NTP_EMP_AUTH')
            if connection is None:
                raise DatabaseConnectionError("Error: Could not establish database connection.")

            cursor = connection.cursor()
            fetch_user_id_in_users_table = """
            SELECT user_id, user_name, user_email, user_email_password, user_role FROM users WHERE BINARY user_name = %s
            """
            cursor.execute(fetch_user_id_in_users_table, (user_name,))
            result = cursor.fetchone()

            if result:
                # Set values to session
                self.user_session["user_id"] = result[0]
                self.user_session["user_name"] = result[1]
                self.user_session["user_email"] = result[2]
                self.user_session["user_email_password"] = result[3]
                self.user_session["user_role"] = result[4]
                return

        except Error as e:
            logging.error(f"Error fetching user_id: {e}")
            return

        finally:
            if cursor is not None:
                cursor.close()
            # Ensure the connection is closed if it was established
            if connection is not None and connection.is_connected():
                connection.close()
                logging.info("Database connection closed")