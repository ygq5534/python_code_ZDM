# -*- coding:utf-8 -*-
import pandas as pd
import sys, os
import time


# reload(sys)
# sys.setdefaultencoding('utf-8')

def write_cat(col, src_path, tag_path):
    try:
        # prod_data = pd.read_table(src_path, sep="\001", engine="python", names=col)
        # prod_data = pd.read_csv(src_path, engine="python", names=col, lineterminator=os.linesep)
        prod_data = pd.read_csv(src_path, engine="python", names=col)
        prod_data = prod_data.fillna(" ")
        dis_cat3 = prod_data.drop_duplicates(subset=["CAT1","CAT2","CAT3"])
        map_cat3 = dis_cat3[["CAT1_NAME","CAT2_NAME","CAT3_NAME","MAP_CAT3"]]
        sep_str = "$"
        filename_dict = {}
        for index, row in map_cat3.iterrows():
            # print row["CAT1_NAME"], row["CAT2_NAME"], row["CAT3_NAME"]    
            if row["MAP_CAT3"] not in filename_dict.keys():
                filename_dict[row["MAP_CAT3"]] = row["CAT1_NAME"].decode("u8")+sep_str+row["CAT2_NAME"].decode("u8")+sep_str+row["CAT3_NAME"].replace("/","").decode("u8")
                # filename_dict[row["MAP_CAT3"]] = row["CAT1_NAME"].encode("u8")+sep_str+row["CAT2_NAME"].encode("u8")+sep_str+row["CAT3_NAME"].encode("u8")
            else:
                pass

        for index, prod_row in prod_data.iterrows():
            title = prod_row["TITLE"].replace("\t"," ")
            brand_name = prod_row["BRAND_NAME"].replace("\N"," ")
            rst_str = ("[\""+prod_row["CAT1_NAME"]+"\",\""+prod_row["CAT2_NAME"]+"\",\""+prod_row["CAT3_NAME"]+"\"]"
                      +"\t"+title+"\t"+brand_name+"\t"+str(prod_row["PRICE"])+"\n")
            MAP_CAT1 = str(prod_row["MAP_CAT3"]).replace(str(prod_row["MAP_CAT3"])[-5:],"00000")
            tag_path_tmp = tag_path+"/"+MAP_CAT1
            if not os.path.isdir(tag_path_tmp):
                # tag_path = tag_path+"/"+MAP_CAT1
                os.system("mkdir " + tag_path_tmp)
            else:
                pass
            cat_name = filename_dict[prod_row["MAP_CAT3"]].replace("/"," ")
            # print cat_name
            tag_fname = tag_path_tmp+"/"+str(prod_row["MAP_CAT3"])+"_"+cat_name.encode("utf-8")+".dat"
            # print tag_fname
            with open(tag_fname, "a") as f:
                f.write(rst_str)
    except Exception as e:
        print e
        print src_path

def get_fname(file_dir):
    for root, dirs, files in os.walk(file_dir):
        return files




if __name__ == "__main__":
    start = time.clock()
    # src_path = "/home/python/zeh/tmp/data/data_src/jd_data/20180529_part21"
    src_path = "/home/python/zeh/tmp/data/data_src/all_data/test"
    # tag_path = "/home/python/zeh/tmp/data/website_brand"
    tag_path = "/home/python/zeh/tmp/data/data_train_test12"
    col_name = ["URL","TITLE","PRICE","CAT1","CAT2","CAT3","BRAND_ID","BRAND_NAME","CAT1_NAME","CAT2_NAME","CAT3_NAME", "STATU","MAP_CAT3","POP"]
    files = get_fname(src_path)
    os.system("sh /home/python/zeh/tmp/script/etl.sh "+src_path)
    # os.system("sh /home/python/zeh/tmp/script/iconv_data.sh "+src_path)
    for f_name in files:
        src_file = src_path +"/"+ f_name
        write_cat(col_name, src_file, tag_path)
    
    # calculate time
    elasped = (time.clock() - start)
    print "Time used:", elasped



