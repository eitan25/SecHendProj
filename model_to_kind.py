from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd


def get_elements(dropdown_nemu, driver):
    # print('func get_elements___________________________')
    dropdown_nemu.click()
    sleep(1)
    elems = driver.find_elements(By.CSS_SELECTOR, "span[class='cb_text'")
    car_dict = {}
    for elem in elems:
        if elem.text != '':
            car_dict[elem.text] = elem
    # print(car_dict)
    print('end of get_elements___________________________')
    return car_dict

# first scrap
data = pd.read_csv('./data/clean_cars1605.csv', index_col=0)
# next
# data = pd.read_csv('clean_cars1605.csv', index_col=0)

# data = data[data.car_kind.isnull()].copy()
company_list = data['company'].value_counts().keys().to_list()
car_dict = {}
for company in company_list:
    model_list = data[data.company == company].model.value_counts().keys().to_list()
    car_dict[company] = model_list

# undetected webdriver to avoid blocks
driver = uc.Chrome()
url = 'https://www.yad2.co.il/vehicles/cars?area=2'
driver.get(url)

# open relevant sections
car_kind_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[2]/ul/li[2]/label/span')
car_kind_button.click()
sleep(1)
advanced_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[5]/div/div[1]/div/button/span/span')
advanced_button.click()
sleep(1)

dropdown_kind = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[1]/div/div/div[2]/i')

dropdown_car_nemu = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[4]/div/div/div[2]/i')

dropdown_model_menu = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[5]/div/div[2]/div/ul[1]/li[1]/div/div/div[2]/i')

driver.execute_script(f"window.scrollTo(0, {car_kind_button.location['y']})")

data['car_kind'] = None

dropdown_kind.click()
sleep(1)
kinds = driver.find_elements(By.CSS_SELECTOR, "span[class='text'")
kinds_text = ['קרוסאוברים', 'משפחתיים' , 'יוקרה', "ג'יפים", 'קטנים', 'מיניוואנים', 'מנהלים', 'ספורט', 'מסחריים', 'טנדרים']
kind_dict = {}
for elem in kinds:
    kind_name = elem.text
    if kind_name in kinds_text:
        kind_dict[kind_name] = elem
# print(kind_dict)

# remove any scraped model from dict values, if no models in company, remove the key as well

for kind in kinds_text:
    kind_dict[kind].click()
    sleep(1)
    car_elems_dict = get_elements(dropdown_car_nemu, driver)
    # print('create dictionary of elements')
    # print(car_elems_dict.keys())

    for car in car_dict:
        # check the car company component
        sleep(1)
        try:
            car_elems_dict[car].click()
        except Exception as e:
            print(e)
            continue
        sleep(1)
        model_dict = get_elements(dropdown_model_menu, driver)
        # uncheck the car company component
        dropdown_car_nemu.click()
        sleep(1)
        car_elems_dict[car].click()
        sleep(1)
        model_list = list(model_dict.keys())
        print(model_list)
        for model in car_dict[car]:
            if model in model_list:
                data.loc[(data.model == model), ['car_kind']] = kind
                data.to_csv('clean_cars1605.csv')
    dropdown_kind.click()
    sleep(1)
    kind_dict[kind].click()
    sleep(1)

print(data.car_kind)

driver.close()

