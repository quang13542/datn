from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle

def crawl_TopCV_url():
    driver = webdriver.Chrome()

    driver.get("https://www.topcv.vn/viec-lam-it")
    count = 0
    page_count = 1
    page_list = []
    url_list = []
    while True:
        print(f'loop_{count}')
        fl=False
        for id in range(50):
            try:
                job_post = driver.find_element(
                    By.XPATH,
                    f"//*[@id='main']/div[1]/div[3]/div[4]/div[1]/div[1]/div[{id+1}]/div/div[1]/a"
                )
                count+=1
                fl=True
                url_list.append(
                    job_post.get_attribute('href')
                )
            except:
                break
        if fl == False:
            break
        try:
            page_count += 1
            driver.quit()
            driver = webdriver.Chrome()
            driver.get(f'https://www.topcv.vn/viec-lam-it?page={page_count}')
            time.sleep(5)
            page_list.append(page_count)
            print(page_count)
        except:
            break

    # print(url_list)

    with open("./crawler_datn/TopCV_list_url", "wb") as fp:
        pickle.dump(url_list, fp)

    driver.quit()
