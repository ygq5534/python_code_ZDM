from unrar import rarfile
import os
import fnmatch

def unrar_file(rar_path,year):
    year_ru = year[2:]
    unrar_path = "D:\\金融数据\\data\\testdir11-18\\ru"+year_ru+"01"+"_"+str(int(year)-1)
    
    isExists = os.path.exists(unrar_path)
    if isExists:
        pass
    else:
        unrar_path = os.mkdir(unrar_path)
    print(unrar_path)
    rar = rarfile.RarFile(rar_path)
    rar.setpassword("www.jinshuyuan.net")
    
#     print('jfasdl;fldjksa;')
    name_list = rar.namelist()
    for name in name_list:
        if name.startswith('sc\\ru'+str(year_ru)+'01') or name.startswith('sc\\ru'+str(int(year_ru)+1)+'01'):
            file_name = name
            if os.path.exists(unrar_path):
                
                print(file_name+unrar_path)
                rar.extract(member = file_name ,path = unrar_path)
            else:
                print("文件夹创建失败！")
                
dir_path = "D:\\金融数据\\data\\11-18\\"

for rar_name in os.listdir(dir_path):

    for i in range(2011,2019):
        file_str = 'FutAC_TickKZ_CTP_Daily_'+str(i)+'01.rar'
#             print(file_str)
        if fnmatch.fnmatch(rar_name,file_str):
            year = str(i)
            rar_path = os.path.join(dir_path,rar_name)
            print(rar_path)
            unrar_file(rar_path,year)
            break
        file_str = 'FutAC_TickKZ_CTP_Daily_'+str(i)+'[0-1][0-9].rar'
        if fnmatch.fnmatch(rar_name,file_str):
            year = str(i+1)
            rar_path = os.path.join(dir_path,rar_name)
            print(rar_path)
            unrar_file(rar_path,year)

    
# unrar_path = "D:\\金融数据\\data\\testdir"

    
#     info = rar.getinfo('sc\\ru0401_20030801.csv')
#     print(rar.infolist())
#     rar_name = ['ru0401_20030801.csv','ru0401_20030808.csv']
    