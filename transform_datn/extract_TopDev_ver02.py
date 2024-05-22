import json
import pandas as pd

full_time_keyword = ['toàn thời gian', 'full time', 'full-time', 'full_time']
part_time_keyword = ['bán thời gian', 'part time', 'part-time', 'part_time']
job_level_list = ['intern', 'fresher', 'junior', 'senior']
year_of_exp_list = ['years', 'year', 'năm kinh nghiệm']

extracted_field_list = [
    "skills_arr",
    "job_types_str",
    "job_levels_arr",
    "detail_url",
    "salary.min",
    "salary.max",
    "requirements_arr.value"
]

with open("./transform_datn/TopDev_ver02.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

for post_url in json_data.keys():
    job_detail_job_requirements = json_data[post_url]['skill_arr']