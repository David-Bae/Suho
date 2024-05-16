import os

# DB
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# CoolSMS API Key
COOLSMS_KEY = os.getenv('COOLSMS_KEY')
COOLSMS_SECRET = os.getenv('COOLSMS_SECRET')


# JWT
JWT_SECRET = os.getenv('JWT_SECRET')