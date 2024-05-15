# import requests
# from bs4 import BeautifulSoup

# # URL of the webpage you want to scrape
# url = 'https://www.topcv.vn/viec-lam/senior-business-analyst-co-kinh-nghiem-banking-finance/1288303.html?ta_source=ITJobs_LinkDetail'

# # Fetch the webpage content
# response = requests.get(url)

# if response.status_code == 200:
#     # Access the HTML content from the response
#     html_content = response.text
#     soup = BeautifulSoup(html_content, 'html.parser')
#     job_detail_element = soup.find(class_='job-detail')


#     # Get the modified HTML content without <script> tags
#     modified_html_content = str(job_detail_element)

#     # Print or further process the modified HTML content
#     print(modified_html_content)
# else:
#     print('Failed to fetch the webpage:', response.status_code)
import pickle
import json

with open("TopDev_list_url", "rb") as fp:
    url_list = pickle.load(fp)

with open("TopDev.json", "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

crawled_url_list = json_data.keys()

print(len(list(set(url_list))))

url_list = [url for url in url_list if url not in crawled_url_list]

print(len(url_list))
print(len(list(set(url_list))))
print(len(json_data.keys()))