from selenium import webdriver
import time
from datetime import datetime
from tqdm import tqdm
import pickle
from selenium.webdriver.common.by import By
import json

def update_ITjobs_status():
    with open("./crawler_datn/ITjobs_list_url_ver2", "rb") as fp:
        url_list = pickle.load(fp)
    with open("./crawler_datn/invalid_date.json", "r", encoding="utf-8") as json_file:
        invalid_date = json.load(json_file)
        invalid_url_list = list(invalid_date.keys())

    url_list = [url for url in url_list if url not in invalid_url_list]

    count = 0
    for url in tqdm(url_list):
        # url = 'https://www.itjobs.com.vn/vi/job/81994/java-developer'
        try:
            driver = webdriver.Chrome()
            driver.get(url)
            time.sleep(1)

            apply_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div[4]/ul/li/a')
            text = apply_button.text

            driver.quit()
            if text == 'Hết hạn':
                invalid_url_list.append(url)
                invalid_date[url] = datetime.today().strftime('%m/%d/%Y')
                count += 1
            if count == 100:
                url_list = [url for url in url_list if url not in invalid_url_list]

                with open("./crawler_datn/ITjobs_list_url_ver2", "wb") as fp:
                    pickle.dump(url_list, fp)
                with open("./crawler_datn/invalid_date.json", "w", encoding="utf-8") as json_file:
                    json.dump(invalid_date, json_file, ensure_ascii=False, indent=4)
                count = 0
        except:
            print(url)
            continue
    
    url_list = [url for url in url_list if url not in invalid_url_list]

    with open("./crawler_datn/ITjobs_list_url_ver2", "wb") as fp:
        pickle.dump(url_list, fp)
    with open("./crawler_datn/invalid_date.json", "w", encoding="utf-8") as json_file:
        json.dump(invalid_date, json_file, ensure_ascii=False, indent=4)

