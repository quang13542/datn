from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle

driver = webdriver.Chrome()

driver.get("https://itviec.com/it-jobs")
count = 0
page_count = 1
page_list = []
url_list = []
while True:
    print(f'loop_{count}')
    fl=False
    for id in range(20):
        try:
            job_post = driver.find_element(
                By.XPATH,
                f"/html/body/main/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[{id+1}]"
            )
            count+=1
            fl=True
            url_list.append(
                job_post.get_attribute('data-search--job-selection-job-url-value')
            )
        except:
            break
    if fl == False:
        break
    try:
        page_count += 1
        driver.quit()
        driver = webdriver.Chrome()
        driver.get(f'https://itviec.com/it-jobs?page={page_count}&query=&source=search_job')
        time.sleep(5)
        page_list.append(page_count)
        print(page_count)
    except:
        break

# print(url_list)

with open("./crawler_datn/ITViec_list_url", "wb") as fp:
    pickle.dump(url_list, fp)

driver.quit()
