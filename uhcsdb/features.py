import os
import h5py
import pickle
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

from flask import current_app

keys = None
features = None
nneighs = None


def load_features(featuresfile, perplexity=40):
    keys, X = [], []

    cwd = os.getcwd()
    with h5py.File(featuresfile, 'r') as f:
        
        if 'tsne' in featuresfile:
            g = f['perplexity-{}'.format(perplexity)]
        else:
            g = f
            
        for key in g.keys():
            xx = g[key][...]
            keys.append(int(key))
            X.append(g[key][...])

    return keys, np.array(X)

def reload_features(featuresfile, keys, perplexity=40):
    X = []
    
    with h5py.File(featuresfile, 'r') as f:        
        if 'tsne' in featuresfile:
            g = f['perplexity-{}'.format(perplexity)]
        else:
            g = f
            
        for key in keys:
            xx = g[key][...]
            X.append(g[key][...])

    return np.array(X)


def build_search_tree(datadir, featurename='vgg16_block5_conv3-vlad-64.h5'):

    ndim = 64
    features_file = os.path.join(datadir, featurename)

    global keys, features
    keys, features = load_features(features_file)

    pca = PCA(n_components=ndim)
    features = pca.fit_transform(features)

    nn = NearestNeighbors()
    
    global nneighs
    nneighs = nn.fit(features)

def query(entry_id, n_results=16):
    scikit_id = keys.index(entry_id)
    query_vector = features[scikit_id]

    # nearest neighbor will be a self-match
    scores, results = nneighs.kneighbors([query_vector], n_results+1)
    scores, results = scores.flatten()[1:], results.flatten()[1:]
    
    result_entries = map(keys.__getitem__, results)
    scores = ['{:0.4f}'.format(score) for score in scores]

    return scores, result_entries

