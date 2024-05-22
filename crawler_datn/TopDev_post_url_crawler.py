import requests
import time
import json
from datetime import datetime

post_dict = {}
url_list = []
cnt = 0
for i in range(100):
    url = f'https://api.topdev.vn/td/v2/jobs?fields[job]=extra_skills,skills_arr,job_types_str,job_levels_str,job_levels_arr,detail_url,job_url,salary,requirements_arr&page={i+1}&locale=vi_VN&ordering=jobs_new'

    response = requests.get(url)
    print(i, end=' ')
    if response.status_code == 200:
        json_data = response.json()
        data = json_data['data']
        lengnth = len(post_dict.keys())
        for post in data:
            url_list.append(post['detail_url'])
            post['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            post['source'] = "TopDev" 
            post_dict[post['detail_url']] = post
        url_list = list(set(url_list))
        print(len(url_list), end=' ')
        if len(post_dict.keys()) == lengnth:
            cnt += 1
        else:
            cnt = 0
        if cnt == 5:
            break
        
    else:
        print('Failed to retrieve data from API:', response.status_code)
    time.sleep(2)
    print('Done')
    # break

json_file_path = "./crawler_datn/TopDev_ver02.json"

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(post_dict, json_file, ensure_ascii=False, indent=4)