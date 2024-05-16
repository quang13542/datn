from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, BigInteger, ForeignKey, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

Base = declarative_base()

class DimCompany(Base):
    __tablename__ = 'Dim_Company'
    company_id = Column(BigInteger, primary_key=True, autoincrement=True)
    size = Column(String(100), comment='number of employees')
    name = Column(String(100), nullable=False)
    inserted_date = Column(Date, default=datetime.now().date(), comment='company dimension table')

    def __init__(self, size, name, inserted_date=None):
        self.size = size
        self.name = name
        self.inserted_date = inserted_date

class DimDate(Base):
    __tablename__ = 'Dim_Date'
    date_id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.now().date())
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    quarter = Column(Integer, nullable=False)
    inserted_date = Column(Date, default=datetime.now().date())

    def __init__(self, date=None, day=None, month=None, year=None, quarter=None, inserted_date=None):
        self.date = date
        self.day = day
        self.month = month
        self.year = year
        self.quarter = quarter
        self.inserted_date = inserted_date

class DimJobRole(Base):
    __tablename__ = 'Dim_Job_Role'
    job_role_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    name = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date(), comment='job role dimension table')

    def __init__(self, category, name=None, inserted_date=None):
        self.category = category
        self.name = name
        self.inserted_date = inserted_date

class DimPosition(Base):
    __tablename__ = 'Dim_Position'
    position_id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('Dim_Company.company_id'), nullable=False)
    city = Column(String(100))
    detail_position = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date(), comment='sub dimension table')

    def __init__(self, company_id, city=None, detail_position=None, inserted_date=None):
        self.company_id = company_id
        self.city = city
        self.detail_position = detail_position
        self.inserted_date = inserted_date

class DimSkill(Base):
    __tablename__ = 'Dim_Skill'
    skill_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    name = Column(String(100))
    inserted_date = Column(Date, default=datetime.now().date(), comment='skill dimension table')

    def __init__(self, category, name=None, inserted_date=None):
        self.category = category
        self.name = name
        self.inserted_date = inserted_date

class DimSkillList(Base):
    __tablename__ = 'Dim_Skill_List'
    skill_job_post_id = Column(BigInteger, primary_key=True)
    job_post_id = Column(BigInteger, ForeignKey('Fact_Job_Post.job_post_id'), nullable=False)
    skill_id = Column(BigInteger, ForeignKey('Dim_Skill.skill_id'), nullable=False)
    core_skill = Column(Boolean, default=True)
    inserted_date = Column(Date, default=datetime.now().date(), comment='skill list dimension table')

    def __init__(self, skill_job_post_id, job_post_id, skill_id, core_skill=True, inserted_date=None):
        self.skill_job_post_id = skill_job_post_id
        self.job_post_id = job_post_id
        self.skill_id = skill_id
        self.core_skill = core_skill
        self.inserted_date = inserted_date

class DimSource(Base):
    __tablename__ = 'Dim_Source'
    source_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100))
    url = Column(String(255))
    inserted_date = Column(Date, default=datetime.now().date(), comment='source dimension table')

    def __init__(self, name=None, url=None, inserted_date=None):
        self.name = name
        self.url = url
        self.inserted_date = inserted_date

class FactJobPost(Base):
    __tablename__ = 'Fact_Job_Post'
    job_post_id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('Dim_Company.company_id'), nullable=False)
    start_recruit_date_id = Column(BigInteger, ForeignKey('Dim_Date.date_id'), nullable=False)
    end_recruit_date_id = Column(BigInteger, ForeignKey('Dim_Date.date_id'), nullable=False)
    job_role_id = Column(BigInteger, ForeignKey('Dim_Job_Role.job_role_id'), nullable=False)
    source_id = Column(BigInteger, ForeignKey('Dim_Source.source_id'), nullable=False)
    salary_max = Column(BigInteger)
    salary_min = Column(BigInteger)
    years_of_experience = Column(Integer)
    job_level = Column(String(10))
    job_type = Column(String(10))
    inserted_date = Column(Date, default=datetime.now().date(), comment='job post fact table')

    def __init__(self, company_id, start_recruit_date_id, end_recruit_date_id, job_role_id, source_id, 
                 salary_max=None, salary_min=None, years_of_experience=None, job_level=None, 
                 job_type=None, inserted_date=None):
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

engine = create_engine(f'postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/JobPostManagement')
Base.metadata.create_all(engine)