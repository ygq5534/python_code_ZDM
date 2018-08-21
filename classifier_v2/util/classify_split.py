#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys, os, json
sys.path.append("../")

from preprocess.preprocess import Preprocess
from predict import Predict
from train import Train
from ClassTreePredict import ClassTreePedict
from rule import Rule

class ClassifySplit(object):
    '''
        根据规则修改类目标签，并切分到不同的文件中
    '''
    def __init__(self, cfg_file_name, rule_file, cate_id_file, out_dir):
        self.preprocess = Preprocess(cfg_file_name)
        self._rule = Rule()
        self._rule.load_rule(rule_file)
        self.out_dir = out_dir

        cate_file = open(cate_id_file, 'r')
        lines = cate_file.readlines()
        self.cate_map = json.loads(''.join(lines))
        cate_file.close()

        self.cate_fp = {}

    def split_to_file(self, result, name,  brand, price):
        cid = self.cate_map[result]

        if cid not in self.cate_fp:
            self.cate_fp[cid] = open(os.path.join(self.out_dir, cid), 'w')
        fp = self.cate_fp[cid]
        cates = json.dumps(result.split(u'$'), ensure_ascii=False)
        print >> fp, "%s\t%s\t%s\t%s" %(cates.encode('u8'), name.encode('u8'), brand.encode('u8'), str(price))

    def process(self, path):
        if os.path.isdir(path):
            for file in os.listdir(path):
                t_path = os.path.join(path, file)
                self.process(t_path)

        elif os.path.isfile(path):
            fp = open(path, 'r')
            for line in fp:
                line = line.strip('\n')
                fields = line.split('\t')
                try:
                    cat_name = fields[0].decode('u8')
                    name = fields[1].decode('u8')
                    brand = u''
                    price = 0
                    if len(fields) > 3:
                        brand = fields[2].decode('u8')
                        price = fields[3]
                    cat_lst = json.loads(cat_name)
                    result = self._rule.predict(name, price)
                    self.split_to_file(result, name, brand, price)  

                except Exception, e:
                    print >> sys.stderr, "Error:", line
                    print >> sys.stderr, e
                    continue

    def close_file(self):
        for fp in self.cate_fp.values():
            fp.close()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print >> sys.stderr, "Usage: %s config_file cate_id rule_file data_file out_dir" %sys.argv[0]
        sys.exit()

    # cfg_file_name, rule_file, cate_id_file, out_dir
    cs = ClassifySplit(sys.argv[1], sys.argv[3], sys.argv[2], sys.argv[5])
    cs.process(sys.argv[4])
    cs.close_file()
