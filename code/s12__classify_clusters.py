"""
Classify clusters probabilistically, and add missing objects to the dataset
Inspiration: http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html

Args:
 - retrain binary model with latest image samples
Writes:
 - settings for binary model
 - clusters reclassified with new model
"""

import os
from glob import glob
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


def classify_clusters(config, debug):
    # Classifier locations
    if s.general['mode'] == 'detection':
        clf_folder = s.classification['fitted_classifier_folder']
    else:
        clf_folder = os.path.join(config['iteration_directory'], s.general['iterations_structure']['fit'])

    # evaluated clusters file
    cluster_file = os.path.join(config['iteration_directory'], s.general['iterations_structure']['evaluate'],
                                '3dclusters_evaluated.csv')
    # Misses file for complete data
    misses_file = os.path.join(config['iteration_directory'], s.general['iterations_structure']['evaluate'],
                               '3dclusters_truth_evaluated.csv')

    # Where to save clusters
    classified_cluster_folder = os.path.join(config['iteration_directory'], s.general['iterations_structure']['classify'])


    # read data
    data = pd.read_csv(cluster_file)

    # Get column names
    cols = list(data.columns.values)
    # Get col names for explanatory variables
    cols_expl = [c for c in cols if c not in ['x', 'y', 'z', 'matched']]

    # Read data as arrays
    X = data.as_matrix(cols_expl)
    # y = data.as_matrix(['matched']).ravel()

    # For each classifier in the folder, classify the data
    clf_files = glob(os.path.join(clf_folder, '*.pkl'))
    if len(clf_files) == 0:
        return 1
    for file_name in clf_files:
        name = os.path.splitext(os.path.basename(file_name))[0]
        clf = pickle.load(open(file_name))

        # Use the classifier to fit data
        predictions = clf.predict_proba(X)

        # Write predictions to clusters
        data['rating'] = predictions[:, 1]

        # Add missed to file before saving, so that the precision-recall curve is correct
        misses = pd.read_csv(misses_file)
        misses['rating'] = 0
        misses['matched'] = True
        all_clusters = pd.concat([data, misses], axis=0, join='outer').fillna(0)

        # file name
        classified_cluster_file = os.path.join(classified_cluster_folder, 'clusters_(' + name + ').csv')

        # save clusters
        all_clusters.to_csv(classified_cluster_file, index=False)
    return 0
