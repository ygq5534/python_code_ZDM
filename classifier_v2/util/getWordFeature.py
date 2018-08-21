#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, os
import pickle

sys.path.append("../")

class FeaAnalysis(object):
    '''
        输出三级类目模型中使用的单词特征及权重
    '''
    def __init__(self):
        pass

    def load_model(self, model_file):
        print "load model:", model_file
        fp = open(model_file, "r")
        estimator, label_encoder = pickle.load(fp)
        fp.close()
        return (estimator, label_encoder)

    def getWordFeature(self, modelfile, wfile):
        features = {}
        (estimator, label_encoder) = self.load_model(modelfile)
        tmpdict = dict((v, k) for (k, v) in estimator.get_params()['vec'].vocabulary_.iteritems())
        # Weights assigned to the features (n_classes, n_features)
        tmpcoef = estimator.get_params()['clf'].coef_[0]
        # An index that selects the retained features from a feature vector
        tmpindex = estimator.get_params()['feat'].select_words.get_support(True)
        j = 0
        for i in tmpindex:
            features[tmpdict[i]] = tmpcoef[j]
            j = j + 1
        features = sorted(features.iteritems(), key=lambda x:x[1], reverse=True)

        featuresfile=open(wfile, "w")
        featuresfile.write("features count:"+str(len(features))+"\n")
        featuresfile.write(str(estimator.get_params()["clf"].intercept_)+"\n")
        featuresfile.write("\nword weight for the first class:\n")
        for f in features:
            featuresfile.write(f[0].encode('u8')+" "+str(f[1])+"\n")
        featuresfile.close()

    def analysis(self, model_path, w_path):
        if os.path.isdir(model_path):
            print "process direcotry ..."
            for file in os.listdir(model_path):
                t_path = os.path.join(model_path, file)
                w_file = os.path.join(w_path, file+".words")
                self.getWordFeature(t_path, w_file)
        elif os.path.isfile(model_path):
            print "process file..."
            self.getWordFeature(model_path, w_path)
        

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, "Usage: %s model-file out-file" %sys.argv[0]
        sys.exit()
    fa = FeaAnalysis()
    fa.analysis(sys.argv[1], sys.argv[2])
        


