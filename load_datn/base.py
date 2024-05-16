from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values

config = dotenv_values(".env")

engine = create_engine(f'postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/JobPostManagement')
Session = sessionmaker(bind=engine)

Base = declarative_base()