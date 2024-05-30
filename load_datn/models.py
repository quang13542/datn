from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    BigInteger,
    ForeignKey,
    Identity,
    DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from psycopg2 import connect, sql
from dotenv import dotenv_values
from metadata import (
    USERNAME,
    PASSWORD,
    DB_NAME,
    engine
)

config = dotenv_values(".env")

Base = declarative_base()

class DimCompany(Base):
    __tablename__ = 'dim_company'
    company_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='company dimension table')
    size = Column(String(100), comment='number of employees')
    name = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, size, name, inserted_date=None):
        self.size = size
        self.name = name
        self.inserted_date = inserted_date

class DimDate(Base):
    __tablename__ = 'dim_date'
    date_id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now())
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    quarter = Column(Integer)
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, date=None, day=None, month=None, year=None, quarter=None, inserted_date=None):
        self.date = date
        self.day = day
        self.month = month
        self.year = year
        self.quarter = quarter
        self.inserted_date = inserted_date

class DimJobRole(Base):
    __tablename__ = 'dim_job_role'
    job_role_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='job role dimension table')
    category = Column(String)
    name = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, category, name, inserted_date=None):
        self.category = category
        self.name = name
        self.inserted_date = inserted_date

class DimPosition(Base):
    __tablename__ = 'dim_position'
    position_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='sub dimension table')
    company_id = Column(BigInteger, ForeignKey('dim_company.company_id'), nullable=False)
    city = Column(String(100))
    detail_position = Column(String(255))
    inserted_date = Column(Date, default=datetime.now().date())
    region = Column(String(20))
    company = relationship('DimCompany')

    def __init__(self, company_id, city, detail_position, region, inserted_date=None):
        self.company_id = company_id
        self.city = city
        self.detail_position = detail_position
        self.region = region
        self.inserted_date = inserted_date

class DimSkill(Base):
    __tablename__ = 'dim_skill'
    skill_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='skill dimension table')
    category = Column(String(100))
    name = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, category, name, inserted_date=None):
        self.category = category
        self.name = name
        self.inserted_date = inserted_date

class DimSkillList(Base):
    __tablename__ = 'dim_skill_list'
    skill_job_post_id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_post_id = Column(BigInteger, ForeignKey('fact_job_post.job_post_id'), nullable=False)
    skill_id = Column(BigInteger, ForeignKey('dim_skill.skill_id'), nullable=False)
    core_skill = Column(Boolean, default=True)
    inserted_date = Column(Date, default=datetime.now().date())
    job_post = relationship('FactJobPost')
    skill = relationship('DimSkill')

    def __init__(self, job_post_id, skill_id, core_skill=True, inserted_date=None):
        self.job_post_id = job_post_id
        self.skill_id = skill_id
        self.core_skill = core_skill
        self.inserted_date = inserted_date

class DimSource(Base):
    __tablename__ = 'dim_source'
    source_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='source dimension table')
    name = Column(String(100))
    url = Column(String(255))
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, name, url, inserted_date=None):
        self.name = name
        self.url = url
        self.inserted_date = inserted_date

class FactJobPost(Base):
    __tablename__ = 'fact_job_post'
    job_post_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='job post fact table')
    company_id = Column(BigInteger, ForeignKey('dim_company.company_id'), nullable=False)
    start_recruit_date_id = Column(BigInteger, ForeignKey('dim_date.date_id'), nullable=False)
    end_recruit_date_id = Column(BigInteger, ForeignKey('dim_date.date_id'), nullable=True)
    job_role_id = Column(BigInteger, ForeignKey('dim_job_role.job_role_id'), nullable=False)
    source_id = Column(BigInteger, ForeignKey('dim_source.source_id'), nullable=False)
    salary_max = Column(BigInteger)
    salary_min = Column(BigInteger)
    years_of_experience = Column(Integer)
    job_level = Column(String(10))
    job_type = Column(String(10))
    inserted_date = Column(Date, default=datetime.now().date())
    company = relationship('DimCompany')
    start_recruit_date = relationship('DimDate', foreign_keys=[start_recruit_date_id])
    end_recruit_date = relationship('DimDate', foreign_keys=[end_recruit_date_id])
    job_role = relationship('DimJobRole')
    source = relationship('DimSource')

    def __init__(self, company_id, start_recruit_date_id, end_recruit_date_id, job_role_id, source_id, salary_max=None, salary_min=None, years_of_experience=None, job_level=None, job_type=None, inserted_date=None):
        self.company_id = company_id
        self.start_recruit_date_id = start_recruit_date_id
        self.end_recruit_date_id = end_recruit_date_id
        self.job_role_id = job_role_id
        self.source_id = source_id
        self.salary_max = salary_max
        self.salary_min = salary_min
        self.years_of_experience = years_of_experience
        self.job_level = job_level
        self.job_type = job_type
        self.inserted_date = inserted_date

def create_database_if_not_exists(dbname, user, password, host='localhost', port=5432):
    conn = connect(dbname='postgres', user=user, password=password, host=host, port=port)
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        print(f"Database {dbname} created.")
    else:
        print(f"Database {dbname} already exists.")
    
    cur.close()
    conn.close()

def create_database_structure():
    create_database_if_not_exists(DB_NAME, USERNAME, PASSWORD)

    Base.metadata.create_all(engine)
    print('Schema have been added')