import json
import pandas as pd
import ast
import re
import matplotlib.pyplot as plt
from transform_datn.labeling_tool import Trie, TrieNode, search_in_trie

metric_dict = {
    'vnd': 1,
    'triệu': 1000000,
    'tr': 1000000,
    'usd': 25000
}

time_unit = [
    'years',
    'year',
    'months',
    'month',
    'năm',
    'tháng'
]

pattern = f"(\S+)\s({'|'.join(time_unit)})(?!(?:\s*old|s\sold)\b)"

full_time_keyword = ['toàn thời gian', 'full time', 'full-time', 'full_time']
part_time_keyword = ['bán thời gian', 'part time', 'part-time', 'part_time']
job_level_list = ['intern', 'fresher', 'junior', 'senior']
year_of_exp_list = ['years', 'year', 'năm kinh nghiệm']

def transform_ITjobs():
    def extract_year(year_exp):
        matches = re.findall(pattern, year_exp)
        res = []
        for match in matches:
            res.append(match[0] + ' ' + match[1])
        return res

    def get_the_experience(list_string):
        tmp_list_string = [extract_year(string) for string in list_string]
        while len(tmp_list_string) != 0:
            if len(tmp_list_string[0]) == 0:
                tmp_list_string.pop(0)
            else:
                break
        if len(tmp_list_string) == 0:
            return None
        first_line_experience = tmp_list_string[0]
        while len(first_line_experience) != 0:
            if re.search(r'\d+', first_line_experience[0]) is None:
                first_line_experience.pop(0)
            else:
                break
        if len(first_line_experience) == 0:
            return None
        number = int(re.findall(r'\d+', first_line_experience[0])[0])
        if 'tháng' in first_line_experience[0] or \
            'month' in first_line_experience[0] or \
            'months' in first_line_experience[0]:
            number = float(number/12)
        return number

    def extract_salary(salary):
        matches = re.findall(r'[-+]?(?:\d*\.*\d+)', salary.replace(',', ''))
        number = -1
        if len(matches) == 0:
            return []
        for metric in metric_dict.keys():
            if metric in salary.lower():
                number = metric_dict[metric]
        if 'usd' in salary.lower():
            matches = [match.replace('.', '') for match in matches]
            if float(matches[0]) > 5000000:
                number = 1
        if float(matches[0]) < 10000:
            number = 25000
        return [float(match) * (number if float(match)<5000000 else 1) for match in matches]


    with open("./crawler_datn/ITjobs_ver2.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        
    url_list = list(json_data.keys())

    data = []

    for url, extracted_data in json_data.items():
        transformed_data = {
            "url": url,
            "source": extracted_data['metadata']['source'],
            "crawl_date": extracted_data['metadata']['created_date']
        }

        transformed_data['company'] = {}
        transformed_data['job_detail'] = {}
        lines = extracted_data['text'].split('\n')

        #company_name
        transformed_data['company']['name'] = lines[0]
        transformed_data['company']['position'] = [lines[1]]
        transformed_data['company']['size'] = lines[2].replace('Quy mô công ty : ', '')
        transformed_data['job_detail']['name'] = lines[8]
        transformed_data['job_detail']['salary'] = lines[11]
        transformed_data['job_detail']['year_of_exp'] = []
        transformed_data['job_detail']['job_requirements_line'] = []
        transformed_data['job_detail']['job_level'] = []
        fl_skill_requirement = False
        
        for job_level in job_level_list:
            if type(job_level) is dict:
                for level in list(job_level.values())[0]:
                    if level in transformed_data['job_detail']['name'].lower():
                        transformed_data['job_detail']['job_level'].append(job_level.keys()[0])
            elif type(job_level) is str:
                if job_level in transformed_data['job_detail']['name'].lower():
                    transformed_data['job_detail']['job_level'].append(job_level)

        for line in lines:
            line_lower = line.lower()

            transformed_data['job_detail']['full_time'] = False
            transformed_data['job_detail']['part_time'] = False
            transformed_data['job_detail']['remote'] = False
            
            #Job_requirement
            if 'Yêu cầu kỹ thuật: ' in line:
                transformed_data['job_detail']['job_requirements'] = line.replace('Yêu cầu kỹ thuật: ', '').split(', ')
            
            # Fulltime, Parttime, Remote
            for keyword in full_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['full_time'] = True
            if 'bán thời gian' in line_lower or 'part time' in line_lower or 'part-time' in line_lower or 'part_time' in line_lower:
                transformed_data['job_detail']['part_time'] = True
            if 'remote' in line_lower:
                transformed_data['job_detail']['remote'] = True
            
            if line == "NGÔN NGỮ":
                fl_skill_requirement = False
            if fl_skill_requirement == True:
                if 'years old' in line or 'tuổi' in line:
                    continue
                transformed_data['job_detail']['job_requirements_line'].append(line)
                for year_of_exp in year_of_exp_list:
                    if year_of_exp in line_lower:
                        transformed_data['job_detail']['year_of_exp'].append(line)
                        break
            if line == 'YÊU CẦU CÔNG VIỆC':
                fl_skill_requirement = True

        data.append(transformed_data)
        # break

    df_dictionary = pd.DataFrame([{
        "url": job['url'],
        "source": job['source'],
        "crawl_date": job['crawl_date'],
        "company_name": job['company']['name'],
        "company_position": job['company']['position'],
        "company_size": job['company']['size'],
        "job_detail_name": job['job_detail']['name'],
        "job_detail_salary":job['job_detail']['salary'],
        "job_detail_full_time": job['job_detail']['full_time'],
        "job_detail_remote": job['job_detail']['remote'],
        # "job_detail_hybrid": job['job_detail']['hybrid'],
        "job_detail_job_requirements": job['job_detail']['job_requirements'],
        "job_detail_job_requirements_line": job['job_detail']['job_requirements_line'],
        "job_detail_year_of_exp": job['job_detail']['year_of_exp'],
        "job_detail_job_level": job['job_detail'].get('job_level'),
    } for job in data])
    df = pd.DataFrame.from_dict(df_dictionary)

    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].apply(get_the_experience)

    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].map(lambda x: x/10 if x>40 else x)

    df['job_detail_job_level'] = df['job_detail_job_level'].map(lambda x: None if len(x) == 0 else x[-1])

    df['job_detail_salary_range'] = df['job_detail_salary'].map(extract_salary)
    df['job_detail_currency'] = df['job_detail_salary'].map(lambda x: 'usd' if 'usd' in x.lower() else None)
    df['new_col'] = df['job_detail_salary_range'].map(lambda x: len(x))

    df['job_detail_salary_range_max'] = df['job_detail_salary_range'].apply(lambda x: x[-1] if len(x) != 0 else 0)
    df['job_detail_salary_range_min'] = df['job_detail_salary_range'].apply(lambda x: x[0] if len(x) == 2 else 0)

    # build tree
    f = open("transform_datn/skill_list.txt", "r")
    skill_list = list(f)
    trie_directory = '/trie_struture'
    skill_list = [x.lower() for x in skill_list]

    # for x in df['job_detail_job_requirements']:
    #     skill_list.extend(x)

    skill_list = list(set(skill_list))

    file = open('skill_list.txt','w')
    for skill in skill_list:
        file.write(skill.replace('\n', '').rstrip()+"\n")
    file.close()

    trie = Trie()
    for skill in skill_list:
        trie.insert(skill)

    def extract_skill(lines):
        res = []
        for line in lines:
            res.extend(search_in_trie(trie, line))
        return res

    df['job_detail_extracted_skill'] = df['job_detail_job_requirements_line'].apply(extract_skill)

    f = open("transform_datn/job_role.txt", "r")
    job_role_list = list(f)
    trie_directory = '/trie_struture'
    job_role_list = [x.lower() for x in job_role_list]

    job_role_list = list(set(job_role_list))

    trie_job_role = Trie()
    for job_role in job_role_list:
        trie_job_role.insert(job_role)

    def extract_job_role(line):
        res = []
        res.extend(search_in_trie(trie_job_role, line.lower()))
        return res[0] if len(res)!=0 else None

    df['job_detail_extracted_job_role'] = df['job_detail_name'].apply(extract_job_role)

    df.to_csv('transform_datn/transformed_ITjobs_ver2.csv', index=False)

def transform_TopCV():
    with open("./transform_datn/TopCv.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        
    url_list = list(json_data.keys())

    data = []

    for url, extracted_data in json_data.items():
        transformed_data = {
            "url": url,
            "source": extracted_data['metadata']['source'],
            "crawl_date": extracted_data['metadata']['created_date']
        }

        transformed_data['company'] = {}
        transformed_data['job_detail'] = {}
        lines = extracted_data['text'].split('\n')

        #company_name
        
        transformed_data['company']['position'] = [lines[4]]
        
        transformed_data['job_detail']['name'] = lines[0]
        transformed_data['job_detail']['salary'] = lines[2]

        transformed_data['job_detail']['full_time'] = False
        transformed_data['job_detail']['part_time'] = False
        transformed_data['job_detail']['remote'] = False
        transformed_data['job_detail']['job_requirements_line'] = []
        transformed_data['job_detail']['year_of_exp'] = []
        transformed_data['job_detail']['job_level'] = []
        fl_skill_requirement = False

        for job_level in job_level_list:
            if type(job_level) is dict:
                for level in list(job_level.values())[0]:
                    if level in transformed_data['job_detail']['name'].lower():
                        transformed_data['job_detail']['job_level'].append(job_level.keys()[0])
            elif type(job_level) is str:
                if job_level in transformed_data['job_detail']['name'].lower():
                    transformed_data['job_detail']['job_level'].append(job_level)

        previous_line = ''

        for line in lines:
            line_lower = line.lower()
            
            # Fulltime, Parttime, Remote
            for keyword in full_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['full_time'] = True
            for keyword in part_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['part_time'] = True
            if 'remote' in line_lower:
                transformed_data['job_detail']['remote'] = True
            
            if previous_line == 'Khóa học dành cho bạn':
                transformed_data['company']['name'] = line
            if previous_line == 'Quy mô:':
                transformed_data['company']['size'] = line
            if previous_line == 'Địa điểm làm việc':
                transformed_data['company']['detail_position'] = line
            if previous_line == 'Kinh nghiệm':
                transformed_data['job_detail']['year_of_exp'].append(line)
            
            if line == "Quyền lợi":
                fl_skill_requirement = False
            if line == 'Yêu cầu ứng viên':
                fl_skill_requirement = True
            if fl_skill_requirement == True:
                transformed_data['job_detail']['job_requirements_line'].append(line)

            previous_line = line
            
        data.append(transformed_data)
        # break

    df_dictionary = pd.DataFrame([{
        "url": job['url'],
        "source": job['source'],
        "crawl_date": job['crawl_date'],
        "company_name": job['company']['name'],
        "company_position": job['company']['position'],
        "job_detail_detail_position": job['company']['detail_position'],
        "company_size": job['company']['size'],
        "job_detail_name": job['job_detail']['name'],
        "job_detail_salary": job['job_detail']['salary'],
        "job_detail_part_time": job['job_detail']['part_time'],
        "job_detail_full_time": job['job_detail']['full_time'],
        "job_detail_remote": job['job_detail']['remote'],
        "job_detail_job_requirements_line": job['job_detail']['job_requirements_line'],
        "job_detail_year_of_exp": job['job_detail']['year_of_exp'],
        "job_detail_job_level": job['job_detail'].get('job_level'),
    } for job in data])
    df = pd.DataFrame.from_dict(df_dictionary)

    df['job_detail_hybrid'] = False
    df.loc[(df['job_detail_remote'] == True) & (df['job_detail_full_time'] == True), 'job_detail_hybrid'] = True

    df = df.drop('job_detail_remote', axis=1)

    def extract_year_of_exp(list_text):
        matches = re.findall(r'\d+', list_text[0])
        return int(matches[0]) if matches else 0

    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].map(extract_year_of_exp)

    filtered_indices = df[df['job_detail_job_level'].apply(lambda x: len(x)) == 2].index
    df.loc[filtered_indices, 'job_detail_job_level'] = df.loc[filtered_indices]['job_detail_job_level'].apply(lambda x: [x[-1]])

    filtered_indices = df[df['job_detail_job_level'].apply(lambda x: len(x)) != 0].index
    df.loc[filtered_indices, 'job_detail_job_level'] = df.loc[filtered_indices]['job_detail_job_level'].apply(lambda x: x[-1])

    filtered_indices = df[df['job_detail_job_level'].apply(len) == 0].index

    # Set these values to NaN (null)
    df.loc[filtered_indices, 'job_detail_job_level'] = None

    time_unit = [
        'years',
        'year',
        'months',
        'month',
        'năm kinh nghiệm',
        'tháng'
    ]
    def extract_year(exp):
        for year_exp in exp:
            pattern = f"(\S+)\s({'|'.join(time_unit)})"
            matches = re.findall(pattern, year_exp)
            for match in matches:
                number_list = re.findall('\d+', match[0])
                if match[1] in ['months', 'month', 'tháng']:
                    number = [float(number)/12 for number in number_list]
                else:
                    number = [float(number) for number in number_list]
                while len(number) != 0:
                    if number[0]>10:
                        number.remove(number[0])
                    else:
                        break
                return number[0] if len(number)!=0 else None

    df['job_detail_year_exp_from_requirement'] = df['job_detail_job_requirements_line'].map(lambda exp:
        extract_year(exp)
    )

    df['job_detail_year_exp_from_requirement_and_year_exp'] = df[["job_detail_year_exp_from_requirement", "job_detail_year_of_exp"]].max(axis=1)

    # problem: '.', ',' in salary; 'usd' and 'trieu' is wrong 

    metric_dict = {
        'triệu': 1000000,
        'tr': 1000000,
        'usd': 25000
    }

    def extract_salary(salary):
        matches = re.findall(r'[-+]?(?:\d*\.*\d+)', salary.replace(',', ''))
        number = -1
        for metric in metric_dict.keys():
            if metric in salary.lower():
                number = metric_dict[metric]
        if 'usd' in salary.lower():
            matches = [match.replace('.', '') for match in matches]
            if float(matches[0]) > 5000000:
                number = 1
        return [float(match) * (number if float(match)<5000000 else 1) for match in matches]

    df['job_detail_salary_range'] = df['job_detail_salary'].map(extract_salary)
    df['job_detail_currency'] = df['job_detail_salary'].map(lambda x: 'usd' if 'usd' in x.lower() else None)
    df['new_col'] = df['job_detail_salary_range'].map(lambda x: len(x))

    df['job_detail_salary_range_max'] = df['job_detail_salary_range'].apply(lambda x: x[-1] if len(x) != 0 else 0)
    df['job_detail_salary_range_min'] = df['job_detail_salary_range'].apply(lambda x: x[0] if len(x) == 2 else 0)

    # build tree
    f = open("transform_datn/skill_list.txt", "r")
    skill_list = list(f)
    trie_directory = '/trie_struture'
    skill_list = [x.lower() for x in skill_list]

    skill_list = list(set(skill_list))

    file = open('transform_datn/skill_list.txt','w')
    for skill in skill_list:
        file.write(skill.replace('\n', '').rstrip()+"\n")
    file.close()

    trie = Trie()
    for skill in skill_list:
        trie.insert(skill)

    def extract_skill(lines):
        res = []
        for line in lines:
            res.extend(search_in_trie(trie, line))
        return res

    df['job_detail_extracted_skill'] = df['job_detail_job_requirements_line'].apply(extract_skill)

    # build tree
    f = open("transform_datn/job_role.txt", "r")
    job_role_list = list(f)
    trie_directory = '/trie_struture'
    job_role_list = [x.lower() for x in job_role_list]

    job_role_list = list(set(job_role_list))

    trie_job_role = Trie()
    for job_role in job_role_list:
        trie_job_role.insert(job_role)

    def extract_job_role(line):
        res = []
        res.extend(search_in_trie(trie_job_role, line.lower()))
        return res[0] if len(res)!=0 else None

    df['job_detail_extracted_job_role'] = df['job_detail_name'].apply(extract_job_role)

    df.to_csv('transform_datn/transformed_TopCV.csv', index=False)

def transform_ITViec():
    with open("./transform_datn/ITViec.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        
    url_list = list(json_data.keys())
    data = []

    for url, extracted_data in json_data.items():
        transformed_data = {
            "url": url,
            "source": extracted_data['metadata']['source'],
            "crawl_date": extracted_data['metadata']['created_date']
        }

        transformed_data['company'] = {}
        transformed_data['job_detail'] = {}
        lines = extracted_data['text'].split('\n')
        lines = [line.lstrip() for line in lines]
        
        #company_name
        
        transformed_data['company']['name'] = lines[1]
        transformed_data['company']['position'] = []
        
        transformed_data['job_detail']['name'] = lines[0]

        transformed_data['job_detail']['full_time'] = False
        transformed_data['job_detail']['remote'] = False
        transformed_data['job_detail']['hybrid'] = False
        transformed_data['job_detail']['job_requirements'] = []
        transformed_data['job_detail']['job_requirements_line'] = []
        transformed_data['job_detail']['year_of_exp'] = []
        transformed_data['job_detail']['job_level'] = []

        previous_line = ''
        fl_skill = False
        fl_skill_requirement = False
        fl_position = False

        for job_level in job_level_list:
            if type(job_level) is dict:
                for level in list(job_level.values())[0]:
                    if level in transformed_data['job_detail']['name'].lower():
                        transformed_data['job_detail']['job_level'].append(job_level.keys()[0])
            elif type(job_level) is str:
                if job_level in transformed_data['job_detail']['name'].lower():
                    transformed_data['job_detail']['job_level'].append(job_level)

        for line in lines:
            line_lower = line.lower()
            
            # Fulltime, Remote
            for keyword in full_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['full_time'] = True
            if 'remote' in line_lower:
                transformed_data['job_detail']['remote'] = True
            
            if line == 'Top 3 reasons to join us':
                fl_skill = False
            if fl_skill == True:
                transformed_data['job_detail']['job_requirements'].append(line)
            if line == 'Skills:':
                fl_skill = True

            if line == "Why you'll love working here":
                fl_skill_requirement = False
            if fl_skill_requirement == True:
                if 'years old' in line or 'tuổi' in line:
                    continue
                transformed_data['job_detail']['job_requirements_line'].append(line)
                for year_of_exp in year_of_exp_list:
                    if year_of_exp in line_lower:
                        transformed_data['job_detail']['year_of_exp'].append(line)
                        break
            if line == 'Your skills and experience':
                fl_skill_requirement = True

            if 'At office' in line or 'Hybrid' in line or 'Remote' in line:
                if 'At office' in line:
                    transformed_data['job_detail']['full_time'] = True
                elif 'Hybrid' in line:
                    transformed_data['job_detail']['hybrid'] = True
                elif 'Remote' in line:
                    transformed_data['job_detail']['remote'] = True
                fl_position = False
            if fl_position == True:
                transformed_data['company']['position'].append(line)
            if line == 'Sign in to view salary':
                fl_position = True
            
            previous_line = line
        if 'Apply now' in transformed_data['company']['position']:
            transformed_data['company']['position'].remove('Apply now')
        data.append(transformed_data)
        # break
    # data = list(set(data))

    df_dictionary = pd.DataFrame([{
        "url": job['url'],
        "source": job['source'],
        "crawl_date": job['crawl_date'],
        "company_name": job['company']['name'],
        "company_position": job['company']['position'],
        "job_detail_name": job['job_detail']['name'],
        "job_detail_full_time": job['job_detail']['full_time'],
        "job_detail_remote": job['job_detail']['remote'],
        "job_detail_hybrid": job['job_detail']['hybrid'],
        "job_detail_job_requirements": job['job_detail']['job_requirements'],
        "job_detail_job_requirements_line": job['job_detail']['job_requirements_line'],
        "job_detail_year_of_exp": job['job_detail']['year_of_exp'],
        "job_detail_job_level": job['job_detail'].get('job_level'),
    } for job in data])
    df = pd.DataFrame.from_dict(df_dictionary)

    def extract_year(year_exp):
        matches = re.findall(pattern, year_exp)
        # print(pattern)
        res = []
        for match in matches:
            res.append(match[0] + ' ' + match[1])
        return res

    def get_the_experience(list_string):
        tmp_list_string = [extract_year(string) for string in list_string]
        while len(tmp_list_string) != 0:
            if len(tmp_list_string[0]) == 0:
                tmp_list_string.pop(0)
            else:
                break
        if len(tmp_list_string) == 0:
            return None
        first_line_experience = tmp_list_string[0]
        while len(first_line_experience) != 0:
            if re.search(r'\d+', first_line_experience[0]) is None:
                first_line_experience.pop(0)
            else:
                break
        if len(first_line_experience) == 0:
            return None
        number = int(re.findall(r'\d+', first_line_experience[0])[0])
        if 'tháng' in first_line_experience[0] or \
            'month' in first_line_experience[0] or \
            'months' in first_line_experience[0]:
            number = float(number/12)
        return number

    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].apply(get_the_experience)

    df['job_detail_job_level'] = df['job_detail_job_level'].map(lambda x: None if len(x) == 0 else x[-1])

    # build tree
    f = open("transform_datn/skill_list.txt", "r")
    skill_list = list(f)
    trie_directory = '/trie_struture'
    skill_list = [x.lower() for x in skill_list]

    skill_list = list(set(skill_list))

    file = open('transform_datn/skill_list.txt','w')
    for skill in skill_list:
        file.write(skill.replace('\n', '').rstrip()+"\n")
    file.close()

    trie = Trie()
    for skill in skill_list:
        trie.insert(skill)

    def extract_skill(lines):
        res = []
        for line in lines:
            res.extend(search_in_trie(trie, line))
        return res

    df['job_detail_extracted_skill'] = df['job_detail_job_requirements_line'].apply(extract_skill)

    # build tree
    f = open("transform_datn/job_role.txt", "r")
    job_role_list = list(f)
    trie_directory = '/trie_struture'
    job_role_list = [x.lower() for x in job_role_list]

    job_role_list = list(set(job_role_list))

    trie_job_role = Trie()
    for job_role in job_role_list:
        trie_job_role.insert(job_role)

    def extract_job_role(line):
        res = []
        res.extend(search_in_trie(trie_job_role, line.lower()))
        return res[0] if len(res)!=0 else None

    df['job_detail_extracted_job_role'] = df['job_detail_name'].apply(extract_job_role)

    df.to_csv('transform_datn/transformed_ITViec.csv', index=False)

def transform_TopDev():
    with open("./transform_datn/TopDev.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        
    url_list = list(json_data.keys())

    data = []

    for url, extracted_data in json_data.items():
        transformed_data = {
            "url": url,
            "source": extracted_data['metadata']['source'],
            "crawl_date": extracted_data['metadata']['created_date']
        }

        transformed_data['company'] = {}
        transformed_data['job_detail'] = {}
        lines = extracted_data['text'].split('\n')

        #company_name
        
        transformed_data['company']['name'] = lines[1]
        transformed_data['company']['position'] = lines[2]
        
        transformed_data['job_detail']['name'] = lines[0]

        transformed_data['job_detail']['full_time'] = False
        transformed_data['job_detail']['part_time'] = False
        transformed_data['job_detail']['remote'] = False
        transformed_data['job_detail']['job_requirements_line'] = []
        transformed_data['job_detail']['year_of_exp'] = []
        transformed_data['job_detail']['job_level'] = []

        for job_level in job_level_list:
            if type(job_level) is dict:
                for level in list(job_level.values())[0]:
                    if level in transformed_data['job_detail']['name'].lower():
                        transformed_data['job_detail']['job_level'].append(job_level.keys()[0])
            elif type(job_level) is str:
                if job_level in transformed_data['job_detail']['name'].lower():
                    transformed_data['job_detail']['job_level'].append(job_level)

        previous_line = ''
        fl_skill_requirement = False

        for line in lines:
            line_lower = line.lower()

            #Job_requirement
            # if 'Yêu cầu kỹ thuật: ' in line:
            #     transformed_data['job_detail']['job_requirements'] = line.replace('Yêu cầu kỹ thuật: ', '').split(', ')
            
            # Fulltime, Parttime, Remote
            for keyword in full_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['full_time'] = True
            for keyword in part_time_keyword:
                if keyword in line_lower:
                    transformed_data['job_detail']['part_time'] = True
            if 'remote' in line_lower:
                transformed_data['job_detail']['remote'] = True
            
            if previous_line == 'Quy mô công ty':
                transformed_data['company']['size'] = line
            
            if line == "Phúc lợi dành cho bạn":
                fl_skill_requirement = False
            if fl_skill_requirement == True:
                if 'years old' in line or 'tuổi' in line:
                    continue
                transformed_data['job_detail']['job_requirements_line'].append(line)
                for year_of_exp in year_of_exp_list:
                    if year_of_exp in line_lower:
                        transformed_data['job_detail']['year_of_exp'].append(line)
                        break
            if line == 'Kỹ năng & Chuyên môn':
                fl_skill_requirement = True

            previous_line = line
            
        data.append(transformed_data)
        # break

    df_dictionary = pd.DataFrame([{
        "url": job['url'],
        "source": job['source'],
        "crawl_date": job['crawl_date'],
        "company_name": job['company']['name'],
        "company_position": job['company']['position'],
        "company_size": job['company']['size'],
        "job_detail_name": job['job_detail']['name'],
        # "job_detail_salary":job['job_detail']['salary'],
        "job_detail_full_time": job['job_detail']['full_time'],
        "job_detail_remote": job['job_detail']['remote'],
        "job_detail_hybrid": job['job_detail']['part_time'],
        # "job_detail_job_requirements": job['job_detail']['job_requirements'],
        "job_detail_job_requirements_line": job['job_detail']['job_requirements_line'],
        "job_detail_year_of_exp": job['job_detail']['year_of_exp'],
        "job_detail_job_level": job['job_detail'].get('job_level'),
    } for job in data])
    df = pd.DataFrame.from_dict(df_dictionary)
    df.to_csv('./transform_datn/extracted_TopDev.csv', index=False)

    def extract_year(year_exp):
        matches = re.findall(pattern, year_exp)
        # print(pattern)
        res = []
        for match in matches:
            res.append(match[0] + ' ' + match[1])
        return res

    def get_the_experience(list_string):
        tmp_list_string = [extract_year(string) for string in list_string]
        while len(tmp_list_string) != 0:
            if len(tmp_list_string[0]) == 0:
                tmp_list_string.pop(0)
            else:
                break
        if len(tmp_list_string) == 0:
            return None
        first_line_experience = tmp_list_string[0]
        while len(first_line_experience) != 0:
            if re.search(r'\d+', first_line_experience[0]) is None:
                first_line_experience.pop(0)
            else:
                break
        if len(first_line_experience) == 0:
            return None
        number = int(re.findall(r'\d+', first_line_experience[0])[0])
        if 'tháng' in first_line_experience[0] or \
            'month' in first_line_experience[0] or \
            'months' in first_line_experience[0]:
            number = float(number/12)
        return number

    df['job_detail_year_of_exp'] = df['job_detail_year_of_exp'].apply(get_the_experience)

    df['job_detail_job_level'] = df['job_detail_job_level'].map(lambda x: None if len(x) == 0 else x[-1])

    # build tree
    f = open("transform_datn/skill_list.txt", "r")
    skill_list = list(f)
    trie_directory = '/trie_struture'
    skill_list = [x.lower() for x in skill_list]

    # for x in df['job_detail_job_requirements']:
    #     skill_list.extend(x)

    skill_list = list(set(skill_list))

    file = open('transform_datn/skill_list.txt','w')
    for skill in skill_list:
        file.write(skill.replace('\n', '').rstrip()+"\n")
    file.close()

    trie = Trie()
    for skill in skill_list:
        trie.insert(skill)

    def extract_skill(lines):
        res = []
        for line in lines:
            res.extend(search_in_trie(trie, line))
        return res

    df['job_detail_extracted_skill'] = df['job_detail_job_requirements_line'].apply(extract_skill)

    # build tree
    f = open("transform_datn/job_role.txt", "r")
    job_role_list = list(f)
    trie_directory = '/trie_struture'
    job_role_list = [x.lower() for x in job_role_list]

    job_role_list = list(set(job_role_list))

    trie_job_role = Trie()
    for job_role in job_role_list:
        trie_job_role.insert(job_role)

    def extract_job_role(line):
        res = []
        res.extend(search_in_trie(trie_job_role, line.lower()))
        return res[0] if len(res)!=0 else None

    df['job_detail_extracted_job_role'] = df['job_detail_name'].apply(extract_job_role)

    df.to_csv('transform_datn/transformed_TopDev.csv', index=False)