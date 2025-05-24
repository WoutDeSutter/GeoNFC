import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))  # Default MySQL port
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'geonfc')  # Using geonfc as default database
    
    # API configuration
    API_URL = os.getenv('API_URL', 'http://localhost:5000')
    
    # Environment
    ENV = os.getenv('ENV', 'development')
    
    @classmethod
    def is_production(cls):
        return cls.ENV.lower() == 'production'
