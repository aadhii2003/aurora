ADMIN_LOGIN="SELECT * FROM tbl_login WHERE email = %s AND password = %s AND role = 'admin'"
user_login="SELECT * FROM tbl_login WHERE email = %s AND password = %s AND role = 'user'"
user_register = "INSERT INTO tbl_login (email, password, role) VALUES (%s, %s, %s)"