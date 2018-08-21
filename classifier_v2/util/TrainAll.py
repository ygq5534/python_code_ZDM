#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import sys, os, json, logging
from preprocess.preprocess import Preprocess
from train import Train

class TrainAll(object):
    def __init__(self, cfg_file_name):
        self.features = []
        self.labels = []
        self.cnt = 0
        self.preprocess = Preprocess(cfg_file_name)

    def load_data_path(self, path, level=0):
        if os.path.isdir(path):
            for file in os.listdir(path):
                t_path = os.path.join(path, file)
                self.load_data_path(t_path, level)

        elif os.path.isfile(path):
            fp = open(path, 'r')
            for line in fp:
                line = line.strip('\n')
                fields = line.split('\t')
                try:
                    cat_name = fields[0].decode('u8')
                    name = fields[1].decode('u8')
                    brand = fields[2].decode('u8')
                    price = fields[3]
                    if len(fields) == 5:
                        ori_cat = fields[4]
                    #cat_name, name, brand, price = line.split('\t')
                    #cat_name, name, feats = line.strip('\n').split('\t')
                    cat_lst = json.loads(cat_name)
                    if len(cat_lst) < level+1:
                        continue
                    labels = u'$'.join(cat_lst[:level+1])
                except Exception, e:
                    print >> sys.stderr, "Error:", line
                    print >> sys.stderr, e
                    continue
                self.cnt += 1
                if self.cnt % 10000 == 0:
                    print >> sys.stderr, "load %d samples..." %self.cnt

                if cat_lst[0] in [u'服饰鞋帽', u'个人护理', u'母婴用品$']:
                    continue

                features = self.preprocess.process(name, cat_name, brand, price, level=level)
               
                self.features.append(features)
                self.labels.append(labels)

            fp.close()
    
    def train_all(self, data_dir, model_dir, model_name, level):
        
        for file in os.listdir(data_dir):
            t_path = os.path.join(data_dir, file)
            if os.path.isdir(t_path):
                self.train_all(t_path, model_dir, file, level+1)

        print >> sys.stderr, "load node samples", data_dir
        self.features = []
        self.labels = []
  
        self.cnt = 0
        self.load_data_path(data_dir, level)
        print >> sys.stderr, "load samples" , self.cnt
        if (len(set(self.labels))) <= 1:
            logging.error("same label: %s" %self.labels[0].encode('u8'))
            return
        
        if level == 0:
            space = 'topic'
            params = {'n_topics': 30}
        elif level == 1:
            space = 'topic'
            len_child = len(os.listdir(data_dir))+5
            params = {'n_topics': len_child}
        else:
            space = 'word'
            params = {}
        _train = Train(space, params)
        print >> sys.stderr, "train the model"
        _train.train(self.features, self.labels)
        model_path = os.path.join(model_dir, model_name+".model")
        print >> sys.stderr, "dump the model", model_path
        _train.dump_model(model_path)

if __name__ == '__main__':
    #logging.getLogger().setLevel(logging.ERROR)
    if len(sys.argv) < 4:
        print >> sys.stderr, "Usage: %s config_file <data_dir> <model_dir>" % sys.argv[0]
        sys.exit()
    config_file = sys.argv[1]
    data_dir = sys.argv[2]
    model_dir = sys.argv[3]
    ta = TrainAll(config_file)
    ta.train_all(data_dir, model_dir, 'root', 0)

