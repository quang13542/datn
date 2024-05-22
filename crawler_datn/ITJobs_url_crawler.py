from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle

MAX_CLICK = 1500

driver = webdriver.Chrome()

driver.get("https://www.itjobs.com.vn/vi")
count = 0
page_list = []
url_list = []

while count<MAX_CLICK:
    count += 1
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000)")
        button = driver.find_element(By.ID, 'btnShowMoreJob')
        button.click()
        time.sleep(1)
    except:
        break
list_post = driver.find_elements(By.CLASS_NAME, 'jp_job_post_link')

url_list.extend([post.get_attribute('href') for post in list_post])

# print(url_list)

with open("./crawler_datn/ITjobs_list_url", "wb") as fp:
    pickle.dump(url_list, fp)

# driver.get(url_list[0])
# time.sleep(100)
driver.quit()
