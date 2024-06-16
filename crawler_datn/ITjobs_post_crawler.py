from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
import time
from selenium.webdriver.common.by import By
from datetime import datetime
import json
from tqdm import tqdm

def crawl_ITjobs_post():
    json_file_path = "./crawler_datn/ITjobs.json"
    existing_list = []
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        print(type(data))
    existing_list = data.keys()

    with open("./crawler_datn/ITjobs_list_url_ver2", "rb") as fp:
        url_list = pickle.load(fp)
    url_list = [i for i in url_list if i not in existing_list]
    print(len(url_list))

    json_data = {}

    count = 0

    for url in tqdm(url_list):
        try:
            # count += 1
            # print(count, len(url_list))
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

    

    with open("./crawler_datn/ITjobs_ver2.json", "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)