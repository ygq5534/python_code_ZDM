import codecs
import random
import linecache
import time
start = time.clock()
path = 'C:\\Users\\yangguoqiang\\Desktop\\项目相关\\3c_test_data_0716.txt'
save_path = 'C:\\Users\\yangguoqiang\\Desktop\\项目相关\\3c_test_data_0716c-sample.txt'
data = codecs.open(path,'r','utf-8')
save_f = codecs.open(save_path,'w','utf-8')
result = []
for line in data:
    result.append(list(line.split('\n')))

# result[0][1]

sample = random.sample(result,2500)

for i in range(len(sample)):
    save_f.write(str(sample[i][0])+'\n')
save_f.close()
end  = time.clock()
print(end-start)
