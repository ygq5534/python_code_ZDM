# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 16:06:10 2018

@author: yangguoqiang
"""
import tushare as ts
import pandas as pd
import numpy as np
import os

features = pd.DataFrame()
df_hs300 = ts.get_hist_data('hs300')

p_change = df_hs300['p_change'] #价格变化百分比
#print(p_change)

ma5_max = df_hs300['ma5'].max()
ma5_min = df_hs300['ma5'].min()
ma5 = (df_hs300['ma5']-ma5_min)/(ma5_max-ma5_min) #ma5
#print(ma5)

v_list = [(df_hs300.iloc[i][4]-df_hs300.iloc[i+1][4])/df_hs300.iloc[i+1][4] 
        for i in range(len(df_hs300)-1)]
v_list.append(1)
v_change = pd.Series(v_list)
v_change.append(pd.Series(0)) #成交量变化
#print(v_change)

v_ma5_max = df_hs300['v_ma5'].max()
v_ma5_min = df_hs300['v_ma5'].min()
v_ma5 = (df_hs300['v_ma5']-v_ma5_min)/(v_ma5_max-v_ma5_min)#成交量移动变化
#print(v_ma5)

price_change = df_hs300['high']-df_hs300['low']
price_change_max = price_change.max()
price_change_min = price_change.min()
price_change = (price_change-price_change_min)/(price_change_max-price_change_min)#当天价格最高与最低的差
#print(price_change)

volume_max = df_hs300['volume'].max()
volume_min = df_hs300['volume'].min()
volume = (df_hs300['volume']-volume_min)/(volume_max-volume_min)#成交量
#print(volume)

close_list = [(df_hs300.iloc[i][2]-df_hs300.iloc[i+1][2])/df_hs300.iloc[i+1][2] 
        for i in range(len(df_hs300)-1)]
close_list.append(1)
close_change = pd.Series(close_list)
pv = p_change/v_list #价格变化与成交量变化的比值
pv = (pv-pv.min())/(pv.max()-pv.min())
#print(pv)

path_shibor = 'C:\\Users\\yangguoqiang\\Desktop\\橡胶主力'
df_shibor15 = pd.read_excel(os.path.join(path_shibor,'Shibor数据2015.xls'))
#shibor15 = df_shibor15['1W'][140:]
#print(shibor15)  

df_shibor16 = pd.read_excel(os.path.join(path_shibor,'Shibor数据2016.xls'))                     
#shibor16 = df_shibor16['1W']

df_shibor17 = pd.read_excel(os.path.join(path_shibor,'Shibor数据2017.xls'))                     
#shibor17 = df_shibor17['1W']

df_shibor18 = pd.read_excel(os.path.join(path_shibor,'Shibor数据2018.xls'))                     
#shibor18 = df_shibor18['1W']
#print(shibor18)
df_shibor = pd.concat([df_shibor15,df_shibor16,df_shibor17,df_shibor18])
#df_shibor = pd.concat([shibor15,shibor16,shibor17,shibor18])
#print(df_shibor)
ind = pv.index
shibor = []
i = 0
#df_shibor['日期'] = pd.date_range(df_shibor['日期']).to_period('D')
#df_shibor.set_index(["日期"],inplace=True)
#shibor_index = df_shibor.index.to_period('D')
#df_shibor = df_shibor.reset_index(drop = True)
#df_shibor = pd.DataFrame(df_shibor,columns=df_shibor)
#print(df_shibor)
#for date in df_shibor['日期']:
#    if ind[i] == date:
#        shibor.append(df_shibor['1W'][''])













