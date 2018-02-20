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
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, auc


def fit_classifiers(config, debug):
    results_folder_root = os.path.join(config['iteration_directory'],
                                       s.general['iterations_structure']['fit'])
    input_folder = os.path.join(config['iteration_directory'], s.general['iterations_structure']['evaluate'])

    do_fit_classifiers(config=config, results_folder_root=results_folder_root, input_folder=input_folder)

    return 0


def do_fit_classifiers(config, results_folder_root, input_folder):
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

    # iterate over classifiers and folds
    for name, clf in zip(names, classifiers):
        results_folder = os.path.join(results_folder_root,
                                      '{}'.format(name))
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        f, ax = initialize_plot(name)
        for fold_i in range(s.general['do_folds']):
            # print('-- FOLD {} --'.format(fold_i))
            # Read evaluated clusters
            cluster_train_file = os.path.join(input_folder,
                                        '3dclusters_train_{}.csv'.format(fold_i))
            cluster_test_file = os.path.join(input_folder,
                                        '3dclusters_test_{}.csv'.format(fold_i))

            # read training and test data
            data_train = pd.read_csv(cluster_train_file)
            data_test = pd.read_csv(cluster_test_file)

            # split misses
            data_train_no_misses = data_train[~data_train.missed]
            data_test_no_misses = data_test[~data_test.missed]
            data_test_misses = data_test[data_test.missed].fillna(0)

            # Get column names
            colnames = list(data_train.columns.values)
            # Get col names for explanatory variables
            colnames_expl = [c for c in colnames if c not in ['x', 'y', 'z', 'matched', 'missed', 'matched_id']]

            # Read data as arrays
            X_train = data_train_no_misses.as_matrix(colnames_expl)
            y_train = data_train_no_misses.as_matrix(['matched']).ravel()
            X_test = data_test_no_misses.as_matrix(colnames_expl)
            y_test = data_test_no_misses.as_matrix(['matched']).ravel()
            # Read misses as arrays
            X_test_misses = data_test_misses.as_matrix(colnames_expl)
            y_test_misses = data_test_misses.as_matrix(['matched']).ravel()

            # Fit training
            clf.fit(X_train, y_train)

            # Write model to file
            clf_file = os.path.join(results_folder, 'model_{}.pkl'.format(fold_i))
            with open(clf_file, 'wb') as fid:
                pickle.dump(clf, fid)

            # predict train and test
            y_train_predict = clf.predict_proba(X_train)
            y_test_predict = clf.predict_proba(X_test)

            # attach predictions onto data (attention! predictions only exist for non-misses)
            data_train = pd.concat([
                pd.concat([
                    data_train_no_misses.reset_index(drop=True),
                    pd.DataFrame({'rating': list(y_train_predict[:, 1])})], axis=1, ),
                data_train[data_train.missed]], axis=0, join='outer', ignore_index=True).fillna(0)

            data_test = pd.concat([
                pd.concat([
                    data_test_no_misses.reset_index(drop=True),
                    pd.DataFrame({'rating': list(y_test_predict[:, 1])})], axis=1, ),
                data_test[data_test.missed]], axis=0, join='outer', ignore_index=True).fillna(0)

            # write to files
            data_train.to_csv(os.path.join(results_folder, '3dclusters_train_{}.csv'.format(fold_i)))
            data_test.to_csv(os.path.join(results_folder, '3dclusters_test_{}.csv'.format(fold_i)))

            # attach misses to data
            y_test_with_misses = np.append(y_test, y_test_misses, axis=0)
            y_test_predict_with_misses = np.append(y_test_predict, np.zeros((len(y_test_misses), 2)), axis=0, )
            # add precision recall curves to plot
            ax = update_plot(ax, y_test_with_misses, y_test_predict_with_misses[:, 1], fold_i)

        # finalize plot
        plot_file = os.path.join(results_folder_root, 'precision_recall_({}).png'.format(name))
        finalize_plot(f, ax, plot_file)

    return 0


def initialize_plot(classifier_name):
    f, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(classifier_name)
    ax.y_real, ax.y_proba = [], []
    return f, ax


def update_plot(ax, y_real, y_proba, fold_i):
    precision, recall, _ = precision_recall_curve(y_real, y_proba)
    lab = 'Fold %d AUC=%.4f' % (fold_i + 1, auc(recall, precision))
    ax.step(recall[recall < 1], precision[recall < 1], label=lab, where='post')
    # update list containing results from all folds
    ax.y_real += list(y_real)
    ax.y_proba += list(y_proba)
    return ax


def finalize_plot(f, ax, plot_file):
    precision, recall, _ = precision_recall_curve(ax.y_real, ax.y_proba)
    lab = 'Overall AUC=%.4f' % (auc(recall, precision))
    ax.step(recall[recall < 1], precision[recall < 1], label=lab, lw=2, color='black', where='post')
    ax.legend(loc='lower left', fontsize='small')
    f.tight_layout()
    f.savefig(plot_file)
    # plt.show()
