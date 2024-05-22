import json
import pandas as pd

full_time_keyword = ['toàn thời gian', 'full time', 'full-time', 'full_time']
job_level_list = [{'intern': ['thực tập sinh', 'intern', 'thực tập']}, 'fresher', 'junior', 'senior']
year_of_exp_list = ['years', 'year', 'năm kinh nghiệm']

with open("./transform_datn/ITViec.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)
    
url_list = list(json_data.keys())

# print(url_list[0])
print(json_data[url_list[1]]['text'])
# print(url_list[1])
# print('\n\n\n')

data = []

for url, extracted_data in json_data.items():
    
    # print(url)
    # print(extracted_data.keys())
    # print(extracted_data['metadata'])
    # print(extracted_data['text'])
    transformed_data = {
        "url": url,
        "source": extracted_data['metadata']['source'],
        "crawl_date": extracted_data['metadata']['created_date']
    }

    transformed_data['company'] = {}
    transformed_data['job_detail'] = {}
    lines = extracted_data['text'].split('\n')
    lines = [line.lstrip() for line in lines]
    # for line in lines:
    #     print(line)
    

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
print(len(data))
print(data[0])


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
print(data[889]['job_detail'].get('job_level'))
print(df.info())
df.to_csv('./transform_datn/extracted_ITViec.csv', index=False)