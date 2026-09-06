import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

class Config:
    # Flask application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'enterprise_procurement_secret_key_123!')
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Database configuration
    DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite') # 'sqlite' or 'mysql'
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'procurement_db')
    
    if DB_ENGINE == 'sqlite':
        # Force SQLite connection file even if DATABASE_URL in .env points to MySQL
        db_url = os.getenv('DATABASE_URL', 'sqlite:///procurement.db')
        if not db_url.startswith('sqlite:'):
            db_url = 'sqlite:///procurement.db'
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Default to MySQL
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT authentication settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_super_secret_enterprise_procurement_key_2026_secure!')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_EXPIRES_HOURS', 4)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_EXPIRES_DAYS', 7)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Pagination default
    DEFAULT_PAGE_SIZE = 10
