# -*- coding: utf8
#author:fangshu.chang

"""
本代码的目的：
1，加载类目配置
2，加载模型对象和规则对象
3，输入预处理的文本和原始文本串，返回品类
"""

import json
import sys
import os
import logging
import traceback

try:
    import cPickle as pickle
except:
    import pickle

from predict import Predict
from rule import Rule
from module import Module
from preprocess.preprocess import Preprocess
import ConfigParser

class ClassTreePedict():
    def __init__(self,cfgfile,modeldir):
        #类目配置文件
        self.cfgfile=cfgfile
        #放置模型的根目录
        self.modeldir=modeldir
        #存放映射的字典
        self.mapclass={}
        #类目索引字典
        self.indexclass={}
        #存放策略的字典
        self.predictPolicy={}

        self.mapLoad()
        self.modelsLoad()
    
    #加载映射
    def mapLoad(self):
        infile=open(self.cfgfile,"r")
        indata=infile.readlines()
        indata = ' '.join(indata) 
        self.mapclass=json.loads(indata)
        infile.close()
        logging.info('[Done] load category id map')
    
    #类目中加载模型，建立类目索引
    def modelsLoad(self):
        filelist=os.listdir(self.modeldir)
        for f in filelist:
            path = os.path.join(self.modeldir, f)
            id=f.split(".")[0]
            policy=f.split(".")[1]
            if policy == 'model':
                # 初始化 Predict 对象
                pred = Predict()
                pred.load_model(path)           
                self.indexclass[id]= pred
            else:
                # 初始化 Rule 对象
                rule = Rule()
                rule.load_rule(path) 
                self.indexclass[id] = rule
                logging.debug("load rule file " + id)
            self.predictPolicy[id]=policy
        logging.info('[Done] load all models')
   
    #indexclass是类目的中文名称
    def predict(self, text, feature, indexclass=u"root", price=0, pid=u''):
        pre_result = u''
        #index = self.mapclass[indexclass]
        index = indexclass
        while self.indexclass.has_key(index):
            if self.predictPolicy[index] == "model":
                # 使用模型分类
                result = self.indexclass[index].predict(feature)
                #print "model result****", result
            elif self.predictPolicy[index] == "rule":
                # 使用规则匹配商品标题
                result = self.indexclass[index].predict(text, price)
                #print "rule result****", result
            else:
                # 使用规则匹配一方类
                if pid:
                    try:
                        cat = json.loads(pid)
                        client_cate = u'$'.join(cat)
                    except Exception, e:
                        logging.error("proc client category error, %s", e)
                        client_cate = u''

                    if self.predictPolicy[index] == "cate":
                        # 仅仅匹配一方类目
                        match_text = client_cate
                    else:
                        # 匹配一方类目 + 商品标题
                        match_text = client_cate + u" " + text
                else:
                    match_text = text
                
                #print "****", match_text
                result = self.indexclass[index].predict(match_text, price)
               
            if result not in self.mapclass:
                logging.warning("%s is not in categories" %result.encode('u8'))
                if result == u'' and pre_result != u'root':
                    result = pre_result
                break
            pre_result = result
            index = self.mapclass[result]
            #print "predict index****", index
        return result

class Classifier(Module):
    def __init__(self, context):
        super(Classifier, self).__init__(context)
        logging.info("Classifier module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        model_dir = cur_dir + "/model"
        #model_dir = "/home/fenghua.huang/classifier_v2/model"
        map_file = cur_dir + "/resource/cate_id.cfg"
        cfg_file = cur_dir + "/classifier.cfg"
        cid_field_file = cur_dir + "/resource/fields.cfg"
        self.cid_fields = dict() #部分cid的字段要特别处理

        self.resource_process(model_dir, cfg_file, map_file, cid_field_file)
        self.classifier = ClassTreePedict(map_file, model_dir)
        self.preprocess = Preprocess(cfg_file)
        self.start_node= self.get_start_node(cfg_file)

    def get_start_node(self, cfg_file):
        # 开始分类的节点，默认是根节点 u'root'
        # 如使用类目映射，可在 u'root'节点前增加一个节点，使用规则跳到相应节点
        start_node = u'root'
        self.config = ConfigParser.ConfigParser()
        self.config.read(cfg_file)
        section = 'default'
        if self.config.has_option(section, 'start_node'):
            start_node = self.config.get(section, 'start_node')
            start_node = start_node.decode('u8')
        return start_node
        
    def classify(self, cid, name, pid, brand, price):
        features = self.preprocess.process(name, pid, brand, price)
        #print json.dumps(features, ensure_ascii=False).encode('u8')
        result = self.classifier.predict(name, features, self.start_node, price, pid)
        return result

    def load_field_file(self, field_file):
        ''' 读取配置文件(cid对应的需要合并的字段) '''
        with open(field_file, 'r') as rf:
            for line in rf:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    cid, ori_field, dest_field = line.split('#') 
                    fields_lst = self.cid_fields.setdefault(cid, [])
                    fields_lst.append((ori_field, dest_field))
                except:
                    logging.error("wrong field config line: %s" %line)
            logging.info("load file %s done" %field_file)
    
    def chg_cid_fields(self, item_base):
        '''
            用于部分字段的调整
            主要用于，对于某个cid，需要将subtitle的值合并到name中
        '''
        cid = item_base['cid']
        if cid in self.cid_fields:
            for (ori_field, dest_field) in self.cid_fields[cid]:
                if ori_field in item_base and dest_field in item_base:
                    if isinstance(item_base[ori_field], unicode) and isinstance(item_base[dest_field], unicode):
                        item_base[dest_field] += ' '
                        item_base[dest_field] += item_base[ori_field]
                    if isinstance(item_base[ori_field], unicode) and isinstance(item_base[dest_field], list):
                        item_base[dest_field].append(item_base[ori_field])
                        
                    if isinstance(item_base[ori_field], list) and isinstance(item_base[dest_field], list):             
                        item_base[dest_field].extend(item_base[ori_field])
                    if isinstance(item_base[ori_field], list) and isinstance(item_base[dest_field], unicode):
                        item_base[dest_field] += ' '
                        item_base[dest_field] += ' '.join(item_base[ori_field])

    def __call__(self,item_base,item_profile):
        try:
            self.chg_cid_fields(item_base)

            cid = item_base["cid"]
            name=item_base.get("name",None)
            pid=item_base.get("pid",None)
            brand=u" ".join(item_base.get("brand", ""))
            cat=[]
            cat.extend(pid)
            cat_str=json.dumps(cat)
            price=item_base.get("price",0)
             
            result=self.classify(cid, name, cat_str, brand, price)
            result = result.split(u'$')

            item_profile["category_name_new"]=[]
            item_profile["category_name_new"].extend(result)
            item_profile["category_id_new"]=[]
            
            ids = []
            for i in range(len(result)):
                key = '$'.join(result[:i+1])
                if key in self.classifier.mapclass:
                    ids.append(int(self.classifier.mapclass[key]))
                else:
                    logging.error("find category id error, key: %s" %key.encode('u8'))
            item_profile["category_id_new"] = ids
            #item_profile["category_id_new"].extend(map(lambda x:self.classifier.mapclass[x], result.split("$")))
        except Exception as e:
            logging.error(traceback.print_exc())
            logging.error("category_name: %s", e)
        return {"status":0}

    def resource_process(self, model_dir, cfg_file, map_file, cid_field_file):
        self.add_resource_file(model_dir)
        self.add_resource_file(cfg_file)
        self.add_resource_file(map_file)
        self.load_field_file(cid_field_file)
        self.add_resource_file(cid_field_file)

    def test(self):
        cid = u"Cjianyi"
	# name = u"迪士尼（Disney）米妮K金镶钻手机链读卡器 (短)"
	# name = u"佳能（Canon）CL-97彩色墨盒 （适用佳能E568）"
	# name = u"东芝（TOSHIBA) 32A150C 32英寸 高清液晶电视（黑色）"
	# name = u"东芝（TOSHIBA） 55X1000C 55寸 全高清3D LED液晶电视"
	# name = u"东芝（TOSHIBA）42寸液晶电视42A3000C"
	name = u"三星（SAMSUNG）M55 黑色墨盒（适用SF-350）"
	brand = u""
        #cate = u""
        category = json.dumps([u"0"])
        price = -1
        logging.info("start to test")
        print self.classify(cid, name, category, brand, price)        
        '''
        category = []
        #1（id）、4（name）、5（price）、14（brand）、7/9/11 （cate）
        for line in open("test.dat"):
            line = line.strip('\n')
            fields = line.split(',')
            iid = fields[0].decode('u8')
            name = fields[3].decode('u8')
            price = fields[4]
            cate1 = fields[6].decode('u8')
            cate2 = fields[8].decode('u8')
            cate3 = fields[10].decode('u8')
            brand = fields[13].decode('u8')
            category.append(cate1)
            category.append(cate2)
            category.append(cate3)
            cate = json.dumps(category)
            name_new = '%s%s%s' % (cate1, cate2, name)
            predictCate = self.classify(cid, name_new, cate, brand, price)
            print("%s\t%s\t%s\t%s$%s$%s\t%s\t%s" % (iid.encode('u8'),name_new.encode('u8'),price,category[0].encode('u8'),category[1].encode('u8'),
                  category[2].encode('u8'),brand.encode('u8'),predictCate.encode('u8')))
            del category[:]
        print self.classify(cid, name, category, brand, price)        
        '''
        
if __name__=="__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    test = Classifier(None)
    test.test()

