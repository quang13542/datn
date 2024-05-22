import json
import pandas as pd

full_time_keyword = ['toàn thời gian', 'full time', 'full-time', 'full_time']
part_time_keyword = ['bán thời gian', 'part time', 'part-time', 'part_time']
job_level_list = ['intern', 'fresher', 'junior', 'senior']
year_of_exp_list = ['years', 'year', 'năm kinh nghiệm']

with open("./transform_datn/TopCv_ver02.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)
    
url_list = list(json_data.keys())

# print(url_list[0])
# print(json_data[url_list[1]]['text'])
# print(url_list[1])
# print('\n\n\n')

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
# print(len(data))
# print(data[0])
# for job in data:
#     print(job['job_detail']['salary'])


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
df.to_csv('./transform_datn/extracted_TopCV.csv', index=False)