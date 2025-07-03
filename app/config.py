import os
from .utilities.database import Database

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'aurora_dev_key')
    DEBUG = os.getenv('ENV') != 'Production'
    IMG_PATH = 'https://example.com/uploads/products/'

  
    MYSQL_DB = os.getenv('MYSQL_DATABASE','db_aurora')
    MYSQL_USER = os.getenv('MYSQL_USERNAME','root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD','')
    MYSQL_HOST = os.getenv('MYSQL_HOST','localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT') or '3306'

    db = Database(
        db_name=MYSQL_DB,
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT
    )
