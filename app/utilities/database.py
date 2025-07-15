import os
import pymysql

class Database(object):
    def __init__(self, config=None, username=None, password=None, host=None, port=None, db_name=None):
        # Use environment variables as defaults
        if db_name is None:
            db_name = os.getenv('MYSQL_DATABASE')
        if username is None:
            username = os.getenv('MYSQL_USERNAME')
        if password is None:
            password = os.getenv('MYSQL_PASSWORD')
        if host is None:
            host = os.getenv('MYSQL_HOST')
        if port is None:
            port = os.getenv('MYSQL_PORT') or '3306'

        self.params_dict = {
            "host": host,
            "database": db_name,
            "user": username,
            "password": password,
            "port": int(port),
            "charset": 'utf8mb4',
            "cursorclass": pymysql.cursors.DictCursor
        }


    def connect(self):
        """ Connect to the MySQL database server """
        conn = None
        try:
            conn = pymysql.connect(**self.params_dict)
        except pymysql.Error as error:
            raise error
        return conn

    def single_insert(self, insert_req, params=None):
        """ Execute a single INSERT request """
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(insert_req, params)
            conn.commit()
        except pymysql.Error as error:
            if conn is not None:
                conn.rollback()
            return error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def execute(self, req_query, params=None):
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(req_query, params)
            conn.commit()
            print(f"Commit successful for query: {req_query} with params: {params}")  # Debugging
        except pymysql.Error as error:
            if conn is not None:
                conn.rollback()
                print(f"Rollback due to error: {error} for query: {req_query} with params: {params}")  # Debugging
            return error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def executeAndReturnId(self, req_query, params=None):
        """ Execute a single request and return the inserted ID """
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(req_query, params)
            dt = cursor.lastrowid
            conn.commit()
            return dt
        except pymysql.Error as error:
            if conn is not None:
                conn.rollback()
            return error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def fetchone(self, get_req, params=None):
        """ Fetch a single row """
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(get_req, params)
            data = cursor.fetchone()
            return data
        except pymysql.Error as error:
            return error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def fetchall(self, get_req, params=None):
        """ Fetch all rows """
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(get_req, params)
            data = cursor.fetchall()
            return data
        except pymysql.Error as error:
            return error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()