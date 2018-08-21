import pandas as pd
import pprint
import codecs
import os
import csv
path = "D:\\金融数据\\data\\testdir11-18\\"
max_min_value = list()
for path_year in os.listdir(path):
    path_year = os.path.join(path,path_year,'sc')
    for path_file in os.listdir(path_year):
        day_value = list()
        path_file = os.path.join(path_year,path_file)
        # print(path_file)
        # file_csv = pd.read_csv(codecs.open(path_file,'r','utf-8')
        # day_value.append(path_file[48:56]) 
        if os.path.isfile(path_file):
            df_file_csv = pd.read_csv(open(path_file,'r'))
            day_value.append(df_file_csv['交易日'][1])
            day_value.append(df_file_csv['最新价'].max())
            day_value.append(df_file_csv['最新价'].min())
        max_min_value.append(day_value)
    print("已处理一年。。。")
df = pd.DataFrame(max_min_value,columns = ['日期','最高价','最低价'])

writer = pd.ExcelWriter('D:\\金融数据\\data\\process_data03-10\\11-18-price.xlsx')
df.to_excel(writer,'prices')
writer.save()



