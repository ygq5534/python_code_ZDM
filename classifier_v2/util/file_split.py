#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, json, os, traceback

class FileSplit(object):
    '''
        将训练集根据类目层次结构分开
    '''
    def __init__(self):
        pass

    # 将数据文件根据类目划分到不同的文件夹中
    def split_data_into_dir(self, data_file, base_dir):
        self.cate_fp = dict()
        self.base_dir = base_dir
        dfile = open(data_file, 'r')
        for line in dfile:
            try:
                line = line.strip()
                cate = line.split('\t')[0]
                cate_name_lst = json.loads(cate)
                cate_name_lst = self.category_modify(cate_name_lst)
                if not cate_name_lst:
                    continue
            except Exception , e:
                print >> sys.stderr, '==>', e
                print >> sys.stderr, "Error:", line
            self.write_to_file(cate_name_lst, line)
        dfile.close()

    # 将数据写入文件
    def write_to_file(self, cate_name_lst, line):
        s = u'$'.join(cate_name_lst[:3])
        if not s in self.cate_fp: 
            self.create_file(s, cate_name_lst[:3])
        fp = self.cate_fp[s]
        print >> fp, line

    # 创建文件和文件夹
    def create_file(self, s, cate_name_lst):
        dir = self.base_dir
        for i in range(len(cate_name_lst)-1):
            try:
                key = u'$'.join(cate_name_lst[:i+1])
                #print >> sys.stderr, "****", key.encode('u8')
                tag = self.cate_tag_map[key]
            except:
                print >> sys.stderr, 'No key:', key.encode('u8')
                print json.dumps(cate_name_lst, ensure_ascii=False).encode('u8')
                sys.exit()                
            dir = os.path.join(dir, tag)
            if not os.path.exists(dir):
                os.makedirs(dir)
        key = u'$'.join(cate_name_lst)
        try:
            tag = self.cate_tag_map[key]
        except:
            print >> sys.stderr, 'No file key:', key.encode('u8')
            print json.dumps(cate_name_lst, ensure_ascii=False).encode('u8')
            sys.exit()
        filename = os.path.join(dir, tag+".dat")
        fp = open(filename, 'w')
        self.cate_fp[s] = fp

    # 读取类目标识映射文件，标识作为文件夹和文件的名称
    def read_map_file(self, map_file):
        self.cate_tag_map = dict()
        mfile = open(map_file, 'r')
        for line in mfile:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            cate = u'$'.join(json.loads(fields[1]))
            # print cate.encode('u8')
            tag = fields[0]
            self.cate_tag_map[cate] = tag
        mfile.close()

    # 读取类目调整文件
    def read_modify_file(self, modify_file):
        self.cate_modify_map = dict()
        mfile = open(modify_file, 'r')
        for line in mfile:
            ori_cat, dst_cat = line.strip().decode('u8').split('\t')
            self.cate_modify_map[ori_cat] = dst_cat
        mfile.close()
        
    # 根据调整规则将旧类目映射到新类目
    def category_modify(self, cate_name_lst):
        s = cate_name_lst[0]
        if s in [u'服饰鞋帽', u'个人护理', u'母婴用品$']:
            return []
        s = u'$'.join(cate_name_lst[:2])
        if s in [u'美食特产$保健营养品', u'出差旅游$定制游']:
            return []
        s = u'$'.join(cate_name_lst[:3])
        if s in self.cate_modify_map:
            modify_cate = self.cate_modify_map[s]
            print >> sys.stderr, s.encode('u8'), modify_cate.encode('u8')
            return modify_cate.split(u'$')
        else:
            return cate_name_lst
    
    # 关闭文件句柄
    def close_file(self):
        for fp in self.cate_fp.values():
            fp.close()        

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print >> sys.stderr, "Usage: %s cate_map_file cate_modify_file data_file base_dir" %sys.argv[0]
        sys.exit()
    fs = FileSplit()
    fs.read_map_file(sys.argv[1])
    fs.read_modify_file(sys.argv[2])
    fs.split_data_into_dir(sys.argv[3], sys.argv[4])
    fs.close_file()
    
