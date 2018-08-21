#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, logging, json, random, ConfigParser
from preprocess.preprocess import Preprocess
from predict import Predict
from train import Train
from ClassTreePredict import ClassTreePedict
from rule import Rule

class ClassifierRun():
    def __init__(self, cfg_file_name):
        self.config = ConfigParser.ConfigParser()
        self.cur_dir = os.path.dirname(os.path.abspath(cfg_file_name))
        self.cfg_parser(cfg_file_name)
        self.preprocess = Preprocess(cfg_file_name)

        self.cnt = 0
        self.train_features = []
        self.train_labels = []

        self.test_features = []
        self.test_labels = []
        self.test_names = []

        self._train = Train(self.space, self.params)
        self._predict = Predict()
        self._rule = Rule()
        
        self._tree = ClassTreePedict('./resource/cate_id.cfg', './model')

    def cfg_parser(self, cfg_file_name):
        self.config.read(cfg_file_name)
        section = 'model'
        if self.config.has_option(section, 'model_file'):
            self.model_path = self.config.get(section, 'model_file')
        else:
            self.model_path = './model/testmodel'

        if self.config.has_option(section, 'model_dir'):
            self.model_dir = self.config.get(section, 'model_dir')
        else:
            self.model_dir = './model'
       
        if self.config.has_option(section, 'vec_space') and self.config.get(section, 'vec_space') == 'topic':
            self.space = 'topic'
        else:
            self.space = 'word'

        if self.space == 'topic':
            if self.config.has_section('topic_param'):
                self.params = dict(self.config.items('topic_param'))
        elif self.space == 'word':
            if self.config.has_section('word_param'):
                self.params = dict(self.config.items('word_param'))

        section = 'evaluation'
        self.test_size_prob = 1.0
        if self.config.has_option(section, 'test_size'):
            self.test_size_prob = self.config.getfloat(section, 'test_size')
        if self.config.has_option(section, 'random_state'):
            seed = self.config.getint(section, 'random_state')
            random.seed(seed)
            
        self.level = 0
        section = 'default'
        if self.config.has_option(section, 'level'):
            self.level = self.config.getint(section, 'level')
        if self.config.has_option(section, 'cate_id_file'):
            self.cate_id_file = self.config.get(section, 'cate_id_file')
        else:
            self.cate_id_file = "resource/cate_id.cfg"

        logging.info('[Done] config parsing')       
        logging.info('use %s space, params=%s' %(self.space, json.dumps(self.params) ))
 
    def train(self):
        self._train.train(self.train_features, self.train_labels)
        self._train.dump_model(self.model_path)

    def test(self):
        if self.model_path.endswith('rule'):
            self._rule.load_rule(self.model_path)
            is_rule = True
        else:
            self._predict.load_model(self.model_path)
            is_rule = False
        print len(self.test_features)
        for (features, label, name) in zip(self.test_features, self.test_labels, self.test_names):
            if is_rule:
                result = self._rule.predict(name, 0)
            else:
                result = self._predict.predict(features)
            print result.encode('u8'),'\t', label.encode('u8'),'\t', name.encode('u8'), '\t', json.dumps(features,'\t', ensure_ascii=False).encode('u8')

    def testone(self, name, cat_name, brand, price):
        tree = ClassTreePedict(self.cate_id_file, model_dir)
        features = self.preprocess.process(name, cat_name, brand, price, level=0)
        features = json.loads('{"Eden": 1, "Botkier": 1, "Satchel": 1, "马毛": 1, "女士": 1, "柏柯尔": 1, "拼接": 1, "手提包": 1, "Small": 1 }')
        result = tree.predict(name, features, indexclass=u"root") 
        print result.encode('u8'), name.encode('u8'), json.dumps(features, ensure_ascii=False).encode('u8')

    # map_cfg 类目和ID的映射文件，model_dir 存放模型文件目录，data_file 数据文件
    def predict(self, map_cfg, model_dir, data_file_name):
        tree = ClassTreePedict(map_cfg, model_dir)
        data_file = open(data_file_name, 'r')
        for line in data_file:
            line = line.strip()
            try:
                old_cate, cid_cate, name, brand, price = line.decode('u8').split(u'\t')
            except Exception,e :
                print >> sys.stderr, "Error:", line
                print >> sys.stderr, e
                sys.exit()
            cat_name = json.dumps(cid_cate.split(','))
            price = float(price)
            features = self.preprocess.process(name, cat_name, brand, price, level=0)
            #result = tree.predict(name, features, indexclass=u"root")
            indexclass = u'root'
            result = tree.predict(name, features, indexclass, price, cat_name)
            print "%s\t%s\t%s" %(result.encode('u8'), old_cate.encode('u8'), name.encode('u8'))
        data_file.close()
            

    def evaluation(self):
        self._train.train(self.train_features, self.train_labels)
        self._train.dump_model(self.model_path)
        self._predict.load_model(self.model_path)
        
        cate_cnt = dict()
        accuracy_cnt = 0
        all_cnt = 0

        for (features, label, name) in zip(self.test_features, self.test_labels, self.test_names):
            result = self._predict.predict(features)
            all_cnt += 1
            if all_cnt % 1000 == 0:
                print >> sys.stderr, "test %d samples ... " % all_cnt

            cate_key = label
            pred_key = result
            cate_key = cate_key.replace('#', '')
            pred_key = pred_key.replace('#', '')

            if cate_key not in cate_cnt:
                cate_cnt[cate_key] = {'cate': 0, 'pred':0, 'corr':0}

            if pred_key not in cate_cnt:
                cate_cnt[pred_key] = {'cate': 0, 'pred':0, 'corr':0}

            cate_cnt[cate_key]['cate'] += 1
            cate_cnt[pred_key]['pred'] += 1
            if cate_key == pred_key:
                cate_cnt[cate_key]['corr'] += 1
                accuracy_cnt += 1

        print "key\tcate_num\tpred_num\tcorrect_num\tprecision\trecall\tF_score"
        F_score_cnt = 0
        for key, vdic in cate_cnt.iteritems():
            cate_num = vdic['cate']
            pred_num = vdic['pred']
            corr_num = vdic['corr']
            if pred_num == 0 or cate_num == 0:
                print "%s\t%d\t%d\t%d" %(key.encode('utf-8'), cate_num, pred_num, corr_num)
            else:
                precision = corr_num*1.0/pred_num
                recall = corr_num*1.0/cate_num
                F_score = 0.0
                if (precision+recall) > 1e-3:
                    F_score = 2*precision*recall / (precision+recall)
                print "%s\t%d\t%d\t%d\t%.3f\t%.3f\t%.3f" %(key.encode('utf-8'), cate_num, pred_num, corr_num, precision, recall, F_score)
        print "accuracy: ", accuracy_cnt*1.0 / all_cnt 
        print "%d samples are used to train, %d samples are used to test" %(len(self.train_features), len(self.test_features))

    # level训练分类器类目的level
    def load_data_path(self, path, level=0, test_size_prob=0.0):
        if os.path.isdir(path):
            for file in os.listdir(path):
                t_path = os.path.join(path, file)
                self.load_data_path(t_path, level, test_size_prob)

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
                if self.cnt % 1000 == 0:
                    print >> sys.stderr, "load %d samples..." %self.cnt

                if cat_lst[0] in [u'服饰鞋帽', u'个人护理', u'母婴用品$']:
                    continue
                
                if test_size_prob >= 1.0:
                    is_train = False
                elif test_size_prob <= 0.0:
                    is_train = True
                else: 
                    if random.random() < test_size_prob:
                        is_train = False
                    else:
                        is_train = True
               
                if is_train:
                    features = self.preprocess.process(name, cat_name, brand, price, level=level)
                    self.train_features.append(features)
                    self.train_labels.append(labels)
                else:
                    features = self.preprocess.process(name)
                    self.test_features.append(features)
                    self.test_labels.append(labels)
                    self.test_names.append(name)
                # print json.dumps(features, ensure_ascii=False).encode('u8')
            fp.close()

    def classify(self, pid, name, brand, price):
        cat_name = json.dumps(pid.split(','))
        try:
            price = float(price)
        except:
            price = 0
        features = self.preprocess.process(name, cat_name, brand, price, level=0) 
        indexclass = u'root'
        return self._tree.predict(name, features, indexclass, price, cat_name)
        
    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            name = item_base.get("name", None)
            pid = item_base.get("pid", None)
            brand = u" ".join(item_base.get("brand", ""))
            price = item_base.get("price", 0)
            print "------------------------classiy_run enter   __call__"
            result_info = classify(name, pid, name, brand, price)
            print "--------------result_info: ",result_info
            item_profile["category_name_new"] = []
            item_profile["category_name_new"].extend(result_info[0])
            #item_profile["category_id_new"] = []
            #item_profile["category_id_new"].extend(result_info[1])
        except Exception as e:
            logging.error(traceback.print_exc())
            logging.error("category_name_new: %s", e)

            print "------------------------except:",e


        return {"status": 0}

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) < 4:
        print "usage: %s config_file train <data_path> \n\t\t test <data_path> \n\t\t evaluation <data_path>  \
                \n\t\t predict <data_path> <model_dir> \n\t\t testone <model_dir>"  % sys.argv[0]
        sys.exit()

    run = ClassifierRun(sys.argv[1])        
    if sys.argv[2] == 'train':
        run.load_data_path(sys.argv[3], level=run.level, test_size_prob=0.0)      
        logging.info('[Done] load %d data ....' %run.cnt )  
        run.train()
        logging.info('{Done} train')        

    elif sys.argv[2] == 'test':
        run.load_data_path(sys.argv[3], level=run.level, test_size_prob=1.0)
        logging.info('[Done] load %d  data ...'%run.cnt )
        run.test()
        logging.info('[Done] test')
    
    elif sys.argv[2] == 'evaluation':
        run.load_data_path(sys.argv[3], level=run.level, test_size_prob=run.test_size_prob)
        logging.info('[Done] load %d  data ...'%run.cnt )
        run.evaluation()
        logging.info('[Done] evaluation')
    
    elif sys.argv[2] == "predict":
        if len(sys.argv) < 5:
            print "Usage: %s config_file predict <data_file> <model_dir>" % sys.argv[0]
        data_file = sys.argv[3]
        model_dir = sys.argv[4]
        run.predict(run.cate_id_file, model_dir, data_file)
        logging.info('[Done] evaluation')
 
    elif sys.argv[2] == "testone":
        cid = u""
        name = u"婴之侣红外额式体温计id-h023"
        #name = u"t恤"
        brand = u""
        category = json.dumps([u"0"])
        price = 0
        model_dir = sys.argv[3]
        run.testone(name, category, brand, price)
                

