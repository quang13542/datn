import os
from dotenv import dotenv_values
from metadata import URI
config = dotenv_values(".env")

SECRET_KEY = config['SUPERSET_SECRET_KEY']
SQLALCHEMY_DATABASE_URI = URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
