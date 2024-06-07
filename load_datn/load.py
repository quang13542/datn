import pandas as pd
from datetime import datetime
from metadata import session, cities, sourth_region, north_region, central_region
from datetime import datetime
import ast
import os
from tqdm import tqdm
from geoapivietnam import Correct

from load_datn.models import (
    DimCompany,
    DimDate,
    DimJobRole,
    DimPosition,
    DimSkill,
    DimSkillList,
    DimSource,
    FactJobPost
)

def find_city(position):
    if position is None:
        return None
    for city in cities:
        if city in position:
            return city
    return None

def assign_region(city):
    if city in sourth_region:
        return 'Miền Nam'
    elif city in central_region:
        return 'Miền Trung'
    elif city in north_region:
        return 'Miền Bắc'
    return None

def get_first_element(value):
    try:
        value = ast.literal_eval(value)
        if isinstance(value, list):
            return value[0] if len(value)!=0 else None
    except (ValueError, SyntaxError):
        pass
    return value

def upsert_data():
    folder_path = "./load_datn/combined_source"
    all_items = os.listdir(folder_path)
        
    # Filter out directories, we only want files
    files = [f for f in all_items if os.path.isfile(os.path.join(folder_path, f))]
    
    # Find the lexicographically greatest filename
    if files:
        greatest_name = max(files)
    
    df = pd.read_csv(f'{folder_path}/{greatest_name}', header=0)
    
    # upsert_company
    company_list = df[['company_name']].value_counts().index.values.tolist()
    company_list = [' '.join(company).lower() for company in company_list]
    
    query = session.query(DimCompany).filter(DimCompany.name.in_(company_list))
    results = query.all()
    df['company_size'] = df['company_size'].fillna(0)
    unique_company_list = df[['company_name', 'company_size']].value_counts().index.values.tolist()
    existing_companies = [company.name for company in results]

    insert_count = 0
    company_dict = {}
    new_company_name_list = []
    for company in results:
        company_dict[company.name] = company.company_id
    for company in unique_company_list:
        if company[0].lower() not in existing_companies:
            new_company = DimCompany(
                size=str(company[1]),
                name=company[0].lower(),
                inserted_date=datetime.now().date()
            )
            new_company_name_list.append(company[0].lower())
            session.add(new_company)
            insert_count += 1
    session.commit()
    query = session.query(DimCompany).filter(DimCompany.name.in_(new_company_name_list))
    results = query.all()

    for company in results:
        company_dict[company.name] = company.company_id
    print(f"insert {insert_count} company")

    df['company_id'] = df['company_name'].map(lambda x: company_dict[x.lower()])

    # upsert source
    source_list = df[['source']].value_counts().index.values.tolist()
    source_list = [' '.join(source).lower() for source in source_list]
    query = session.query(DimSource).filter(DimSource.name.in_(source_list))
    results = query.all()

    unique_source_list = df[['source']].value_counts().index.values.tolist()

    existing_sources = [source.name for source in results]

    insert_count = 0
    source_dict = {}
    new_source_name_list = []
    for source in results:
        source_dict[source.name] = source.source_id
    for source in unique_source_list:
        if source[0].lower() not in existing_sources:
            new_source = DimSource(
                name=source[0].lower(),
                url='',
                inserted_date=datetime.now().date()
            )
            new_source_name_list.append(source[0].lower())
            existing_sources.append(source[0].lower())
            session.add(new_source)
            insert_count += 1
    session.commit()
    print(f"insert {insert_count} source")
    query = session.query(DimSource).filter(DimSource.name.in_(new_source_name_list))
    results = query.all()

    for source in results:
        source_dict[source.name] = source.source_id

    df['source_id'] = df['source'].map(lambda x: source_dict[x.lower()])

    # upsert job role
    df['job_detail_extracted_job_role'].fillna(df['job_detail_name'], inplace=True)
    job_role_list = df[['job_detail_extracted_job_role']].value_counts().index.values.tolist()
    job_role_list = [' '.join(job_role).lower() for job_role in job_role_list]
    query = session.query(DimJobRole).filter(DimJobRole.name.in_(job_role_list))
    results = query.all()
    
    unique_job_role_list = df[['job_detail_extracted_job_role']].value_counts().index.values.tolist()

    existing_job_roles = [job_role.name for job_role in results]

    insert_count = 0
    job_role_dict = {}
    new_job_role_name_list = []
    for job_role in results:
        job_role_dict[job_role.name] = job_role.job_role_id
    for job_role in unique_job_role_list:
        if job_role[0].lower() not in existing_job_roles:
            new_job_role = DimJobRole(
                name=job_role[0].lower(),
                category=job_role[0].lower(),
                inserted_date=datetime.now().date()
            )
            new_job_role_name_list.append(job_role[0].lower())
            existing_job_roles.append(job_role[0].lower())
            session.add(new_job_role)
            insert_count += 1
    session.commit()
    query = session.query(DimJobRole).filter(DimJobRole.name.in_(new_job_role_name_list))
    results = query.all()

    for job_role in results:
        job_role_dict[job_role.name] = job_role.job_role_id
    print(f"insert {insert_count} job_role")

    df['job_role_id'] = df['job_detail_extracted_job_role'].map(lambda x: job_role_dict[x.lower()])

    # upsert skill
    df['job_detail_extracted_skill'] = df['job_detail_extracted_skill'].apply(ast.literal_eval)
    unique_skills = set()
    df['job_detail_extracted_skill'].apply(lambda skills: unique_skills.update(skills))
    skills_list = list(unique_skills)

    query = session.query(DimSkill).filter(DimSkill.name.in_(skills_list))
    results = query.all()
    
    existing_skills = [skill.name for skill in results]

    update_count = 0
    insert_count = 0
    skill_dict = {}
    for skill in results:
        skill_dict[skill.name] = skill.skill_id
    new_skill_name_list = []
    for skill in skills_list:
        if skill.lower() not in existing_skills:
            new_skill = DimSkill(
                name=skill.lower(),
                category=skill.lower(),
                inserted_date=datetime.now().date()
            )
            new_skill_name_list.append(skill)
            existing_skills.append(skill)
            session.add(new_skill)
            insert_count += 1
    session.commit()
    query = session.query(DimSkill).filter(DimSkill.name.in_(new_skill_name_list))
    results = query.all()

    for skill in results:
        skill_dict[skill.name] = skill.skill_id
    print(f"insert {insert_count} skill")

    df['skill_id'] = df['job_detail_extracted_skill'].map(lambda skill_list: [skill_dict[x.lower()] for x in skill_list])
    
    # upsert position
    correct = Correct(use_fuzzy=True, print_result=True)
    df['company_position'] = df['company_position'].apply(get_first_element)
    df['company_position'] = df['company_position'].fillna(value='unknown')
    company_position_list = df[['company_position']].value_counts().index.values.tolist()
    company_position_list = [' '.join(company_position) for company_position in company_position_list]
    query = session.query(DimPosition).filter(DimPosition.detail_position.in_(company_position_list))
    results = query.all()

    unique_company_position_list = df[['company_position', 'company_id']].value_counts().index.values.tolist()

    existing_company_positions = [company_position.detail_position for company_position in results]

    insert_count = 0
    company_position_dict = {}
    new_company_position_name_list = []
    for company_position in results:
        company_position_dict[company_position.detail_position] = company_position.position_id
    for company_position in unique_company_position_list:
        if company_position[0] not in existing_company_positions:
            city = correct.correct_province(company_position[0].split(',')[-1])
            region = assign_region(city)
            new_company_position = DimPosition(
                detail_position=company_position[0],
                city=city,
                region=region,
                inserted_date=datetime.now().date()
            )
            new_company_position_name_list.append(company_position[0])
            existing_company_positions.append(company_position[0])
            session.add(new_company_position)
            insert_count += 1
    session.commit()
    print(f"insert {insert_count} company_position")
    query = session.query(DimPosition).filter(DimPosition.detail_position.in_(new_company_position_name_list))
    results = query.all()

    for company_position in results:
        company_position_dict[company_position.detail_position] = company_position.position_id

    df['company_position_id'] = df['company_position'].map(lambda x: None if x is None else company_position_dict[x])

    # upsert date
    # df['crawl_date'] = df['crawl_date'].map(lambda x:datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    date_list = df['crawl_date'].value_counts().index.values.tolist()
    query = session.query(DimDate).filter(DimDate.date.in_(date_list))
    results = query.all()
    
    unique_date_list = df[['crawl_date']].value_counts().index.values.tolist()

    existing_dates = [datetime.strftime(date.date, '%Y-%m-%d %H:%M:%S') for date in results]

    insert_count = 0
    date_dict = {}
    new_date_name_list = []
    for date in results:
        date_dict[datetime.strftime(date.date, '%Y-%m-%d %H:%M:%S')] = date.date_id
    for date in unique_date_list:
        if date[0] not in existing_dates:
            date_tmp = datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            new_date = DimDate(
                date=date[0],
                day=date_tmp.day,
                month=date_tmp.month,
                year=date_tmp.year,
                quarter=(date_tmp.month - 1) // 3 + 1,
                inserted_date=datetime.now().date()
            )
            new_date_name_list.append(date[0])
            existing_dates.append(date[0])
            session.add(new_date)
            insert_count += 1
    session.commit()
    query = session.query(DimDate).filter(DimDate.date.in_(new_date_name_list))
    results = query.all()

    for date in results:
        date_dict[datetime.strftime(date.date, '%Y-%m-%d %H:%M:%S')] = date.date_id
    print(f"insert {insert_count} date")

    df['date_id'] = df['crawl_date'].map(lambda x: date_dict[x])

    # upsert fact job post
    job_post_list = df[['company_id', 'job_role_id', 'source_id', 'date_id']].value_counts().index.values.tolist()
    company_id_list = list(set([job_post[0] for job_post in job_post_list]))
    job_role_id_list = list(set([job_post[1] for job_post in job_post_list]))
    source_id_list = list(set([job_post[2] for job_post in job_post_list]))
    date_id_list = list(set([job_post[3] for job_post in job_post_list]))

    query = session.query(FactJobPost).\
        filter(FactJobPost.end_recruit_date_id==None).\
        filter(FactJobPost.company_id.in_(company_id_list)).\
        filter(FactJobPost.job_role_id.in_(job_role_id_list)).\
        filter(FactJobPost.source_id.in_(source_id_list)).\
        filter(FactJobPost.start_recruit_date_id.in_(date_id_list))
    results = query.all()
    existing_job_post = [(
        job_post.company_id,
        job_post.job_role_id,
        job_post.source_id,
        job_post.start_recruit_date_id,
    ) for job_post in results]
    df[[
        'job_detail_full_time',
        'job_detail_part_time',
        'job_detail_remote',
        'job_detail_hybrid'
    ]] = df[[
        'job_detail_full_time',
        'job_detail_part_time',
        'job_detail_remote',
        'job_detail_hybrid'
    ]].fillna(value=False)
    df['job_detail_job_level'] = df['job_detail_job_level'].fillna(value='unknown')
    df[[
        'job_detail_salary_range_min',
        'job_detail_salary_range_max'
    ]] = df[[
        'job_detail_salary_range_min',
        'job_detail_salary_range_max'
    ]].fillna(value=0)
    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].fillna(value=-1)
    unique_record_list = df[[
        'company_id',
        'job_role_id',
        'source_id',
        'date_id',
        'job_detail_job_level',
        'job_detail_salary_range_max',
        'job_detail_salary_range_min',
        'job_detail_year_of_exp',
        'job_detail_hybrid',
        'job_detail_full_time',
        'job_detail_part_time',
        'job_detail_remote',
        'company_position_id'
    ]].value_counts().index.values.tolist()
    # print(len(unique_record_list))
    # print(df.count())
    # print(df[df['company_position_id'].isna()]['url'])
    # print(df.iloc[6287]['company_position'])
    insert_count = 0
    job_post_dict = {}
    new_job_post_list = []
    for job_post in results:
        job_post_dict[(
            job_post.company_id,
            job_post.job_role_id,
            job_post.source_id,
            job_post.start_recruit_date_id,
        )] = job_post.job_post_id
    for job_post in unique_record_list:
        if (job_post[:4]) not in existing_job_post:
            job_type = None
            if job_post[8] == True:
                job_type = 'hybrid'
            if job_post[9] == True:
                job_type = 'full_time'
            if job_post[10] == True:
                job_type = 'part_time'
            if job_post[11] == True:
                job_type = 'remote'
            new_job_post = FactJobPost(
                company_id=job_post[0],
                job_role_id=job_post[1],
                source_id=job_post[2],
                start_recruit_date_id=job_post[3],
                end_recruit_date_id=None,
                inserted_date=datetime.now().date(),
                job_level=job_post[4],
                job_type=job_type,
                salary_max=job_post[5],
                salary_min=job_post[6],
                years_of_experience=job_post[7],
                position_id=job_post[12]
            )
            new_job_post_list.append((
                new_job_post.company_id,
                new_job_post.job_role_id,
                new_job_post.source_id,
                new_job_post.start_recruit_date_id,
            ))
            existing_job_post.append((
                new_job_post.company_id,
                new_job_post.job_role_id,
                new_job_post.source_id,
                new_job_post.start_recruit_date_id,
            ))
            session.add(new_job_post)
            insert_count += 1
    session.commit()
    query = session.query(FactJobPost).\
        filter(FactJobPost.end_recruit_date_id==None).\
        filter(FactJobPost.company_id.in_(company_id_list)).\
        filter(FactJobPost.job_role_id.in_(job_role_id_list)).\
        filter(FactJobPost.source_id.in_(source_id_list)).\
        filter(FactJobPost.start_recruit_date_id.in_(date_id_list))
    results = query.all()

    for job_post in results:
        job_post_dict[(
            job_post.company_id,
            job_post.job_role_id,
            job_post.source_id,
            job_post.start_recruit_date_id,
        )] = job_post.job_post_id
    print(f"insert {insert_count} job_post")

    df['job_post_id'] = df.apply(lambda row: job_post_dict[(row['company_id'], row['job_role_id'], row['source_id'], row['date_id'])], axis=1)
    
    # upsert skill list
    skill_list_list = list(df[['job_post_id', 'skill_id']].itertuples(index=False, name=None))
    job_post_id_list = list(set([skill_list[0] for skill_list in skill_list_list]))
    skill_id_list = []
    for skill_list in skill_list_list:
        skill_id_list.extend(skill_list[1])
    skill_list_list = list(set(skill_id_list))
    query = session.query(DimSkillList).\
        filter(DimSkillList.job_post_id.in_(job_post_id_list)).\
        filter(DimSkillList.skill_id.in_(skill_id_list))
    results = query.all()
    existing_skill_list = [(
        skill_list.job_post_id,
        skill_list.skill_id,
    ) for skill_list in results]
    unique_record_list =  list(df[['job_post_id', 'skill_id']].itertuples(index=False, name=None))
    insert_count = 0
    skill_list_dict = {}
    new_skill_list_list = []
    for skill_list in results:
        skill_list_dict[(
            skill_list.job_post_id,
            skill_list.skill_id,
        )] = skill_list.skill_job_post_id
    for skill_list in tqdm(unique_record_list):
        for skill_id in skill_list[1]:
            if (skill_list[0], skill_id) not in existing_skill_list:
                new_skill_list = DimSkillList(
                    core_skill=True,
                    inserted_date=datetime.now().date(),
                    job_post_id=skill_list[0],
                    skill_id=skill_id,
                )
                new_skill_list_list.append((
                    new_skill_list.job_post_id,
                    new_skill_list.skill_id,
                ))
                existing_skill_list.append((
                    new_skill_list.job_post_id,
                    new_skill_list.skill_id,
                ))
                session.add(new_skill_list)
                insert_count += 1
    session.commit()
    # query = session.query(DimSkillList).\
    #     filter(DimSkillList.job_post_id.in_(job_post_id_list)).\
    #     filter(DimSkillList.skill_id.in_(skill_id_list))
    # results = query.all()

    # for skill_list in results:
    #     skill_list_dict[(
    #         skill_list.job_post_id,
    #         skill_list.skill_id,
    #     )] = skill_list.skill_job_post_id
    print(f"insert {insert_count} skill_list")

    # df['skill_list_id'] = df.apply(lambda row: skill_list_dict[(row['job_post_id'], row['skill_id'])], axis=1)


def combine_data():
    df1 = pd.read_csv('./transform_datn/transformed_ITjobs.csv')
    df2 = pd.read_csv('./transform_datn/transformed_ITViec.csv')
    df3 = pd.read_csv('./transform_datn/transformed_TopCV.csv')
    df4 = pd.read_csv('./transform_datn/transformed_TopDev.csv')

    combined_df = pd.concat([df1, df2, df3, df4], axis=0, ignore_index=True)

    combined_df.to_csv(f"./load_datn/combined_source/{datetime.today().strftime('%Y_%m_%d')}_combined_data.csv")

    return f"./load_datn/combined_source/{datetime.today().strftime('%Y_%m_%d')}_combined_data.csv"