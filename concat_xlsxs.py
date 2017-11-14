import glob
import pandas as pd

path = './'

all_files = glob.glob('*.xlsx')
all_files.sort()
print(all_files)
frame = pd.DataFrame()
list_ = []

for file in all_files:
    df = pd.read_excel(file, index_col=None)
    list_.append(df)

frame = pd.concat(list_)
frame.to_excel('restaurants.xlsx', index=False)