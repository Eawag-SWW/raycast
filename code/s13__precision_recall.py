"""
Args:
 - clusters with predictions scores and ground truth evaluation
Writes:
 - precision-recall curve data
Tasks:
 - Read evaluation results
 - For a number of probabilities, compute precision and recall

"""

import os
import pandas as pd
from glob import glob
import default_settings as settings
import numpy as np


def precision_recall(config, debug):

    # clusters folder
    cl_folder = os.path.join(config['iteration_directory'],
                                      settings.general['iterations_structure']['classify'])

    # output folder for data and graphs
    prc_folder = os.path.join(config['iteration_directory'],
                                      settings.general['iterations_structure']['prc'])

    # for each set of classifiers
    for cl_file in glob(os.path.join(cl_folder, 'clusters_*.csv')):
        #classifier name
        n = os.path.basename(cl_file)
        name = n[n.find("(") + 1:n.find(")")]
        # read data
        data = pd.read_csv(cl_file)

        # ground truth count
        gt = 223
        # smallest and largest thresholds
        thresh_min = 0
        thresh_max = max(data.rating)

        # precision recall holders
        pr = pd.DataFrame(columns=['threshold', 'precision', 'recall', 'hits', 'false_positives'])

        for threshold in np.linspace(thresh_min, thresh_max, settings.precision_recall['steps']):
            data_filtered = data[data.rating >= threshold]
            tp = len(data_filtered[data_filtered.matched])
            fp = len(data_filtered[data_filtered.matched == False])

            result = pd.DataFrame({
                'threshold': [threshold],
                'recall': [float(tp)/float(gt)],
                'precision': [float(tp)/float(tp+fp)],
                'hits': tp,
                'false_positives': fp
            })

            pr = pr.append(result)

        # file names
        prc_file = os.path.join(prc_folder, 'precision_recall_(' + name + ').csv')
        prc_graph_file = os.path.join(prc_folder, 'precision_recall_(' + name + ').png')

        pr.to_csv(prc_file, index=False)

        # plot results
        plot_precision_recall(data, prc_graph_file)


def plot_precision_recall(data, file_path):
    # Inspiration: https://stackoverflow.com/questions/29656550/how-to-plot-pr-curve-over-10-folds-of-cross-validation-in-scikit-learn

    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_curve, auc

    y_real = np.array([int(a == True) for a in data.matched])
    y_proba = np.array(data.rating)

    precision, recall, _ = precision_recall_curve(y_real, y_proba)
    lab = 'Overall AUC=%.4f' % (auc(recall, precision))

    f, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].scatter(data.loc[data.matched == True, 'N_max'], data.loc[data.matched == True, 'image_count'], color='blue', s=2, label='true positive')
    axes[0].scatter(data.loc[data.matched == False, 'N_max'], data.loc[data.matched == False, 'image_count'], color='red', s=2, label='false positive')
    axes[0].set_xlabel('N_max')
    axes[0].set_ylabel('image_count')
    axes[0].legend(loc='lower left', fontsize='small')
    axes[1].step(recall, precision, label=lab, lw=2, color='black')
    axes[1].set_xlabel('Recall')
    axes[1].set_ylabel('Precision')
    axes[1].legend(loc='lower left', fontsize='small')

    f.tight_layout()
    f.savefig(file_path)
