import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
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
    if gearbox == 'ידני':
        return 1
    if gearbox == 'טיפטרוניק':
        return 2
    if gearbox == 'רובוטית':
        return 3
    return None


def enc_color(param):
    # get from a string only the color and encode it:
    # red = 0
    # gray = 1
    # pink = 2
    # brown = 3
    # green = 4
    # blue = 5
    # orange = 6
    # wight = 7
    # purple = 8
    # yellow = 9
    # black = 10
    # silver = 11
    # missing_val = 12
    color = param.split(' ')[0]
    if color == 'אדום':
        return 0
    if color == 'אפור':
        return 1
    if color == 'ורוד':
        return 2
    if color == 'חום':
        return 3
    if color == 'ירוק':
        return 4
    if color == 'כחול':
        return 5
    if color == 'כתום':
        return 6
    if color == 'לבן':
        return 7
    if color == 'סגול':
        return 8
    if color == 'צהוב':
        return 9
    if color == 'שחור':
        return 10
    if color == 'כסוף':
        return 11
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
    return -1


def scrap(driver):
    # function scraps from given driver
    # returns dictionary of second handed cars data
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
    rows = driver.find_elements(By.CSS_SELECTOR, "div[class='feeditem table'")
    try:
        counter = 0
        for row in rows:
            driver.execute_script(f"window.scrollTo(0, {row.location['y']})")
            row.click()
            sleep(1)

            # get company and model
            try:
                tmp = row.find_element(By.XPATH, f'// *[ @ id = "feed_item_{counter}_title"] / span')
                t = tmp.text.split(' ', maxsplit=1)
                company.append(t[0])
                model.append(t[1])
            except Exception as e:
                print(e)
                company.append(None)
                model.append(None)
            # price handle
            p = get_element_by_xpath(row, f'// *[ @ id = "feed_item_{counter}_price"]')
            if p == 'לא צוין מחיר':
                 p = None
            if p is not None:
                p = int(p.split(' ')[0].replace(',', ''))
            price.append(p)

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
                k = int(k.replace(',',''))
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
            # color encoding in enc_color() function
            color.append(enc_color(get_js_element_by_xpath(row, f'//*[@id="more_details_color"]/span')))

            # gearbox handle
            # automatic = 0, manual = 1, tiptronic = 2, robotic = 3
            gearbox.append(gear_kind(get_js_element_by_xpath(row, f'//*[@id="more_details_gearBox"]/span')))

            # ad number handle
            ad_num.append(int((row.find_elements(By.CSS_SELECTOR, "span[class='num_ad'"))[-1].text.split(' ')[-1]))

            # trader handle: private(0) or trader(1)
            trader.append(is_trader(row))


            counter += 1



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
                 'color': color,
                 'gearbox': gearbox,
                 'trader': trader
                 }
    print(rows_dict)
    return rows_dict


driver = uc.Chrome()

# setting dynamic URL and needed parameters
area_list = [2, 25, 19]  # 2=center, 25=north, 19=sharon
url = f"https://www.yad2.co.il/vehicles/cars?area={area_list[0]}"

driver.get(url=url)
sleep(1)
scraped_data = scrap(driver)
driver.close()
scraped_df = df(scraped_data)
scraped_df.to_csv('cars_data.csv', encoding="utf-8")


