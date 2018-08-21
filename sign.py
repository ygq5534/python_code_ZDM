# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 10:43:05 2018

@author: yangguoqiang
"""

import pandas as pd
#import numpy as np
import os

f = 'F'
r = 'R'
pz = 'PZ'

path = 'C:\\Users\\yangguoqiang\\Desktop\\橡胶主力'
filename = '橡胶主力连续日数据.xlsx'
savename = '橡胶主力连续日数据_已标记.xlsx'
file_path = os.path.join(path,filename)
save_path = os.path.join(path,savename)
df_data = pd.read_excel(file_path,sheetname='file')
df_data.drop([len(df_data)-1,len(df_data)-2],inplace=True)

#print(df_data)

symbol = list()

if df_data['开盘价(元)'][0] > df_data['收盘价(元)'][0]:           
    symbol.append(f)
elif df_data['开盘价(元)'][0] < df_data['收盘价(元)'][0]:
    symbol.append(r)
else:
    symbol.append(pz)
        
for i in range(1,len(df_data)):
    if df_data['最高价(元)'][i] > df_data['最高价(元)'][i-1] and df_data['最低价(元)'][i] > df_data['最低价(元)'][i-1]:
        symbol.append(r)
    elif df_data['最高价(元)'][i] < df_data['最高价(元)'][i-1] and df_data['最低价(元)'][i] < df_data['最低价(元)'][i-1]:
        symbol.append(f)
    else:
        symbol.append(pz)

df_data['标签'] = symbol
#print(df_data)
df_data.to_excel(save_path,'file')
 
        
        