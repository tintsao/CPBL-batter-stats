# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
import csv
import os
import pandas as pd


# %% [markdown]
# ### 匯入 Selenium 的核心瀏覽器控制模組（webdriver）
# 需要這個才能打開 Chrome、控制點擊、輸入、截圖等動作。  

# %%
service = Service("/Users/tintsao/Desktop/chromedriver-mac-arm64/chromedriver")

# 指定你自己的 ChromeDriver 路徑
driver = webdriver.Chrome(service=service)

# %%
# 打開網站
url = "https://www.cpbl.com.tw"
driver.get(url)
# print(driver.title)
driver.find_element(By.XPATH, '//*[@id="Menu"]/div/ul/li[6]/a').click()
driver.find_element(By.XPATH, '//*[@id="Menu"]/div/ul/li[6]/ul/li[1]/a').click()
driver.find_element(By.XPATH, '//*[@id="PageListContainer"]/div/div[10]/div/div[3]/a').click()
# driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[2]/select').click() 
# driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[2]/select/option[5]').click() # 2022
driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[3]/select').click()
driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[3]/select/option[2]').click()
driver.find_element(By.CLASS_NAME, 'sort_type').click()

# %%
# 開啟 CSV 一次寫入全部
headers = []
for i in range(1, 3): 
    xpath = f'//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[1]/th[1]/div/div[{i}]'
    try:
        element = driver.find_element(By.XPATH, xpath)
        headers.append(element.text.strip())
    except Exception as e:
        headers.append("") 
    
for i in range(2, 29):
    xpath = f'//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[1]/th[{i}]'
    try:
        element = driver.find_element(By.XPATH, xpath)
        headers.append(element.text.strip())
    except:
        headers.append("")  # 沒抓到就空白佔位

# print(headers)
# print("路徑：", os.path.abspath("中職對戰2020~2022.csv"))

# %%
# 抓 title 屬性的球隊
team_xpath = '//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[2]/td[1]/div/div[2]/span[1]/a'
team = driver.find_element(By.XPATH, team_xpath).get_attribute("title")

# 抓名字
name_xpath = '//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[2]/td[1]/div/div[2]/span[2]'
name = driver.find_element(By.XPATH, name_xpath).text.strip()

print(f"{team}：{name}")

headers = ["年份"] + headers  # 把"年份"加在最前面
headers[1] = "隊伍"  # 原本的排名那欄改名為隊伍

# %% [markdown]
# ### 抓取 2020~2025 的野手資料

# %%
all_data = []

year_list = [2025, 2024, 2023, 2022, 2021, 2020]

for year_index, year in zip(range(1, 7), year_list):

    # 點選年份下拉
    dropdown = driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[2]/select')
    dropdown.click()
    time.sleep(0.5)
    option_xpath = f'//*[@id="bindVue"]/div/div[2]/select/option[{year_index + 1}]'
    driver.find_element(By.XPATH, option_xpath).click()
    driver.find_element(By.XPATH, '//*[@id="bindVue"]/div/div[6]/input').click()
    time.sleep(0.5)  # 等頁面刷新

    # 翻頁
    while True:
        rows = driver.find_elements(By.XPATH, '//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr')

        for row in range(2, len(rows)+1):
            try:
                team_xpath = f'//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[{row}]/td[1]/div/div[2]/span[1]/a'
                team = driver.find_element(By.XPATH, team_xpath).get_attribute("title")

                name_xpath = f'//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[{row}]/td[1]/div/div[2]/span[2]'
                name = driver.find_element(By.XPATH, name_xpath).text.strip()

                stats = []
                for col in range(2, 29):
                    stat_xpath = f'//*[@id="PageListContainer"]/div[1]/div/table/tbody/tr[{row}]/td[{col}]'
                    stat = driver.find_element(By.XPATH, stat_xpath).text.strip()
                    stats.append(stat)

                data_row = [2026 - (year_index), team, name] + stats  # 推出對應年份：2022 → 2021 → 2020
                all_data.append(data_row)

            except:
                continue

        # 嘗試翻頁
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(text(), "下一頁")]')
            if "disabled" in next_button.get_attribute("class"):
                break
            else:
                next_button.click()
                time.sleep(1.5)
        except:
            break

# %%
time.sleep(1)
driver.quit()

# %%
print(len(all_data))
# print(all_data)

# %%
# 寫入 CSV
with open("中職野手2020~2025.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(all_data)      # 寫入所有資料列
    
df = pd.read_csv("中職野手2020~2025.csv", encoding="utf-8-sig")
df

# %%
df.to_csv("中職野手2020~2025.csv", index=False, encoding="utf-8-sig")


