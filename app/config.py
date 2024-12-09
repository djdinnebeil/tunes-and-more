import os

allowed_extensions = {'mp3'}

environment = os.getenv('FLASK_ENV')
SCHEMA = os.environ.get('SCHEMA')

BUCKET_NAME = os.environ.get('S3_BUCKET')
S3_REGION = os.environ.get('S3_REGION')
S3_LOCATION = f'https://{BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com'
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET")

if environment == 'production' or environment == 'aws-testing':
    music_server_url = S3_LOCATION
else:
    music_server_url = 'http://localhost:5000'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    SQLALCHEMY_ECHO = True
