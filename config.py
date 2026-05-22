import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Railway provee variables individuales de MySQL: MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
    # O una URL completa en MYSQL_URL
    database_url = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL')
    
    if database_url:
        # Si hay URL, convertirla al formato de pymysql
        if database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        elif database_url.startswith('mysql+'):
            pass  # Ya tiene el formato correcto
    else:
        # Intentar construir desde variables individuales de Railway
        mysql_host = os.getenv('MYSQL_HOST')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')
        mysql_db = os.getenv('MYSQL_DB')
        
        if mysql_host and mysql_user and mysql_db:
            # Construir URL desde variables individuales
            database_url = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}'
        else:
            # Fallback para desarrollo local
            database_url = 'mysql+pymysql://root:password@localhost:3306/encuestas'
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
