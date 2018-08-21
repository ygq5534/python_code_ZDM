# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 18:04:18 2018

@author: yangguoqiang
"""

import sys
import tushare as ts
import numpy as np
import pandas as pd
# from sklearn.externals.six.moves.urllib.request import urlopen
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from sklearn import cluster, covariance, manifold


from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题



hs300 = ts.get_hs300s()
hs300_name = hs300.name

hs300_code = hs300.code
#print(hs300_code)
df_hs300 = pd.DataFrame()
names = []
for i in range(298):
#    try:
    df = ts.get_hist_data(hs300_code[i],start='2017-07-23',end='2018-07-23')
    #print(str(hs300_code[i])+':'+str(df.shape))
        #print(df)
    if df.shape == (245,13):
        df_hs300[str(hs300_code[i])] = df['price_change']
        names.append(hs300_name[i])
#    except:
#        print('出现未知错误')
names = np.array(names)
variation = np.array(df_hs300)
#print(variation)
#print(df_hs300)
X = variation.copy()
X /= X.std(axis=0)
edge_model = covariance.GraphLassoCV()  #构建稀疏协方差逆矩阵
edge_model.fit(X)


_,labels = cluster.affinity_propagation(edge_model.covariance_)#进行聚类
n_labels = labels.max()

for i in range(n_labels + 1):
   # print('Cluster %i: %s' % ((i + 1), ', '.join(names[labels == i])))
    print('Cluster'+str(i+1)+','.join(names[labels == i]))

node_position_model = manifold.LocallyLinearEmbedding(
        n_components=2,eigen_solver='dense',n_neighbors=6)

embedding = node_position_model.fit_transform(X.T).T



plt.figure(1, facecolor='w', figsize=(10, 8))
plt.clf()
ax = plt.axes([0., 0., 1., 1.])
plt.axis('off')

# Display a graph of the partial correlations
partial_correlations = edge_model.precision_.copy()
d = 1 / np.sqrt(np.diag(partial_correlations))
partial_correlations *= d
partial_correlations *= d[:, np.newaxis]
non_zero = (np.abs(np.triu(partial_correlations, k=1)) > 0.02)

# Plot the nodes using the coordinates of our embedding
plt.scatter(embedding[0], embedding[1], s=100 * d ** 2, c=labels,
            cmap=plt.cm.nipy_spectral)

# Plot the edges
start_idx, end_idx = np.where(non_zero)
# a sequence of (*line0*, *line1*, *line2*), where::
#            linen = (x0, y0), (x1, y1), ... (xm, ym)
segments = [[embedding[:, start], embedding[:, stop]]
            for start, stop in zip(start_idx, end_idx)]
values = np.abs(partial_correlations[non_zero])
lc = LineCollection(segments,
                    zorder=0, cmap=plt.cm.hot_r,
                    norm=plt.Normalize(0, .7 * values.max()))
lc.set_array(values)
lc.set_linewidths(15 * values)
ax.add_collection(lc)

# Add a label to each node. The challenge here is that we want to
# position the labels to avoid overlap with other labels
for index, (name, label, (x, y)) in enumerate(
        zip(names, labels, embedding.T)):

    dx = x - embedding[0]
    dx[index] = 1
    dy = y - embedding[1]
    dy[index] = 1
    this_dx = dx[np.argmin(np.abs(dy))]
    this_dy = dy[np.argmin(np.abs(dx))]
    if this_dx > 0:
        horizontalalignment = 'left'
        x = x + .002
    else:
        horizontalalignment = 'right'
        x = x - .002
    if this_dy > 0:
        verticalalignment = 'bottom'
        y = y + .002
    else:
        verticalalignment = 'top'
        y = y - .002
    plt.text(x, y, name, size=10,
             horizontalalignment=horizontalalignment,
             verticalalignment=verticalalignment,
             bbox=dict(facecolor='w',
                       edgecolor=plt.cm.nipy_spectral(label / float(n_labels)),
                       alpha=.6))

plt.xlim(embedding[0].min() - .15 * embedding[0].ptp(),
         embedding[0].max() + .10 * embedding[0].ptp(),)
plt.ylim(embedding[1].min() - .03 * embedding[1].ptp(),
         embedding[1].max() + .03 * embedding[1].ptp())

plt.show()
plt.savefig('plot_hs300.png',dpi = 500)