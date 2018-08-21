# -*- coding: utf-8 -*-
import os

path = "C:\\Users\\yangguoqiang\\Desktop\\项目相关\\模型\\处理数据集\\dat_file"
file_write_path = open("C:\\Users\\yangguoqiang\\Desktop\\项目相关\\模型\\处理数据集\\test_file\\test.dat",'w',encoding='utf8')

filelist = os.listdir(path)
for files in filelist:
    filelist_1 = os.path.join(path,files)
#     print(filelist_1)
    for file in os.listdir(filelist_1):
#         print(file)
        data_file = open(os.path.join(filelist_1,file),'r',encoding='utf8')
        for i in range(2000):
            line = data_file.readline()
            file_write_path.writelines(line)
        data_file.close()

file_write_path.close()