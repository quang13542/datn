from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
import time
from selenium.webdriver.common.by import By
from datetime import datetime
import json

with open("ITjobs_list_url", "rb") as fp:
    url_list = pickle.load(fp)

json_data = {}

count = 0

for url in url_list:
    try:
        count += 1
        print(count, len(url_list))
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1)

        content = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[1]/div')
        text = content.text

        cleaned_text = '\n'.join(line for line in text.split('\n') if line.strip())

        driver.quit()

        metadata = {"source": "ITjobs", "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        json_data[url] = {"text": cleaned_text, "metadata": metadata}

        
    except:
        print(url)
        continue

json_file_path = "ITjobs.json"

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)