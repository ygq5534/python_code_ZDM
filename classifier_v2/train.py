#!/usr/bin/evn python
# -*- coding:utf-8 -*-

import sys, logging
from sklearn.linear_model import SGDClassifier
from feature.feature_word import WordFeature
from feature.feature_topic import TopicFeature

from sklearn.preprocessing  import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import BernoulliNB

try:
    import cPickle as pickle
except:
    import pickle

class Train(object):
    def __init__(self, vec_space='topic', params={}):
        self.label_encoder = LabelEncoder()
        if vec_space == 'topic':
            Feature = TopicFeature
        elif vec_space == 'word':
            Feature = WordFeature
         
        self.params = params
        self.pipeline = Pipeline([
                        ('vec',   DictVectorizer()),
                        ('feat',  Feature(user_params=params)),
                        ('clf',   LogisticRegression(penalty='l2', C=1.0, class_weight='auto'))
                        #('clf',   BernoulliNB(fit_prior=True))
                        #('clf',   SGDClassifier(shuffle=True))
                 ])

    def train(self, features, labels):
        y = self.label_encoder.fit_transform(labels)
        self.pipeline.fit(features, y)

    def grid_train(self, features, labels, cv=2, n_jobs=1, verbose=0):
        y = self.label_encoder.fit_transform(labels)
        k = self.params['select_k']
        param_grid = { 'feat__select_k': [k, k*2, k/2, k*3] }
        grids = GridSearchCV(estimator=self.pipeline, param_grid=param_grid, cv=cv, n_jobs=n_jobs, verbose=verbose)
        grids.fit(features, y)
        self.pipeline = grids.best_estimator_
        logging.info("best param", grids.best_params_)
        return grids.best_params_
 
    def dump_model(self, dumpfile):
        self.model = (self.pipeline, self.label_encoder)
        with open(dumpfile, 'wb') as f:
           pickle.dump(self.model, f)
    
