import json
import pandas as pd

full_time_keyword = ['toàn thời gian', 'full time', 'full-time', 'full_time']
part_time_keyword = ['bán thời gian', 'part time', 'part-time', 'part_time']
job_level_list = ['intern', 'fresher', 'junior', 'senior']
year_of_exp_list = ['years', 'year', 'năm kinh nghiệm']

with open("ITjobs.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)
    
url_list = list(json_data.keys())

print(url_list[0])

data = []

for url, extracted_data in json_data.items():
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
            # print(transformed_data['job_detail']['job_requirements'])
        
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
print(len(data))
print(data[0])
for job in data:
    print(job['job_detail']['name'], job['job_detail']['salary'])


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
print(data[889]['job_detail'].get('job_level'))
print(df.info())
df.to_csv('extracted_ITjobs.csv', index=False)