import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

url = 'https://levi-itzhak.co.il/20,000-25,000-%E2%82%AA'
result = requests.get(url)
soup = BeautifulSoup(result.text, 'html.parser')

urls = []
model_code = []
engine_capacity = []
brand = []
model = []
year = []
from_price = []
to_price = []
average_price = []


# finds all links of the pages that contained the data and puts it in a list
for link in soup.find_all('a', {"class": "level3"}):
    # appending the link from the website to a list
    urls.append(f'{link["href"][:-1]}%E2%82%AA')
    # re.findall separates the numbers from the string and puts it in to a list
    temp_list_price = re.findall(r'\d+', f'{link["href"]}')
    # appending the numbers in the list to specific list for the future df
    from_price.append(temp_list_price[0] + temp_list_price[1])
    to_price.append(temp_list_price[2] + temp_list_price[3])

# scraping the data from each link
i = 0
for url in urls:
    full_url = f"https://levi-itzhak.co.il{url}"
    df_list = pd.read_html(io=full_url)

    # nested loop is required because the data is in a table
    for df in df_list:
        for j in range(len(df. index)):
            # appending the data in to lists, each column to specific list
            model_code.append(df.values[j][0])
            engine_capacity.append(df.values[j][1])
            year.append(df.values[j][3])
            average_price.append((int(from_price[i]) + int(to_price[i])) / 2)

            # get the brand of the car
            model_brand = df.values[j][2].split()
            # converting the list(model_brand) to a string
            tmp_str = ' '.join(model_brand)
            brand.append(tmp_str.partition(' ')[0])
            model.append(tmp_str.partition(' ')[2])
    # creating new data frame and inserting the list to it
    new_df = pd.DataFrame({"Model_Code": model_code,
                           "Engine_Capacity": engine_capacity,
                           "Brand": brand,
                           "Model": model,
                           "Year": year,
                           "Average_Price": average_price})
    i = i + 1
print(new_df)

file_name = 'L.I. price list.xlsx'
new_df.to_excel(file_name)
print('DataFrame is written to Excel File successfully.')
