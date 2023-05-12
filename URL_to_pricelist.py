import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd

# for the start we will use the original scrapped data
# data = pd.read_csv('./data/cars_data0105.csv')

# to avoid data loss during scrapping we will save once we detected.
# then we will return to scrap from the same position from the new file.
data = pd.read_csv('./data/full_car_data0105.csv', index_col=0)

# print(data)

urls_to_convert = data[data.price_list.isnull()].index.to_list()
print(len(urls_to_convert))

driver = uc.Chrome()

for url in urls_to_convert:
    print(url)
    driver.get(data['price_list_url'][url])
    try:
        price_list = driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[1]/div/div/div[2]/div[2]/div/div[2]/span/span').get_attribute("innerHTML")
        price_list = int(price_list.split(' ', maxsplit=1)[1].replace(',', '').replace(' ',''))
        data.at[url, 'price_list'] = price_list
    except Exception as e:
        try:
            # this element should be in the page if we are not detected
            # if this element is in page, then leave the price list to be None
            is_detected = driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div/div[1]/ul/li[1]/a')
        except:
            try:
                # should detect page not found error
                is_detected = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div/div/h2')
            # final error exception for selenium detection
            except:
                # this print is for debug to locate other reasons then being detected.
                print(data['price_list_url'][url])
                print('detected')
                break
        # push -1 as a flag to none price list car
        data.at[url, 'price_list'] = -1

driver.close()

data.to_csv('./data/full_car_data0105.csv')
