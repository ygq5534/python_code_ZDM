# coding=utf8
import re, json, sys, time, os
import ConfigParser

class WordLabel(object):
    '''
        将指定词语转化为相应的特征
    '''
    def __init__(self, cfg_file_name):
        self.cur_dir = os.path.dirname(os.path.abspath(cfg_file_name))
        self.config = ConfigParser.ConfigParser()
        self.cfg_parser(cfg_file_name)    
    
    def cfg_parser(self, cfg_file_name):
        self.config.read(cfg_file_name)
        
        section = "preprocess"
        area_word = u"(市|省|地区|林区|自治区)$"
        self.re_area = re.compile(area_word)
        self.area_lst = []
        self.load_words_lst(section, 'city_file', self.area_lst)

        self.area_out_lst = []
        self.load_words_lst(section, 'city_out_file', self.area_out_lst)

        self.color_lst = []
        self.load_words_lst(section, 'color_file', self.color_lst)

        self.quantifier_lst = []
        self.load_words_lst(section, 'quantifier_file', self.quantifier_lst)
        self.num_zh = []
        self.load_words_lst(section, 'num_zh_file', self.num_zh)
        num_word = ur"^\d+\.?\d*|[%s]+" % (u"".join(self.num_zh))
        self.re_num = re.compile(num_word)

    def load_words_lst(self, section ,option, words_lst):
        if self.config.has_option(section, option):
            value = self.config.get(section, option)
            filename = os.path.join(self.cur_dir, value)
            fp = open(filename, 'r') 
            for line in fp:
                if line.startswith('#'):
                    continue
                words_lst.append(line.rstrip().decode('utf-8')) 
            fp.close()

    # 地域
    def is_area(self, word):
        new_word = self.re_area.sub(u"", word)
        if new_word in self.area_lst:
            word = u"area__%s" % new_word
        elif new_word in self.area_out_lst:
            word = u"out__%s" % new_word
        return word

    # 颜色
    def is_color(self, word):
        if word in self.color_lst:
            return u"color__%s" % word.rstrip(u"色")
        new_word = word.rstrip(u"色")
        if new_word in self.color_lst:
            word = u"color__%s" % new_word
        return word

    # 量词
    def not_quantifier(self, word):
        brand = [u"361°", u"361度"]
        if word in brand:
            return True

    def is_quantifier(self, word, word0=None):
        if self.not_quantifier(word):
            return word
        if (word in self.quantifier_lst):
            if word0 and (not self.re_num.sub(u"", word0)):
                return u"qnt__%s" % word
            else:
                return word
        new_word = self.re_num.sub(u"", word)
        if new_word in self.quantifier_lst:
            word = u"qnt__%s" % new_word
        return word

    # 将特征词转化
    def word_label(self, word, word0=None):
        new_word = self.is_area(word)
        if new_word != word:
            return new_word
        new_word = self.is_color(word)
        if new_word != word:
            return new_word
        new_word = self.is_quantifier(word, word0)
        if new_word != word:
            return new_word
        return word

if __name__ == '__main__':
    test_file = "test_word_label"
    wl = WordLabel('../classifier.cfg')
    with open(test_file, "r") as f:
        for line in f:
            word = line.strip().decode("u8")
            print word, wl.word_label(word)

