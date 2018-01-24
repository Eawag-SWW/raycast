"""
Inspiration: http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html

Args:
 - retrain binary model with latest image samples
Writes:
 - settings for binary model
 - clusters reclassified with new model
"""

import os
import default_settings as s
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import pickle
import csv


def fit_classifiers(config, debug):
    clf_folder = os.path.join(config['iteration_directory'], s.general['iterations_structure']['fit'])

    for fold_i in range(s.general['folds']):
        print('-- FOLD {} --'.format(fold_i))
        # Read evaluated clusters
        cluster_file = os.path.join(config['iteration_directory'], s.general['iterations_structure']['evaluate'],
                                    '3dclusters_{}.csv'.format(fold_i))
        # Read training list
        training_list = pd.read_csv(os.path.join(s.general['working_directory'],
                               s.general['preparations_subdir'],
                               s.general['preparations_structure']['folds'],
                               'gt_train_{}.csv'.format(fold_i)))
        # read data
        data = pd.read_csv(cluster_file)

        # filter data with training set
        # select matches that are in training set
        data_true_train = data.loc[data.matched_id.isin(training_list.id)]
        # divide false alerts into

        # Get column names
        colnames = list(data.columns.values)
        # Get col names for explanatory variables
        colnames_expl = [c for c in colnames if c not in ['x', 'y', 'z', 'matched']]

        # Read data as arrays
        X = data.as_matrix(colnames_expl)
        y = data.as_matrix(['matched']).ravel()

        # create logistic regression model and train it
        classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=0.025, probability=True),
            SVC(gamma=2, C=1, probability=True),
            # GaussianProcessClassifier(1.0 * RBF(1.0)),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
            MLPClassifier(alpha=1),
            AdaBoostClassifier(),
            GaussianNB(),
            QuadraticDiscriminantAnalysis(),
            LogisticRegression()
        ]
        names = ["Nearest Neighbors",
                 "Linear SVM",
                 "RBF SVM",
                 # "Gaussian Process",
                 "Decision Tree",
                 "Random Forest",
                 "Neural Net",
                 "AdaBoost",
                 "Naive Bayes",
                 "QDA",
                 "LogisticRegression"]

        # iterate over classifiers
        for name, clf in zip(names, classifiers):
            clf.fit(X, y)
            score = clf.score(X, y)
            print('Detection score for {n}:  {s}'.format(n=name, s=score))

            # Write model to file
            clf_file = os.path.join(clf_folder, '{}_{}.pkl'.format(name, fold_i))
            with open(clf_file, 'wb') as fid:
                pickle.dump(clf, fid)

    return 0
