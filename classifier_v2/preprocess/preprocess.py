#!/usr/bin/env python
#! -*- coding:utf-8 -*-

import sys, os, logging, re, json, math
from segment_jieba import Segmenter
from word_label import WordLabel

import ConfigParser


reload(sys)
sys.setdefaultencoding('utf-8')


class Preprocess(object):
    def __init__(self, cfg_file_name):
        self.config = ConfigParser.ConfigParser()
        self.cur_dir = os.path.dirname(os.path.abspath(cfg_file_name))
        self.segmenter = Segmenter()
        self.cfg_parser(cfg_file_name)

    def cfg_parser(self, cfg_file_name):
        self.config.read(cfg_file_name)
        
        section = 'segmenter'
        for (key, value) in self.config.items(section):
            if key.startswith('user_dict'):
                dict_name = os.path.join(self.cur_dir, value)
                self.segmenter.add_user_dict(dict_name)

        section = 'preprocess'
        self.stop_words = set()
        self.load_option_words(section, 'stop_file', self.stop_words)

        self.reserve_words = set()
        self.load_option_words(section, 'reserve_file', self.reserve_words)

        self.med_words = set()
        self.load_option_words(section, 'medicine_file', self.med_words)

        self.word_label = WordLabel(cfg_file_name)

        self.replace_lst = [(u'斜跨包', u'斜挎包'), (u'!', u','), (u'！', u','), (u'。', u','), (u'，', u','),
                (u'市场价', u''), (u'全国包邮', u''), (u'包邮', u''), (u'【', u''),
                (u'】', u''), (u'[', u''), (u']', u''), (u'《', u''), (u'》', u'')]

    def load_option_words(self, section, option, word_set):
        if self.config.has_option(section, option):
            value = self.config.get(section, option)
            filename = os.path.join(self.cur_dir, value)
            fp = open(filename, 'r') 
            for line in fp:
                if line.startswith('#'):
                    continue
                word_set.add(line.rstrip().split()[0].decode('utf-8'))
            logging.info("load words %s" %filename)
            fp.close()

    def check_is_mode(self, word):
        has_hyphen = False
        for c in word:
            if c == u'-':
                has_hyphen = True
            if (c < u'a' and c > u'z') and (c < u'0' and c > u'9'):
                return False
        return has_hyphen

    # 检查特征单词是否有效
    def check_valid(self, word):
        if word in self.reserve_words:
            return True
        if not word:
            return False
        if word.isnumeric():
            return False
        # unicode 编码无法使用 isalnum()
        if word.encode("u8").isalnum() and len(word) <= 3:
            return False
    #    if len(word) == 1 and ord(word) < 256:
        if len(word) == 1:
            return False
        if word in self.stop_words:
            return False
        if self.check_is_mode(word):
            return False
        try:
            float(word)
            return False
        except:
            pass
        return True

    def convert_word_features(self, text):
        #words = self.segmenter.segment(text.lower().strip())
        words = self.segmenter.segment(text.strip())
        features = {}

        word0 = ""
        for word in words:
            word = word.strip().replace(u'（', u'').replace(u'）', u'').replace(u'(', u'').replace(u')', u'')
            if not word:
                continue
            word = self.word_label.word_label(word, word0)
            word0 = word
            if not self.check_valid(word):
                continue
            features[word] = 1
        return features

    # 将 数据 转为字典特征, level为训练类目节点的level，root: level=0
    def process(self, name, category=u'', brand=u'', price=0, level=0):
        category_new = self.feat_category(category, level)
        brand_new = self.feat_brand(brand)

        text = name.decode('utf-8') + u' ' + category_new.decode("utf-8") + u' ' + brand_new.decode("utf-8")
        text = self.extract_sentence(text)
       
        features = self.convert_word_features(text)
        self.add_price_feature(features, price)

        self.transform_area(features)
        self.add_med_feat(features)

        return features       

    # 处理客户类目数据
    def feat_category(self, category, level=0):
        if category and category != u'':
            cat = json.loads(category)
            category_new = u' '.join(cat[level:])
        else:
            category_new = u''
        return category_new

    # 处处理品牌数据
    def feat_brand(self, brand):
        if not brand or brand == u'None' or brand == u'Null' or brand == u'empty' or brand.endswith(u'公司'):
            return u''
        elif brand.find(u'["') != -1:
            brand = brand.replace(u'[',u'').replace(u']',u'').replace(u'"',u'')        
        return brand
    
    def add_price_feature(self, features, price):
        if type(price) is str:
            try:
                price = float(price)
            except:
                price = 0

        if price >= 10000:
            feature_price = u'price_%d' % int(round(math.log10(price)))
            features[feature_price] = 1        

    def extract_sentence(self, text):            
        for (ostr, rstr) in self.replace_lst:
            text = text.replace(ostr, rstr)
        text = re.sub(u'仅[0-9.]*元', u'', text)
        text = re.sub(u'仅售[0-9.]*元', u'', text).replace(u'仅售', u'')
        sentences = text.split(u',')
        if len(sentences) < 4:
            return text
        results = []
        for sentence in sentences:
            results.append(sentence)
            if len(sentence.encode('utf-8')) > 45:
                break
        #if (text.find(u'女') != -1 or text.find(u'裙') != -1 or text.find(u'美腿') != -1 ) and text.find(u'男') == -1:
        #    results.append(u'女')
        #elif text.find(u'男') != -1 and (text.find(u'女') == 1 and text.find(u'裙') == -1 and text.find(u'美腿') == -1 ):
        #    results.append(u'男')
        return u' '.join(results)

    def transform_area(self, word_feats):
        to_delete = []
        area_cnt = 0
        out_cnt = 0
        for word, value in word_feats.iteritems():
            if word.startswith('color__'):
                to_delete.append(word)
            elif word.startswith('area__'):
                to_delete.append(word)
                area_cnt += 1
            elif word.startswith('out__'):
                to_delete.append(word)
                out_cnt += 1

        for key in to_delete:
            del word_feats[key]       

        if area_cnt != 0:
            word_feats["area__%d" % area_cnt] = 1 
        if out_cnt != 0:
            word_feats["out__%d" % out_cnt] = 1

    def add_med_feat(self, word_feats):
        for word, value in word_feats.iteritems():
            if word in self.med_words:
                word_feats['_YIYAO_'] = 1
                break

# Preprocess加载字典多，对象只创建一次，麻烦的是还需要先传配置文件地址
#try:
#    type(eval(cfg_file_name))
#except:
#    cur_dir = os.path.dirname(os.path.abspath(__file__)) 
#    cfg_file_name = cur_dir + '/../classifier.cfg'
#    logging.warn("global cfg_file_name is not defined, relocate it in %s" %cfg_file_name)
#preprocess = Preprocess(cfg_file_name)

if __name__ == '__main__':
    preprocess = Preprocess('../classifier.cfg')
    features = preprocess.process(u'T恤二件', u'', u'', 1000000)
    print json.dumps(features, ensure_ascii=False).encode('utf-8')

