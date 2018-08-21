#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, os, random

class SampleAdjust(object):
    '''
        使用 oversampling 和 undersampling 来调整样本参数
    '''
    def __init__(self, min, max, seed=0):
        if max < min:
            raise ValueError('%s max value must be larger than min value' %(self.__class__.__name__))

        self.features = {}
        self.labels = {}
        # 样本最小数量，不足采用重采样
        self.min = min
        # 样本最大数量，如多则采用蓄水池采样
        self.max = max
        self.cnt = {}
        random.seed(seed)

    def add_sample(self, feature, label):
        self.features.setdefault(label, [])
        self.labels.setdefault(label, [])
        self.cnt.setdefault(label, 0)
        features = self.features[label]
        labels = self.labels[label]        

        self.cnt[label] += 1
        cnt = self.cnt[label]
        i = len(features)
        if i < self.max:
            features.append(feature)
            labels.append(label)
            return

        replace_ri = random.randint(0, cnt)
        if replace_ri < self.max:        
            features[replace_ri] = feature
            labels[replace_ri] = label  

    def over_sampling(self, features, labels):
        size = len(features)
        while size < self.min:
            t = random.randint(0, size-1)
            features.append(features[t].copy())
            labels.append(labels[t])
            size += 1

    def get_all_samples(self, shuffle=False, over_sampling=True):
        features = []
        labels = []
        for label in self.features.keys():
            if over_sampling:
                self.over_sampling(self.features[label], self.labels[label])
            features.extend(self.features[label])
            labels.extend(self.labels[label])
        return (features, labels)

    def clear(self):
        self.features.clear()
        self.labels.clear()

def test():
    sa = SampleAdjust(3, 3, seed=20)
    sa.add_sample({'a':1}, 1) 
    sa.add_sample({'a':3}, 1) 
    sa.add_sample({'b':1}, 2)
    sa.add_sample({'a':4}, 1) 
    sa.add_sample({'b':2}, 2)
    sa.add_sample({'a':2}, 1) 
        
    a ,b = sa.get_all_samples(over_sampling=False)
    print a
    print b
    sa.clear()

if __name__ == '__main__':
    test()
        


