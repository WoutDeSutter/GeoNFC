import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'geonfc')

[connector_python]
user = root
host = 127.0.0.1
port = 3306
password = root
database = mendeljev

[application_config]
driver = 'SQL Server'
