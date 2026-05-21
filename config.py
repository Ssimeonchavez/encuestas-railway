import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Railway provee MYSQL_URL automáticamente cuando agregas el servicio MySQL
    # Formato: mysql://user:password@host:port/database
    database_url = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL')
    
    if database_url:
        if database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        elif database_url.startswith('mysql+'):
            pass  # Ya tiene el formato correcto
        else:
            # Si se proporciona otra URL (ej. sqlite:///) la respetamos (útil para pruebas locales)
            pass
    else:
        # Fallback para desarrollo local
        database_url = 'mysql+pymysql://root:password@localhost:3306/encuestas'
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False