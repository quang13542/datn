# 50 phut

from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
import time
from datetime import datetime
import json

with open("./crawler_datn/ITViec_list_url", "rb") as fp:
    url_list = pickle.load(fp)

json_data = {}

for url in url_list:
    try:
        driver = webdriver.Chrome()

        # url = 'https://itviec.com/it-jobs/security-consultant-cloud-fpt-software-5619?lab_feature=preview_jd_page'
        driver.get(f'https://itviec.com{url}')
        time.sleep(2)

        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        header_elements = soup.find_all(['head', 'header'])
        for header in header_elements:
            header.decompose()

        footer_elements = soup.find_all('footer')
        for footer in footer_elements:
            footer.decompose()

        html_without_header_footer = soup.prettify()
        soup_without_header_footer = BeautifulSoup(html_without_header_footer, 'html.parser')

        text = soup_without_header_footer.get_text()

        cleaned_text_without_header_footer = '\n'.join(line for line in text.split('\n') if line.strip())

        start_index = cleaned_text_without_header_footer.find('More jobs for you')

        if start_index != -1:
            cleaned_text = cleaned_text_without_header_footer[:start_index]
        else:
            cleaned_text = cleaned_text_without_header_footer

        driver.quit()

        metadata = {"source": "ITViec", "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        json_data[url] = {"text": cleaned_text, "metadata": metadata}
        
    except:
        print(url)
        continue

json_file_path = "./crawler_datn/ITViec.json"

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)