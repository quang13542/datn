from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import pickle

MAX_SCROLL = 800

for crawl_time in range(3):
    driver = webdriver.Chrome()

    driver.get("https://topdev.vn/viec-lam-it")
    count = 0
    # url_list = []
    with open("TopDev_list_url", "rb") as fp:
        url_list = pickle.load(fp)

    for count in tqdm(range(MAX_SCROLL)):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000)")
            time.sleep(1)
        except:
            break

    list_post = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div[1]/section/ul').find_elements(By.CLASS_NAME, 'block')

    for post in list_post:
        href = post.get_attribute('href')
        url_list.append(href)

    with open("TopDev_list_url", "wb") as fp:
        pickle.dump(url_list, fp)
    print(len(url_list))
    driver.quit()
