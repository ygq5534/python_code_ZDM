import pandas as pd
import codecs


path_data = 'C:\\Users\\yangguoqiang\\Desktop\\项目相关\\3c_test_data_0608.txt'
path_out = 'C:\\Users\\yangguoqiang\\Desktop\\项目相关\\nohup20180608.out'
data = codecs.open(path_data,'r','utf-8')
out = codecs.open(path_out,'r','utf-8')
list_data = []


for line in data:
    list_data.append(list(line.strip('\n').split(',')))


df_data0 = pd.DataFrame(list_data)
df_data = df_data0[[9,10,11,13]]
df_data.columns = [0,1,2,3]
# df_data

list_out = []
for line in out:
    list_line0 = list(line.split('\t'))
    list_line1 = list(list_line0[1].split('$$$'))
    list_line2 = list(list_line1[0].split('$'))
    list_line2.append(list_line0[0])
#     print(list_line2)
    list_out.append(list_line2)


df_out = pd.DataFrame(list_out)
# clu_id = df_out[3]
# df_out.drop(labels = 3,axis = 1,inplace = True)
# df_out.insert(0,3,clu_id)
df_out.columns = [0,1,2,3]
# df_out

id_class = 0
one_class = 0
two_class = 0
three_class = 0
badcase = pd.DataFrame()

for i in range(len(df_data)):
#     if df_data.iloc[i][3] == df_out.iloc[i][3]:
#         id_class += 1
    if df_data.iloc[i][0] == df_out.iloc[i][0]:
        one_class += 1
        if df_data.iloc[i][1] == df_out.iloc[i][1]:
            two_class += 1
            if df_data.iloc[i][2] == df_out.iloc[i][2]:
                three_class += 1
            else:
            	badcase.append(df_data.iloc[i])#,ignore_index=True)
        else:
        	badcase.append(df_data.iloc[i])#,ignore_index=True)
    else:
    	badcase.append(df_data.iloc[i])#,ignore_index=True)

# print(id_class/len(df_data)) 
print(badcase)
print('总数据量：'+str(len(df_data))+'\t一级匹配量：'+ str(one_class)+ '\t一级准确率:' +str(one_class/len(df_data)))
print('总数据量：'+str(len(df_data))+'\t二级匹配量：'+ str(two_class)+ '\t二级准确率:' +str(two_class/len(df_data)))
print('总数据量：'+str(len(df_data))+'\t三级匹配量：'+ str(three_class)+ '\t三级准确率:' +str(three_class/len(df_data)))