#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, logging, json, os

try:
    import cPickle as pickle
except:
    import pickle

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir)

class Predict(object):
    def __init__(self):
        pass

    def load_model(self, model_file):
        fp = open(model_file, "r")
        (self.pipeline, self.label_encoder) = pickle.load(fp)
        fp.close()

    def predict(self, features):
        result = ''
        try:
            target = self.pipeline.predict(features)
            result = self.label_encoder.classes_[target[0]]
        except Exception, e:
            logging.error("Error: %s" %json.dumps(features, ensure_ascii=False).encode('u8') )
            logging.error(e)
        return result

    def predict_prob_one(self, features):
        decision = self.pipeline.decision_function(features)
        if decision.ndim == 1:
            df = [0, decision.item()]
            args = [0, 1] if df[1] > 0 else [1, 0]
        else:
            df = decision.tolist()[0]
            args = decision.argsort().tolist()[0]
        args.reverse()
