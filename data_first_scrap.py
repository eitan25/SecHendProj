import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from pandas import DataFrame as df


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


def get_js_element_by_xpath(row, xpath):
    # gets a driver type row, xpath.
    # returns text value inside the element.
    # if element is not found or empty return None.
    try:
        tmp = row.find_elements(By.XPATH, xpath)[-1].text
    except Exception as e:
        print('unable to scrap ' + xpath)
        tmp = None
    return tmp


def ownership(owner):
    # encoding for owner :
    # private = 0
    # leasing = 1
    # rent = 2
    # company = 3
    # taxi = 4
    # driving lessons = 5
    # personal import = 6
    # parallel import = 7
    # governmental = 8
    # without prev ownership = 9
    if owner == 'פרטית':
        return 0
    if owner == 'ליסינג':
        return 1
    if owner == 'השכרה' or owner == 'השכרה / החכר':
        return 2
    if owner == 'חברה':
        return 3
    if owner == 'מונית':
        return 4
    if owner == 'לימוד נהיגה':
        return 5
    if owner == 'ייבוא אישי':
        return 6
    if owner == 'ייבוא מקביל':
        return 7
    if owner == 'ממשלתי' or owner == 'או"ם':
        return 8
    if owner == 'ללא רישום בעלות קודמת':
        return 9
    return None


def gear_kind(gearbox):
    # encoding for gearbox kind:
    # automatic = 0, manual = 1, tiptronic = 2, robotic = 3
    if gearbox == 'אוטומט':
        return 0
    if gearbox == 'ידנית':
        return 1
    if gearbox == 'טיפטרוניק':
        return 2
    if gearbox == 'רובוטית':
        return 3
    return None


def handle_color(param):
    # get from a string only the color.
    try:
        color = param.split(' ')[0]
        return color
    except:
        pass
    return None


def enc_eng_kind(eng_king):
    # get from a string the engine kind and encode it:
    # gas = 0
    # hybrid elc/diesel = 1
    # electric = 2
    # hybrid elc/benzine = 3
    # gas/benzine = 4
    # turbo diesel = 5
    # diesel = 6
    # benzine = 7
    if eng_king == 'גט"ד':
        return 0
    if eng_king == 'היברידי חשמל / דיזל':
        return 1
    if eng_king == 'חשמלי':
        return 2
    if eng_king == 'היברידי חשמל / בנזין':
        return 3
    if eng_king == 'גט"ד / בנזין' or eng_king == 'גפ"ם  / בנזין':
        return 4
    if eng_king == 'טורבו דיזל':
        return 5
    if eng_king == 'דיזל':
        return 6
    if eng_king == 'בנזין':
        return 7
    return None


def is_trader(row):
    # check to see if the advisor is a trader
    # private = 0
    # trader = 1
    try:
        str = (row.find_elements(By.CSS_SELECTOR, "button[class='contact-seller-btn'"))[-1].text
        if str == 'הצגת מספר טלפון':
            return 0
    except Exception as e:
        return 1
    return None


def get_car_list(driver):
    # return all the car company name as a list.
    destraction = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/div/div/div/div[1]/button/i')
    destraction.click()
    dropdown_car_nemu = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div/div[4]/div[4]/div/div/form/ul/li[1]/div/div/div[2]/i')
    dropdown_car_nemu.click()
    cars = driver.find_elements(By.CSS_SELECTOR, "span[class='cb_text'")
    car_list = []
    for car in cars:
        if car.text != '':
            car_list.append(car.text)
    return car_list


def handle_company_and_model(row, title_url, car_list):
    try:
        title_text = row.find_element(By.XPATH, title_url).text
        for car in car_list:
            if car in title_text:
                company = car
                break
        model = title_text.replace(company,'')
        return (company , model)
    except Exception as e:
        print(e)
        return (None,None)


def scrap(driver, area_val, car_list):
    # function scraps from given driver
    # area_val is the value that specify location area of the advisor
    # returns data frame of second handed cars data
    ad_num = []
    company = []
    model = []
    price = []
    engine = []
    year = []
    hand = []
    km = []
    eng_kind = []
    test = []
    current_owner = []
    prev_owner = []
    color = []
    gearbox = []
    trader = []
    area = []
    sub_area = []
    price_list_url = []
    rows = driver.find_elements(By.CSS_SELECTOR, "div[class='feeditem table'")
    try:
        counter = 0
        for row in rows:
            driver.execute_script(f"window.scrollTo(0, {row.location['y']})")
            row.click()

            # price_list_url handle
            price_url = row.find_element(By.XPATH, f'//*[@id="accordion_wide_{counter}"]/div/div[2]/div/div[2]/div[1]/div/div/div[2]/p/a').get_attribute('href')
            price_list_url.append(price_url)

            # company and model handle
            title_url = f'// *[ @ id = "feed_item_{counter}_title"] / span'
            company_tmp, model_tmp = handle_company_and_model(row, title_url, car_list)
            company.append(company_tmp)
            model.append(model_tmp)

            # price handle
            p = get_element_by_xpath(row, f'// *[ @ id = "feed_item_{counter}_price"]')
            if p == 'לא צוין מחיר':
                p = None
            if p is not None:
                p = int(p.split(' ')[0].replace(',', ''))
            price.append(p)

            # area handle
            area.append(area_val)

            # engine handle
            en = get_element_by_xpath(row, f'//*[@id="data_engine_size_{counter}"]')
            if en is not None:
                en = int(en.replace(',', ''))
            engine.append(en)

            # year handle
            year.append(int(get_element_by_xpath(row, f'//*[@id="data_year_{counter}"]')))

            # hand handle
            hand.append(int(get_element_by_xpath(row, f'//*[@id="data_hand_{counter}"]')))

            # km handle
            k = get_js_element_by_xpath(row, f'//*[@id="more_details_kilometers"]/span')
            if k is not None:
                k = int(k.replace(',', ''))
            km.append(k)

            # eng_kind handle
            # encoding for engine kink detailed in enc_eng_kind() function
            eng_kind.append(enc_eng_kind(get_js_element_by_xpath(row, f'//*[@id="more_details_engineType"]/span')))

            test.append(get_js_element_by_xpath(row, f'//*[@id="more_details_testDate"]/span'))

            # owner handle
            # encoding for owner detailed in ownership() function
            cur = get_js_element_by_xpath(row, f'//*[@id="more_details_ownerID"]/span')
            current_owner.append(ownership(cur))
            prev = get_js_element_by_xpath(row, f'//*[@id="more_details_previousOwner"]/span')
            prev_owner.append(ownership(prev))

            # color handle
            color.append(handle_color(get_js_element_by_xpath(row, f'//*[@id="more_details_color"]/span')))

            # gearbox handle
            # automatic = 0, manual = 1, tiptronic = 2, robotic = 3
            gearbox.append(gear_kind(get_js_element_by_xpath(row, f'//*[@id="more_details_gearBox"]/span')))

            # ad number handle
            try:
                ad_num.append(int((row.find_elements(By.CSS_SELECTOR, "span[class='num_ad'"))[-1].text.split(' ')[-1]))
            except:
                ad_num.append(None)

            # trader handle: private(0) or trader(1)
            trader.append(is_trader(row))

            # sub_area handle
            sub_area.append(get_element_by_xpath(row, f'//*[@id="accordion_wide_{counter}"]/div/div[2]/div/div[2]/div[1]/div/div/div[1]/div/span[2]'))


            counter+=1
            # during EDA found that only fist 18 ads are private and the other are from traders.
            if counter == 18:
                break

    except Exception as e:
        print(e)

    rows_dict = {'ad_num': ad_num,
                 'company': company,
                 'model': model,
                 'price': price,
                 'engine': engine,
                 'year': year,
                 'hand': hand,
                 'km': km,
                 'eng_kind': eng_kind,
                 'test': test,
                 'current_owner': current_owner,
                 'prev_owner': prev_owner,
                 'צבע': color,
                 'gearbox': gearbox,
                 'trader': trader,
                 'area': area,
                 'sub_area': sub_area,
                 'price_list_url': price_list_url
                 }
    return df(rows_dict)


# scrped_df is an empty data frame to save all the data to export
scraped_df = df(columns=['ad_num',
                         'company',
                         'model',
                         'price',
                         'engine',
                         'year',
                         'hand',
                         'km',
                         'eng_kind',
                         'test',
                         'current_owner',
                         'prev_owner',
                         'צבע',
                         'gearbox',
                         'trader',
                         'area',
                         'sub_area',
                         'price_list'])

# undetected webdriver to avoid blocks
driver = uc.Chrome()

# list of area codes as described below the code row.
area_list = [2, 25, 19, 101, 100, 41, 75, 43]
# 2=center
# 25=north
# 19=sharon
# 101=hadera&valies
# 100=jerusalem
# 41=shfela
# 75=y"osh
# 43=south

url = f"https://www.yad2.co.il/vehicles/cars?area={area_list[0]}"
driver.get(url)
# get all the cars from yad2 as a list.
car_list = get_car_list(driver)

exception_flag = False

for area in area_list:
    # scrap first page
    if area != area_list[0]:
        url = f"https://www.yad2.co.il/vehicles/cars?area={area}"
        driver.get(url=url)
    scraped_df = pd.concat([scraped_df, scrap(driver, area, car_list)], ignore_index=True)
    # scrap another few pages
    for page in range(2, 26):
        url = f"https://www.yad2.co.il/vehicles/cars?area={area}&page={page}"
        driver.get(url=url)
        try:
            scraped_df = pd.concat([scraped_df, scrap(driver, area, car_list)], ignore_index=True)
        except:
            print(f'could not scrap page {page} in area {area}')
            exception_flag = True
        print(f'area = {area} , page = {page} succeed')
    if exception_flag == True:
        break

driver.close()
scraped_df.to_csv('cars_data0105.csv', encoding="utf-8")
