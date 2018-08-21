#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import sys, os, json, logging, random, time, traceback
from multiprocessing import Process
from preprocess.preprocess import Preprocess
from train import Train
from predict import Predict
from util.sample_adjust import SampleAdjust

class EvalNode(Process):
    def __init__(self, cfg_file_name, test_size_prob, data_dir, model_dir, model_name, level, dump_file=False, has_feat=False, max_num=0, min_num=0):
        Process.__init__(self)
        self.preprocess = Preprocess(cfg_file_name)
        self.test_size_prob = test_size_prob
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.model_name = model_name
        self.level = level

        self.cnt = 0
        self.train_features = []
        self.train_labels = []
        self.test_features = []
        self.test_labels = [] 
        self.test_lines = []
        self.train_lines = []
        self.dump_file = dump_file
        self.has_feat = has_feat
        self.load_label = True        

        if max_num != 0 and min_num != 0:
            self.sample_adjust = SampleAdjust(min_num, max_num, seed=20)
    
        #self.cate_trans = {u'运动户外$女装':[u'服装配饰'], u'运动户外$男装':[u'服装配饰'], u'运动户外$运动女鞋':[u'鞋'], u'运动户外$运动男鞋':[u'鞋'], u'运动户外$户外鞋':[u'鞋'], u'母婴用品$童装':[u'服装配饰'], u'母婴用品$宝宝洗护':[u'个护化妆']}

    def cate_lst_transform(self, cate_lst):
        key  = u'$'.join(cate_lst[:2])
        if key in self.cate_trans:
            return self.cate_trans[cate_lst]
        else:
            return cate_lst

    # level训练分类器类目的level
    def load_data_path(self, path, level=0, test_size_prob=0.0, has_feat=False):
        if os.path.isdir(path):
            for file in os.listdir(path):
                t_path = os.path.join(path, file)
                self.load_data_path(t_path, level, test_size_prob, has_feat)

        elif os.path.isfile(path):
            if has_feat and not path.endswith("feature"):
                return
            fp = open(path, 'r')
            for line in fp:
                line = line.strip('\n')
                fields = line.split('\t')
                try:
                    cat_name = fields[0].decode('u8')
                    name = fields[1].decode('u8')
                    if len(fields) > 3:
                        brand = fields[2].decode('u8')
                        price = fields[3]
                    else:
                        brand = u''
                        price = 0
                    if has_feat:
                        features = json.loads(fields[-1])
                        if not isinstance(features, dict):
                            print >> sys.stderr, "Error:", line 
                            continue
                    #cat_name, name, brand, price = line.split('\t')
                    #cat_name, name, feats = line.strip('\n').split('\t')
                    cat_lst = json.loads(cat_name)

                    #######################
                    # 类别替换
                    #cat_lst = self.cate_lst_transform(cat_lst)
                    ######################

                    if len(cat_lst) < level+1:
                        continue
                    labels = u'$'.join(cat_lst[:level+1])
                except Exception, e:
                    print >> sys.stderr, "Error:", line
                    print >> sys.stderr, e
                    traceback.print_exc()
                    continue
                self.cnt += 1
                if self.cnt % 10000 == 0:
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
                    if not has_feat:
                        if self.load_label:
                            features = self.preprocess.process(name, cat_name, brand, price, level=level)
                        else:
                            features = self.preprocess.process(name, u"[]" ,brand, price)
                    if len(features) == 0:
                        continue
                    # 是否平衡训练样本的数量
                    if hasattr(self, 'sample_adjust'):
                        self.sample_adjust.add_sample(features, labels)
                    else:
                        self.train_features.append(features)
                        self.train_labels.append(labels)
                    # 是否将训练集输出到文件
                    if self.dump_file:
                        self.train_lines.append(line)
                else:
                    if not has_feat:
                        features = self.preprocess.process(name)
                    self.test_features.append(features)
                    self.test_labels.append(labels)
                    #self.test_names.append(name)
                    self.test_lines.append(line)
                # print json.dumps(features, ensure_ascii=False).encode('u8')
            fp.close()    

    def evaluation(self, model_path, eval_file, predict_file, badcase_file):
        print "%d samples are used to train, %d samples are used to test" %(len(self.train_features), len(self.test_features))
        _predict = Predict()
        _predict.load_model(model_path)
        #report = classification_report(self.test_labels, self._predict.predict(self.test_features)) 
        efile = open(eval_file, 'w+')
        pfile = open(predict_file, 'w') 
        bfile = open(badcase_file, 'w')    
        cate_cnt = dict()
        accuracy_cnt = 0
        all_cnt = 0
        print "******************"
        for features, label, line in zip(self.test_features, self.test_labels, self.test_lines):
            result = _predict.predict(features)
            #print result.encode('u8'), label.encode('u8'), name.encode('u8')
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
            print >> pfile, "%s\t%s" %(result.encode('u8'), line)             

            if cate_key == pred_key:
                cate_cnt[cate_key]['corr'] += 1
                accuracy_cnt += 1
            else:
                print >> bfile, "%s\t%s\t%s" %(result.encode('u8'), line, json.dumps(features, ensure_ascii=False).encode('u8'))

        print >> efile, "key\tcate_num\tpred_num\tcorrect_num\tprecision\trecall\tF_score"
        F_score_cnt = 0
        for key, vdic in cate_cnt.iteritems():
            cate_num = vdic['cate']
            pred_num = vdic['pred']
            corr_num = vdic['corr']
            if pred_num == 0 or cate_num == 0:
                print >> efile, "%s\t%d\t%d\t%d" %(key.encode('utf-8'), cate_num, pred_num, corr_num)
            else:
                precision = corr_num*1.0/pred_num
                recall = corr_num*1.0/cate_num
                F_score = 0.0
                if (precision+recall) > 1e-3:
                    F_score = 2*precision*recall / (precision+recall)
                print >> efile, "%s\t%d\t%d\t%d\t%.3f\t%.3f\t%.3f" %(key.encode('utf-8'), cate_num, pred_num, corr_num, precision, recall, F_score)
        print >> efile, "accuracy: ", accuracy_cnt*1.0 / all_cnt 
        print >> efile, "%d samples are used to train, %d samples are used to test" %(len(self.train_features), len(self.test_features))
        efile.close()
        pfile.close()
        bfile.close()

    def run(self):
        self.load_data_path(self.data_dir, self.level, self.test_size_prob, self.has_feat)
        if hasattr(self, 'sample_adjust'):
            (self.train_features, self.train_labels) = self.sample_adjust.get_all_samples(over_sampling=False)
            self.sample_adjust.clear()

        print >> sys.stderr, "load samples" , self.cnt
        if (len(set(self.train_labels))) <= 1:
            logging.error("same label: %s" %self.train_labels[0].encode('u8'))
            return

        if self.dump_file:
            train_file_name = os.path.join(self.model_dir, "train/"+self.model_name+".train")
            train_file = open(train_file_name, 'w')
            for line, features in zip(self.train_lines, self.train_features):
                print >> train_file, "%s\t%s" %(line, json.dumps(features,ensure_ascii=False).encode('u8'))
            train_file.close()
                
            test_file_name = os.path.join(self.model_dir, "test/"+self.model_name+".test")
            test_file = open(test_file_name, 'w')
            for line, features in zip(self.test_lines, self.test_features):
                print >> test_file, "%s\t%s" %(line, json.dumps(features,ensure_ascii=False).encode('u8'))
            test_file.close()

        print >> sys.stderr, "train the model", self.data_dir

        if self.level == 0:
            space = 'topic'
            params = {'n_topics': 50}
            _train = Train(space, params)
            _train.train(self.train_features, self.train_labels)
        elif self.level == 1:
            space = 'topic'
            len_child = len(os.listdir(self.data_dir))+5
            params = {'n_topics': len_child}
            _train = Train(space, params)
            _train.train(self.train_features, self.train_labels)
            print self.data_dir, "topic num:", len_child
        else:
            space = 'word'
            len_k = len(os.listdir(self.data_dir))*20+ 30
            #params = {"select_k": len_k}
            #_train = Train(space, params)
            _train = Train(space, {})
            _train.train(self.train_features, self.train_labels)
            #best_params = _train.grid_train(self.train_features, self.train_labels, cv=2, n_jobs=1, verbose=5)
            #print self.data_dir, "k:", len_k, "best params:", best_params

        model_path = os.path.join(self.model_dir, 'model/'+self.model_name+".model")
        print >> sys.stderr, "dump the model", model_path
        _train.dump_model(model_path)

        eval_file =  os.path.join(self.model_dir, 'report/'+self.model_name+".report")
        predict_file = os.path.join(self.model_dir, 'predict/'+self.model_name+".predict")
        badcase_file = os.path.join(self.model_dir, 'bad_case/'+self.model_name+".badcase")        

        self.evaluation(model_path, eval_file, predict_file, badcase_file)
        print >> sys.stderr, "Done %s" %self.data_dir
    
       
def train_all(cfg_file_name, test_size_prob, data_dir, model_dir, model_name, level):
        
    for file in os.listdir(data_dir):
        t_path = os.path.join(data_dir, file)
        if os.path.isdir(t_path):
            train_all(cfg_file_name, test_size_prob, t_path, model_dir, file, level+1)

    if model_name != 'root': 
        return
    # if level != 2:
    #    return
    print >> sys.stderr, "start:", model_name
    if level == 0:
        max = 10000
        min = 10000 
    elif level == 1:
        max = 0
        min = 0
    elif level == 2:
        max = 5000
        min = 4000

    en = EvalNode(cfg_file_name, test_size_prob, data_dir, model_dir, model_name, level, dump_file=False, has_feat=False, max_num=max, min_num=min)

    # 训练时是否加入标签
    en.load_label = False

    a = random.randint(0, 40)
    time.sleep(a)
    print >> sys.stderr, "now to start"
    en.start()
    #en.run()
    

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    if len(sys.argv) < 4:
        print >> sys.stderr, "Usage: %s config_file data_dir model_dir" %sys.argv[0]
        sys.exit()
    config_file = sys.argv[1]
    data_dir = sys.argv[2]
    model_dir = sys.argv[3]
    train_all(config_file, 0.1, data_dir, model_dir, 'root', 0)
    # train_all(config_file, 0.1, data_dir, model_dir, 'data_train_test', 1)
