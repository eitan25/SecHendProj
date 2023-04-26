
#             PROXY = 'http://128.140.6.139:8080'

import pandas as pd
from pandas import DataFrame as df


data = pd.read_csv('cars_data.csv')
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.unicode.ambiguous_as_wide', True)
traders = data.loc[data["trader"] == 1 ].trader.count()
print(f'sum of traders: {traders}')
nontraders = (data.loc[data["trader"] == 0]).trader.count()
print(f'sum of non traders: {nontraders}')

# print(data)


