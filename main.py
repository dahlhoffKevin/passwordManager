from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTime, QDate, QTimer
from configparser import ConfigParser
from cryptography.fernet import Fernet
import mysql.connector
import sys
import random
import clipboard

# Encrypt = Verschlüsseln
# Decrypt = Verschlüsselung aufheben

class Settings:
    config = ConfigParser()
    config.read('config.ini')
    login_ui = config['DEFAULT']['login_ui']
    register_ui = config['DEFAULT']['register_ui']
    main_ui = config['DEFAULT']['main_ui']
    change_pwd_ui = config['DEFAULT']['change_pwd_ui']
    key = config['DEFAULT']['key']
    f_key = Fernet(key)


class MySQL:
    def __init__(self):
        self.myc = None
        self.db = None

        self.host = Settings.config['database']['host']
        self.user = Settings.config['database']['user']
        self.password = Settings.config['database']['password']
        self.database = Settings.config['database']['database']

        self.msg = QMessageBox()
    
    def connect(self):
        try:
            self.db = mysql.connector.connect(
                host = f'{self.host}',
                user = f'{self.user}',
                password = f'{self.password}',
                database = f'{self.database}'
            )
            self.myc = self.db.cursor()
        except:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('An error occurred!\nPlease conntact an administrator\nError code: 408')
            self.msg.setWindowTitle('Login Error')
            self.msg.show()
    
    def terminate_connection(self):
        self.db.close()
    
    def reopen_connection(self):
        self.connect()


class LoginUi(QtWidgets.QMainWindow):
    def __init__(self):
        super(LoginUi, self).__init__()
        uic.loadUi(Settings.login_ui, self)

        self.msg = QMessageBox()

        self.button_login.clicked.connect(self.login)
        self.button_register.clicked.connect(self.register)

        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.check_username = False
        self.check_password = False

        self.hide_password.stateChanged.connect(self.check_for_checkbox)
        self.hide_password.setChecked(True)

        self.user_id = None
    
    def check_for_checkbox(self):
        if self.hide_password.isChecked():
            self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        else:
            self.input_password.setEchoMode(QtWidgets.QLineEdit.Normal)

    def decrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        encrypted_string = f.decrypt(encoded_string)
        return str(encrypted_string)[2:-1]
    
    def login(self):
        sql.myc.execute('SELECT username FROM users')
        row_data_username = sql.myc.fetchall()
        found_data_username = []
        
        username = self.input_username.text()
        password = self.input_password.text()

        if username == '' and password == '':
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('All fields must been filled in!')
            self.msg.setWindowTitle('Login Error')
            self.msg.show()

        for i in row_data_username:
            found_data_username += i         

        if username not in found_data_username:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("This username doesn't exists!")
            self.msg.setWindowTitle('Login Error')
            self.msg.show()
        else:
            self.check_username = True

        sql.myc.execute(f"SELECT password FROM users WHERE username='{username}'")
        row_data_password = sql.myc.fetchall()
        found_data_password = []

        for i in row_data_password:
            found_data_password += i
        
        for i in found_data_password:
            i = self.decrypt_str(i)
            if password != i:
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText("Wrong password. Please try again!")
                self.msg.setWindowTitle('Login Error')
                self.msg.show()
            else:
                self.check_password = True

        sql.myc.execute(f"SELECT user_id FROM users WHERE username='{username}'")
        row_data_user_id = sql.myc.fetchall()
        found_data_user_id = []

        for i in row_data_user_id:
            found_data_user_id += i
        
        if self.check_password and self.check_username:
            self.user_id = found_data_user_id[0]
            self.cams = MainUI(username, self.user_id)
            self.cams.show()
            username = self.input_username.setText('')
            password = self.input_password.setText('')
            sql.terminate_connection()
            sql.reopen_connection()
            self.close()
    
    def register(self):
        self.cams = RegisterUI()
        self.cams.show()
        self.close()


class RegisterUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(RegisterUI, self).__init__()
        uic.loadUi(Settings.register_ui, self)

        self.button_exit.clicked.connect(self.exit)
        self.button_register.clicked.connect(self.register)

        self.hide_password.stateChanged.connect(self.check_for_checkbox)
        self.hide_password.setChecked(True)

        self.msg = QMessageBox()

        self.reg_continue = True
    
    def check_for_checkbox(self):
        if self.hide_password.isChecked():
            self.box_password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.box_password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        else:
            self.box_password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.box_password_confirm.setEchoMode(QtWidgets.QLineEdit.Normal)
        
    def register(self):
        username = self.box_username.text()
        password = self.box_password.text()
        password_confirm = self.box_password_confirm.text()
        email = self.box_email.text()
        name = self.box_name.text()
        lastname = self.box_lastname.text()
        user_id = self.generate_user_id()

        if username == '' or password == '' or password_confirm == '' or email == '' or name == '' or lastname == '':
            self.reg_continue = False
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('All fields must been filled in!')
            self.msg.setWindowTitle('Registration Error')
            self.msg.show()

        if password != password_confirm:
            self.reg_continue = False
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('Passwords are not equal!')
            self.msg.setWindowTitle('Registration Error')
            self.msg.show()
        
        if self.reg_continue:
            try:
                if self.check_if_email_exists(email):
                    if self.check_if_username_exists(username):
                        self.box_username.setText('')
                        self.box_password.setText('')
                        self.box_password_confirm.setText('')
                        self.box_email.setText('')
                        self.box_name.setText('')
                        self.box_lastname.setText('')

                        encrypted_pw = self.encrypt_str(password)

                        encrypted_email = self.encrypt_str(email)

                        encrypted_name = self.encrypt_str(name)

                        encrypted_lastname = self.encrypt_str(lastname)

                        current_time = QTime.currentTime()
                        current_date = QDate.currentDate()
                        reformat_time = current_time.toString('hh:mm:ss')
                        reformat_date = current_date.toString('yyyy-MM-dd')

                        sql.myc.execute('INSERT INTO users (user_id, username, password, email, name, lastname, time, date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                                        (f'{user_id}',f'{username}',f'{encrypted_pw}',f'{encrypted_email}',f'{encrypted_name}',f'{encrypted_lastname}',f'{reformat_time}',f'{reformat_date}'))
                        sql.db.commit()

                        sql.myc.execute(f"CREATE TABLE user_{user_id} (application VARCHAR(255), email VARCHAR(255), password VARCHAR(255), username VARCHAR(255))")
                        sql.db.commit()

                        self.msg.setIcon(QMessageBox.Information)
                        self.msg.setText('Successfully registerd!')
                        self.msg.setWindowTitle('Info')
                        self.msg.show()
                    else:
                        self.msg.setIcon(QMessageBox.Critical)
                        self.msg.setText('This username is already in use!')
                        self.msg.setWindowTitle('Registration Error')
                        self.msg.show()
                else:
                    self.msg.setIcon(QMessageBox.Critical)
                    self.msg.setText('This email is already in use!')
                    self.msg.setWindowTitle('Registration Error')
                    self.msg.show()

            except:
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText('An error occured\nPlease conntact an administrator\nError code: 400')
                self.msg.setWindowTitle('Registration Error')
                self.msg.show()
    
    def generate_user_id(self):
        digits = [1,2,3,4,5,6,7,8,9]
        user_id = []

        for _ in range(0, 5):
            user_id.append(random.choice(digits))
            
            user_id_list = [str(integer) for integer in user_id]
            user_id_str = "".join(user_id_list)
            user_id_int = int(user_id_str)

        return user_id_int
        
    def encrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        encrypted_string = f.encrypt(encoded_string)
        return str(encrypted_string)[2:-1]

    def decrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        decrypted_string = f.decrypt(encoded_string)
        return str(decrypted_string)[2:-1]

    def check_if_email_exists(self, email):
        sql.myc.execute('SELECT email FROM users')
        row_data = sql.myc.fetchall()
        found_data = []
        
        for i in row_data:
            found_data += i

        if found_data != []:
            for ii in found_data:
                ii = self.decrypt_str(ii)
                if email != ii:
                    return True
                else:
                    return False
        else:
            return True
    
    def check_if_username_exists(self, username):
        sql.myc.execute('SELECT username FROM users')
        row_data = sql.myc.fetchall()
        found_data = []

        for i in row_data:
            found_data += i
        
        if found_data != []:
            for ii in found_data:
                if not ii == username:
                    return True
                else:
                    return False
        else:
            return True

    def exit(self):
        self.cams = LoginUi()
        self.cams.show()
        self.close()


class Change_Password(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(Change_Password, self).__init__()
        uic.loadUi(Settings.change_pwd_ui, self)

        self.u_id = user_id

    def encrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        encrypted_string = f.encrypt(encoded_string)
        return str(encrypted_string)[2:-1]

    def decrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        decrypted_string = f.decrypt(encoded_string)
        return str(decrypted_string)[2:-1]
        
    def check_password(self):
        new_password = self.box_pwd.text()
        con_password = self.box_con_pwd.text()
        old_password = self.box_old_pwd.text()


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, username, user_id):
        super(MainUI, self).__init__()
        uic.loadUi(Settings.main_ui, self)

        self.setup_ui()

        self.username = username
        self.user_id = user_id

        self.changeTimeDate()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.changeTimeDate)
        self.timer.start(1000)

        self.msg = QMessageBox()

        self.all_items = True

        self.show_version()

        self.app = None
        self.email = None
        self.password = None
        self.username = None
    
    def setup_ui(self):
        self.hide_password.stateChanged.connect(self.check_box_add_pwd)
        self.hide_password.setChecked(True)

        self.button_add_password.clicked.connect(self.add_password)

        self.btn_page_1.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_account))

        self.btn_page_2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_passwords))

        self.btn_page_3.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_settings))

        self.btn_page_4.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_info))

        self.btn_logout.clicked.connect(self.logout)

        self.btn_start_search.clicked.connect(self.search_for_password)

        self.btn_clear_search.clicked.connect(self.clear_search)

        self.btn_copy_password.clicked.connect(self.copy_password)
    
    def encrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        encrypted_string = f.encrypt(encoded_string)
        return str(encrypted_string)[2:-1]

    def decrypt_str(self, s):
        key = Settings.key
        f = Settings.f_key
        encoded_string = s.encode()
        decrypted_string = f.decrypt(encoded_string)
        return str(decrypted_string)[2:-1]
    
    def show_version(self):
        sql.myc.execute('SELECT version FROM infos')
        row_data = sql.myc.fetchall()
        found_data = []

        for i in row_data:
            found_data += i
        
        self.version_input.setText(f'{found_data[0]}')
    
    def logout(self):
        self.cams = LoginUi()
        self.cams.show()
        self.close()
    
    def check_box_add_pwd(self):
        if self.hide_password.isChecked():
            self.box_password.setEchoMode(QtWidgets.QLineEdit.Password)
        else:
            self.box_password.setEchoMode(QtWidgets.QLineEdit.Normal)

    def changeTimeDate(self):
        self.current_time = QTime.currentTime()
        self.current_date = QDate.currentDate()

        label_time = self.current_time.toString('hh:mm:ss')
        label_date = self.current_date.toString('dd.MM.yyyy')

        self.time_stemp.setText(label_time)
        self.date_stemp.setText(label_date)

    def add_password(self):
        app = self.box_app.text()
        email = self.box_email.text()
        password = self.box_password.text()
        username = self.box_username.text()

        encrypted_password = self.encrypt_str(password)

        if app == '' or email == '' or password == '':
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('All necessary fields musst been filled in!')
            self.msg.setWindowTitle('Error')
            self.msg.show()
            self.all_items = False
        
        if self.all_items:
            encrypt_password = self.encrypt_str(password)
            
            try:
                sql.myc.execute(f"INSERT INTO user_{self.user_id} (application, email, password, username) VALUES ('{app}','{email}','{encrypted_password}','{username}')")
                sql.db.commit()

                self.box_app.setText('')
                self.box_email.setText('')
                self.box_password.setText('')
                self.box_username.setText('')

                self.msg.setIcon(QMessageBox.Information)
                self.msg.setText('Password successfully added!')
                self.msg.setWindowTitle('Info')
                self.msg.show()
            except:
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText('An error occured\nPlease conntact an administrator\nError code: 40')
                self.msg.setWindowTitle('Error')
                self.msg.show()
    
    def search_for_password(self):
        app_search = self.box_app_search.text()
        email_search = self.box_email_search.text()
        username_search = self.box_username_search.text()

        search_continue = True

        if app_search == '' or email_search == '':
            search_continue = False
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('All necessary fields musst been filled in!')
            self.msg.setWindowTitle('Error')
            self.msg.show()
        
        if search_continue:
            sql.myc.execute(f"SELECT application, email, password, username FROM user_{self.user_id} WHERE email='{email_search}' AND application='{app_search}'")
            row_data = sql.myc.fetchall()
            found_data = []

            for i in row_data:
                found_data += i

            if not found_data:
                self.label_results.setText('No Password found! Please try again!')
                self.label_app.setText('Application / Website:')
                self.label_email.setText('E-Mail:')
                self.label_password.setText('Password:')
                self.label_username.setText('Username:')
            else:
                self.label_results.setText('')

                self.app = found_data[0]
                self.email = found_data[1]
                self.password = self.decrypt_str(found_data[2])
                self.username = found_data[3]

                self.label_app.setText(f'Application / Website: {self.app}')
                self.label_email.setText(f'E-Mail: {self.email}')
                self.label_password.setText(f'Password: {self.password}')
                self.label_username.setText(f'Username: {self.username}')

    def clear_search(self):
        self.label_results.setText('')
        self.box_app_search.setText('')
        self.box_email_search.setText('')
        self.box_username_search.setText('')

        self.label_app.setText('Application / Website:')
        self.label_email.setText('E-Mail:')
        self.label_password.setText('Password:')
        self.label_username.setText('Username:')

    def copy_password(self):
        if self.password is not None:
            self.label_results.setText('')
            self.box_app_search.setText('')
            self.box_email_search.setText('')
            self.box_username_search.setText('')

            self.label_app.setText('Application / Website:')
            self.label_email.setText('E-Mail:')
            self.label_password.setText('Password:')
            self.label_username.setText('Username:')

            clipboard.copy(self.password)

            self.msg.setIcon(QMessageBox.Information)
            self.msg.setText('Password successfully copied!')
            self.msg.setWindowTitle('Info')
            self.msg.show()
        else:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText('You have to search for a password first!')
            self.msg.setWindowTitle('Error')
            self.msg.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: sql.terminate_connection())
    login = LoginUi()
    login.show()

    sql = MySQL()
    sql.connect()

    app.exec_()