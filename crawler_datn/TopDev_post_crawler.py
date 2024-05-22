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

with open("./crawler_datn/TopDev_list_url", "rb") as fp:
    url_list = pickle.load(fp)

with open("./crawler_datn/TopDev.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

crawled_url_list = json_data.keys()

url_list = [url for url in url_list if url not in crawled_url_list]

print(len(url_list))

count=0
for url in url_list:
    try:
        count+=1
        print(count)
        driver = webdriver.Chrome()

        driver.get(url)
        time.sleep(1)

        content = driver.find_element(
            By.XPATH,
            '/html/body/section/div/div'
        )
        cleaned_text = content.text


        driver.quit()
        metadata = {"source": "TopDev", "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        json_data[url] = {"text": cleaned_text, "metadata": metadata}
        # print(json_data[url]['text'])
        # break
    
    except:
        print(url)
        continue

json_file_path = "./crawler_datn/TopDev.json"

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)