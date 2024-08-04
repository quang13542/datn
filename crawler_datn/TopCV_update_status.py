from selenium import webdriver
import time
from datetime import datetime
from tqdm import tqdm
import pickle
from selenium.webdriver.common.by import By
import json
from selenium.common.exceptions import NoSuchElementException

def update_TopCV_status():
    with open("./crawler_datn/TopCV_list_url", "rb") as fp:
        url_list = pickle.load(fp)
    with open("./crawler_datn/invalid_date.json", "r", encoding="utf-8") as json_file:
        invalid_date = json.load(json_file)
        invalid_url_list = list(invalid_date.keys())
        count=0
    for url in tqdm(url_list):
        # url = 'https://www.topcv.vn/viec-lam/flutter-developer-senior/1298909.html?ta_source=ITJobs_LinkDetail'
        # try:
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1)

        try:
            element = driver.find_element(By.CLASS_NAME, 'job-detail__expired')
            invalid_url_list.append(url)
            invalid_date[url] = datetime.today().strftime('%m/%d/%Y')
            print(count)
            count += 1
        except NoSuchElementException:
            driver.quit()  
            continue

        driver.quit()            
        if count == 100:
            url_list = [url for url in url_list if url not in invalid_url_list]

            with open("./crawler_datn/ITjobs_list_url_ver2", "wb") as fp:
                pickle.dump(url_list, fp)
            with open("./crawler_datn/invalid_date.json", "w", encoding="utf-8") as json_file:
                json.dump(invalid_date, json_file, ensure_ascii=False, indent=4)
            count = 0
        # break
        # except:
        #     print(url)
        #     continue
    
    url_list = [url for url in url_list if url not in invalid_url_list]

    with open("./crawler_datn/TopCV_list_url", "wb") as fp:
        pickle.dump(url_list, fp)
    with open("./crawler_datn/invalid_date.json", "w", encoding="utf-8") as json_file:
        json.dump(invalid_date, json_file, ensure_ascii=False, indent=4)

