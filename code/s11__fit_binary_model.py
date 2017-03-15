"""
Args:
 - retrain binary model with latest image samples
Writes:
 - settings for binary model
"""

import os
import default_settings as s
import numpy as np
from sklearn import linear_model as sklim
import pickle


def fit_binary_model(config, debug):

    model_out_file = os.path.join(config['iteration_directory'], s.general['iterations_structure']['fit'],
                                'logistic_regression.pkl')

    # Read evaluated clusters
    cluster_file = os.path.join(config['iteration_directory'], s.general['iterations_structure']['evaluate'],
                                '3dclusters_evaluated.csv')

    with open(cluster_file, 'rb') as f:
        X = np.loadtxt(f, skiprows=1, usecols=(0, 1, 3, 4, 7))
    with open(cluster_file, 'rb') as f:
        Y = np.loadtxt(f, skiprows=1, usecols=2)

    # create logistic regression model and train it
    logRegModel = sklim.LogisticRegression()
    logRegModel.fit(X, Y)
    score = logRegModel.score(X, Y)
    print 'Detection score of clusters is %s' % score

    with open(model_out_file, 'wb') as fid:
        pickle.dump(logRegModel, fid)

    return 1
