# Lan 1:3h58p - 1178/3241 url
# Lan 2:3h02p - 2094/3241 url
# Lan 3:2h21p - 2737/3241 url

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pickle
import time
from datetime import datetime
import json

with open("TopCV_list_url", "rb") as fp:
    url_list = pickle.load(fp)

try:
    with open("TopCv_ver02.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
except:
    json_data = {}

crawled_url_list = json_data.keys()

url_list = [url for url in url_list if url not in crawled_url_list]

print(len(url_list))
json_file_path = "TopCv_ver02.json"
count=0
for url in url_list:
    try:
        count+=1
        print(count)
        driver = webdriver.Chrome()

        driver.get(url)
        time.sleep(1)
        content = driver.find_element(By.CLASS_NAME, 'job-detail__body')
        text = content.text

        text= '\n'.join(line for line in text.split('\n') if line.strip())

        # start_index = text.find('Phân tích mức độ phù hợp của bạn với công việc')

        # if start_index != -1:
        #     cleaned_text = text[:start_index]
        # else:
        #     cleaned_text = text

        driver.quit()
        metadata = {"source": "TopCv", "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        json_data[url] = {"text": text, "metadata": metadata}
    except:
        print(url)
        continue

    if count % 100 == 0:
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)