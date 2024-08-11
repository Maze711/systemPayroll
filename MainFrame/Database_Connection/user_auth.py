import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MainFrame.Resources.lib import *

from MainFrame.systemFunctions import single_function_logger
from MainFrame.Database_Connection.DBConnection import create_connection


class UserAuthorization:
    @single_function_logger.log_function
    def getUserRole(self, username):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return
            cursor = connection.cursor()
            fetch_user_role_in_users_table = "SELECT user_role FROM users WHERE user_name = %s"
            cursor.execute(fetch_user_role_in_users_table, (username,))
            result = cursor.fetchone()

            return result[0]

        except Error as e:
            logging.error(f"Error fetching user role: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")


class UserAuthentication(UserAuthorization):
    def __init__(self):
        self.verifiedUsername = None

    """LOG IN USER"""
    @single_function_logger.log_function
    def logInUser(self, instance):
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

        return

    """SIGN UP USER"""
    @single_function_logger.log_function
    def signUpUser(self, instance):
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

        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return

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

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    """RESET USER PASSWORD"""
    def verifyExistingUser(self, instance):
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

    @single_function_logger.log_function
    def resetUserPassword(self, instance):
        pre_new_password = instance.txtPreNewPassword.text()
        new_password = instance.txtNewPassword.text()

        # Input Validations
        if not pre_new_password.strip() or not new_password.strip():
            QMessageBox.warning(instance, "Input Error", "Please input all fields!")
            return
        elif not self.isPasswordMatch(pre_new_password, new_password):
            QMessageBox.warning(instance, "Input Error", "Passwords do not match!")
            return

        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return

            cursor = connection.cursor()
            update_user_password_in_users_table = "UPDATE users SET user_password = %s WHERE user_name = %s"
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

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def setVerifiedUserName(self, username):
        self.verifiedUsername = username

    def getVerifiedUserName(self):
        return self.verifiedUsername


    """Validation Functions"""
    @single_function_logger.log_function
    def isUsernameNotExist(self, username):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return False

            cursor = connection.cursor()
            fetch_username_in_users_table = "SELECT user_name FROM users WHERE user_name = %s"
            cursor.execute(fetch_username_in_users_table, (username,))
            result = cursor.fetchone()

            if result:
                return False

            return True

        except Error as e:
            logging.error(f"Error fetching username: {e}")
            return False

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    @single_function_logger.log_function
    def isCorrectPassword(self, username, password):
        try:
            connection = create_connection('SYSTEM_AUTHENTICATION')
            if connection is None:
                logging.error("Error: Could not establish database connection.")
                return
            cursor = connection.cursor()
            fetch_password_in_users_table = "SELECT user_password FROM users WHERE user_name = %s"
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
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                logging.info("Database connection closed")

    def isPasswordMatch(self, pre_password, password):
        if pre_password != password:
            return False

        return True

    def isUserAlreadyLoggedIn(self, instance, isLoggedIn):
        if isLoggedIn is False:
            instance.btnLogOut.setVisible(False)
            instance.disableAllNavButtons()
            instance.mainBody.setVisible(True)
        else:
            instance.btnLogOut.setVisible(True)
            instance.mainBody.setVisible(False)

    def getGeneratedHashPassword(self, password):
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashedPassword.decode('utf-8')