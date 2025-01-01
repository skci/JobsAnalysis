import pandas as pd

fileNameStr = 'test.csv'

data = pd.read_csv(fileNameStr, encoding='utf-8', dtype=str)

duplicate_bool = data.duplicated(keep='first')
print(data.loc[duplicate_bool == True])

# # 输出全部行，不省略
# pd.set_option('display.max_rows', None)
