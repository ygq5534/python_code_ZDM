#!/usr/bin/python
#-*-coding:utf-8 -*-
import sys
import os
import json
import random
import traceback
reload(sys)
sys.setdefaultencoding('utf8')

def process(dir):
    file_map = open('./resource/cate_id.cfg', 'r')
    data_lines = file_map.readlines()
    data_map = ''.join(data_lines)
    data_map_dict = json.loads(data_map)
    file_map.close()
    file_list = os.listdir(dir)
    error_file_list = []
    for f in file_list:
        if f.endswith('.model')==False and f.endswith('.rule')==False and f.endswith('.rule_cate')==False and f.endswith('.price')==False:
            error_file_list.append(f)            
    if len(error_file_list) > 0:
        print "有错误的文件："
        print "--------------",','.join(error_file_list)
    
    id_map_dict_0_grade = {}
    id_map_dict_1_grade = {}
    id_map_dict_2_grade = {}

    check_0_grade = {}
    check_1_grade = {}
    check_2_grade = {}

    for name in data_map_dict:
        if name == 'root':
            id_map_dict_0_grade[data_map_dict[name]] = name
            check_0_grade[data_map_dict[name]] = [] 
        else:
            if len(name.strip().split('$'))==1:
                id_map_dict_1_grade[data_map_dict[name]] = name
                check_1_grade[data_map_dict[name]] = []
            if len(name.strip().split('$'))==2:
                id_map_dict_2_grade[data_map_dict[name]] = name
                check_2_grade[data_map_dict[name]] = []


    for f in file_list:
        id = f[:f.find('.')]
        if f.endswith('.model') or f.endswith('.rule') or f.endswith('.rule_cate') or f.endswith('.price'):
            end = f[f.find('.')+1:]
            if check_0_grade.has_key(id):
                check_0_grade[id].append(end)
            elif check_1_grade.has_key(id):
                check_1_grade[id].append(end)
            elif check_2_grade.has_key(id):
                check_2_grade[id].append(end)
            else:
                print "-----------------------------error : ",f


    #print json.dumps(check_0_grade, ensure_ascii=False)
    #print json.dumps(check_1_grade, ensure_ascii=False)
    #print json.dumps(check_2_grade, ensure_ascii=False)
   
    print "-----------------------------------------一级"
    for id in check_0_grade:
        if len(check_0_grade[id])==0:
            print >> sys.stderr, id, id_map_dict_0_grade[id], "--- 即没有模型也没有规则文件        --- error"
        elif 'model' not in check_0_grade[id]:
            print >> sys.stderr, id, id_map_dict_0_grade[id], "--- 没有模型文件，只有", ','.join(check_0_grade[id])
        elif len(check_0_grade[id]) > 1:
            print >> sys.stderr, id, id_map_dict_0_grade[id], "--- 同时有模型和规则文件:", ','.join(check_0_grade[id])

    print "-----------------------------------------二级"
    for id in check_1_grade:
        if len(check_1_grade[id])==0:
            print >> sys.stderr, id, id_map_dict_1_grade[id], "--- 即没有模型也没有规则文件        --- error"
        elif 'model' not in check_1_grade[id]:
            print >> sys.stderr, id, id_map_dict_1_grade[id], "--- 没有模型文件，只有:", ','.join(check_1_grade[id])
        elif len(check_1_grade[id]) > 1:
            print >> sys.stderr, id, id_map_dict_1_grade[id], "--- 同时有模型和规则文件:", ','.join(check_1_grade[id])
            
    print "-----------------------------------------三级"
    for id in check_2_grade:
        if len(check_2_grade[id])==0:
            print >> sys.stderr, id, id_map_dict_2_grade[id], "--- 即没有模型也没有规则文件          --- "
        elif 'model' not in check_2_grade[id] and 'rule' not in check_2_grade[id]:
            print >> sys.stderr, id, id_map_dict_2_grade[id], "--- 只有", ','.join(check_2_grade[id])
        elif len(check_2_grade[id]) > 1:
            print >> sys.stderr, id, id_map_dict_2_grade[id], "--- 同时有模型和规则文件:", ','.join(check_2_grade[id])
            

if __name__ == "__main__":
    process(sys.argv[1])
 
    
