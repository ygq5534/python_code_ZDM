# -*- coding: utf-8 -*-
import sys, traceback, os, logging
import jieba
import jieba.posseg as pseg
 
class Segmenter(object):
    def __init__(self):
        self.init()

    def init(self):
        jieba.initialize()
   
    def add_user_dict(self, user_dict_file):
        jieba.load_userdict(user_dict_file)
        logging.info('load user defined dictionary: %s' %user_dict_file)
        
    def segment(self, text):
        seg_list = jieba.cut(text)
        return list(seg_list)

    def cleanup(self):
        pass

    def segment_pos(self, text):
        words = pseg.cut(text)
        return list(words)

if __name__ == '__main__':
    segmenter = Segmenter()
    text = u'今天你开心吗?还好啦'
    text1 = u'【维阿露】 复方卡力孜然酊 （30毫升）'
    text2 = u't恤'
    for i in range(1):
        results = segmenter.segment(text2)
    for r in results: print r
    result_pos = segmenter.segment_pos(text2)
    print result_pos
    #words = segmenter.segment_pos(text2)
    #for w in words: print w.word, w.flag
    #segmenter.cleanup()

    if len(sys.argv) == 2:
        tfile = open(sys.argv[1], 'r')
        for line in tfile:
            fields = line.strip().split('\t')
            name = fields[1].decode('utf-8')
            words = segmenter.segment_pos(name)
            wlst = [w.word+"/"+w.flag for w in words]
            print fields[1], '  '.join(wlst).encode('utf-8')
        tfile.close()

