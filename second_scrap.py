from time import sleep
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from pandas import DataFrame as df
from random import randint


new_price_col = 'price0705'


def is_trader(row):
    # check to see if the advisor is a trader
    # private = 0
    # trader = 1
    try:
        str = (row.find_elements(By.CSS_SELECTOR, "button[class='contact-seller-btn'"))[-1].text
        if str == 'הצגת מספר טלפון':
            return False
    except Exception as e:
        return True
    return False


def get_element_by_xpath(row, xpath):
    # gets a driver type row, xpath.
    # returns text value inside the element.
    # if element is not found or empty return None.
    try:
        tmp = row.find_element(By.XPATH, xpath).text
    except Exception as e:
        print('unable to scrap ' + xpath)
        tmp = None
    return tmp


def scrap_page(data, driver):
    # function scraps from given driver
    # fills new price column in the data
    # returns data frame with new price column filled
    is_blocked_flag = False
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "div[class='feeditem table'")
    except:
        is_blocked_flag = True
    try:
        counter = 0
        for row in rows:
            driver.execute_script(f"window.scrollTo(0, {row.location['y']})")
            row.click()
            if is_trader(row):
                continue
            # search for ad_number
            try:
                curr_ad_num = (
                    float((row.find_elements(By.CSS_SELECTOR, "span[class='num_ad'"))[-1].text.split(' ')[-1]))
                # if ad number is found, take its price and inset to the new price col
                if curr_ad_num in data.ad_num.values:
                    print(f'curr ad num is: {curr_ad_num}, is in data: {curr_ad_num in data.ad_num.values}')
                    # price handle
                    p = get_element_by_xpath(row, f'// *[ @ id = "feed_item_{counter}_price"]')
                    if p == 'לא צוין מחיר':
                        p = None
                    if p is not None:
                        p = int(p.split(' ')[0].replace(',', ''))
                    data.at[data[data.ad_num == curr_ad_num].index.to_list()[0], new_price_col] = p
                else:
                    print('not in df')
            except:
                is_blocked_flag = True
            counter += 1
    except Exception as e:
        is_blocked_flag = False

    return data, is_blocked_flag


def find_rameining_years(model, data):
    # find the remaining years
    year_data = data[(data[new_price_col].isnull()) & (data.model == model)]
    print(year_data)

    years = []
    for index, row in year_data.iterrows():
        if row.year not in years:
            years.append(row.year)
    return years


def load_page_elements(driver):
    # ---------------------------------------- get selenium elements -------------------------------
    try:
        # close the small disturbing window if needed
        driver.find_element(By.XPATH,
                            '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[1]/button/i').click()
    except Exception as e:
        pass

    # find car dropdown button
    dropdown_car_nemu = driver.find_element(By.XPATH,
                                            '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[1]/div/div/div[2]/i')

    # find the model dropdown button
    models_drop_down = driver.find_element(By.XPATH,
                                           '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[2]/div/div/div[2]/i')

    # get car scrolling list to choose car company from
    cars = driver.find_elements(By.CSS_SELECTOR, "span[class='cb_text'")

    # open car menu to choose car from
    dropdown_car_nemu.click()

    # find the search button
    search_buton = driver.find_element(By.XPATH,
                                       '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[7]/button')

    try:
        # find the next page button
        next_page = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[6]/div[2]/div[5]/a[2]')
    except:
        next_page = None
        print('only one page exist')

    return dropdown_car_nemu, models_drop_down, cars, search_buton, next_page


def scrap_area(company, models, data):
    # undetected webdriver to avoid blocks
    driver = uc.Chrome()

    url = f"https://www.yad2.co.il/vehicles/cars"
    driver.get(url)

    try:
        # close the small disturbing window
        driver.find_element(By.XPATH,
                            '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[1]/button/i').click()
    except:
        print('there is no win')

    dropdown_car_nemu, models_drop_down, cars, search_buton, next_page = load_page_elements(driver)

    # page counter indicator
    page_counter = 0

    # reference for nulls before of the scrap
    print(f'num of null in price new col: {data[new_price_col].isnull().sum()} ')

    try:
        # close the small disturbing window if needed
        driver.find_element(By.XPATH,
                            '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[1]/button/i').click()
    except Exception as e:
        pass

    try:
        # check the company check box
        for car in cars:
            if car.text == company:
                car.click()
                print(f'text = {car.text}')
                break
        sleep(1)
    except:
        is_blocked_flag = True
    sleep(2)

    search_buton.click()
    sleep(randint(1,4))

    company_url = driver.current_url
    dropdown_car_nemu, models_drop_down, cars, search_buton, next_page = load_page_elements(driver)

    print(models)



    # run the car models to get the info
    for model in models:
        years = find_rameining_years(model, data)
        driver.get(company_url)
        dropdown_car_nemu, models_drop_down, cars, search_buton, next_page = load_page_elements(driver)

        try:
            # close the small disturbing window if needed
            driver.find_element(By.XPATH,
                                '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[1]/button/i').click()
        except Exception as e:
            pass

        print(model)
        print(f'years to scrap: {years}')

        # --------------------------------- select specific car model ---------------------------------
        # open models drop down bar for the first time
        try:
            driver.execute_script(f"window.scrollTo(0, {models_drop_down.location['y']})")
            models_drop_down.click()
            print('clicked dropdown menu')
        except:
            print('cannot click dropdown menu')
        sleep(randint(1, 5))
        try:
            # find specific model in the dropdown list and murk it
            model_elements = driver.find_elements(By.CSS_SELECTOR, "span[class='cb_text'")
            for element in model_elements:
                if element.text == model:
                    model_element = element
            sleep(randint(2,5))
            print('found model name')
        except:
            print('cannot find model name')
        try:
            model_element.click()
            print('model name checked')
        except:
            print('cannot check model name')
        sleep(randint(1, 3))

        search_buton.click()
        sleep(randint(3, 5))

        # save url with model
        model_url = driver.current_url

        for year in years:
            # select the year
            try:
                print(f'model url is: {model_url}')
                with_year_url = f'{model_url}&year={year}-{year}&priceOnly=1'
                print(f'url with year: {with_year_url}')
                driver.get(with_year_url)
                sleep(1)
                if (driver.current_url != with_year_url):
                    print(f'problem accured in {year}.')
                    continue
                # reload page element
                dropdown_car_nemu, models_drop_down, cars, search_buton, next_page = load_page_elements(driver)
            except Exception as e:
                print(e)

            data, is_blocked_flag = scrap_page(data, driver)  # scrap the page for new price according to date
            print(f'num of null in price new col: {data[new_price_col].isnull().sum()} ')    # visualize the nulls left

            page_counter += 1

            if next_page == None:
                next_page_exist = False
            else:
                next_page_exist = True     # flag for page


            # scrap pages until there are none
            while next_page_exist and not is_blocked_flag:
                try:
                    driver.execute_script(f"window.scrollTo(0, {next_page.location['y']})")
                    url = next_page.get_attribute('href')
                    print(url)
                    sleep(randint(1, 5))
                    next_page.click()
                    sleep(2)
                    page_counter += 1
                except:
                    # if nexp page button is no clickable there are no pages
                    next_page_exist = False
                if next_page_exist == False:
                    break
                try:
                    data, is_blocked_flag = scrap_page(data, driver)
                    print(f'num of null in price new col: {data[new_price_col].isnull().sum()} ')
                except:
                    # if blocked, rais an exception and break.
                    print(f'could not scrap page {page_counter} in area {company}')
                    is_blocked_flag = True
                print(f'company = {company}, model = {model}, year = {year} , page = {page_counter} succeed')
            data.to_csv('./data/cars_data0705.csv', encoding="utf-8")

            try:
                driver.execute_script(f"window.scrollTo(0, {models_drop_down.location['y']})")
                if is_blocked_flag == False:
                    # fill the new prices that not found with -1
                    print(f'model and year nulls = {data[(data.model == model) & (data.year == year)][new_price_col].isnull().sum()}')
                    data.loc[data[(data[new_price_col].isnull()) & (data.model == model) & (data.year == year)].index, [new_price_col]] = -1
                    print(f'model and year nulls = {data[(data.model == model) & (data.year == year)][new_price_col].isnull().sum()}')
                    print(f'AFTER FILL IN THE MISSING VALUES num of null in price new col: {data[new_price_col].isnull().sum()}')
                    # save the dataframe progress to csv
                    data.to_csv('./data/cars_data0705.csv', encoding="utf-8")
                sleep(2)
            except:
                is_blocked_flag = True
                print('failed to scroll page at the end of year scrap')
            if is_blocked_flag:
                print('blocked')
                random_wait = randint(200, 500)
                print(f'big wait after detection {random_wait} seconds')
                sleep(random_wait)
                driver.get(f"https://www.yad2.co.il/vehicles/cars")
                sleep(2)
                driver.get(url)
                is_blocked_flag = False
                data, is_blocked_flag = scrap_page(data, driver)
        # model uncheck
        try:
            sleep(randint(1,3))
            models_drop_down.click()
        except:
            print('can not click dropdown list to close it')
        try:
            sleep(randint(1,5))
            model_element.click()
        except:
            print('can not click dropdown element to uncheck it')

    # close the driver
    driver.close()
    return data

# first iteration
# data = pd.read_csv('./data/clean_data0105.csv', index_col=0)
# data[new_price_col] = None

# after block iteration
data = pd.read_csv('./data/cars_data0705.csv', index_col=0)

# check only for data not scrapped
scrapping_data = data[data[new_price_col].isnull()]

car_dict = {}
for index, row in scrapping_data.iterrows():
    try:
        if row.model not in car_dict[row.company]:
            car_dict[row.company].append(row.model)
    except Exception as e:
        car_dict[row.company] = []

keys_to_delet = []
for key in car_dict:
    if car_dict[key] == []:
        keys_to_delet.append(key)
for key in keys_to_delet:
    del car_dict[key]

# print for reference
print(car_dict)

for company in car_dict:
    data = scrap_area(company, car_dict[company], data)
    time_out = randint(100, 200)
    print(f'random timeout between company scrap: {time_out}')
    sleep(time_out)


print('haleluya')
