path = "C:\\Users\\yangguoqiang\\Desktop\\root1.txt"
f = codecs.open(path,'r','utf-8')

data = f.readlines()
n_data = []
pprint.pprint(data)

for d in data:
    d = d.split('\t')
    n_data.append(d)
pprint.pprint(n_data)
df = pd.DataFrame(n_data,columns = ['key', 'cate_num','pred_num','correct_num','precision','recall','F_s'])
writer = pd.ExcelWriter("C:\\Users\\yangguoqiang\\Desktop\\root_test.xlsx")
df.to_excel(writer,"abac")
writer.save()