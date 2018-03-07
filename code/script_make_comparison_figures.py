from default_settings import all as s
import os
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, auc
import pandas as pd
import seaborn as sns

sns.set(color_codes=True)
from itertools import compress

classifier_names = ["Nearest Neighbors",
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

iteration_name = '2018-01-25 17.43.50'

multi_view_results_dir_root = os.path.join(
    s['general']['working_directory'],
    s['general']['iterations_subdir'],
    iteration_name,
    s['general']['iterations_structure']['fit'])

single_view_results_dir_root = os.path.join(
    s['general']['working_directory'],
    s['general']['iterations_subdir'],
    iteration_name,
    s['general']['iterations_structure']['ortho_fit'])

curves = [
    {
        "epsilon": 18.0,
        "min_samples": 4,
        "classifier": 'Neural Net',
        "folder": multi_view_results_dir_root,
        "title": 'multi-view',
        "linestyle": '-',
        "color": '#ff0000'

    },
 {
        "epsilon": 16.0,
        "min_samples": 2,
        "classifier": 'Neural Net',
        "folder": single_view_results_dir_root,
        "title": 'single-view',
        "linestyle": '--',
        "color": '#000000'
    }
]



def main():

    f, ax = initialize_plot()

    for c in curves:
        # if (os.path.exists(os.path.join(multi_view_results_dir_root, classifier)) &
        #         os.path.exists(os.path.join(single_view_results_dir_root, classifier))):

        y_real = []
        y_predicted = []
        precision_folds = []
        recall_folds = []

        # loop through folds and load data
        for fold_i in range(s['general']['do_folds']):
            data = pd.read_csv(os.path.join(multi_view_results_dir_root, c['classifier'],
                                           '3dclusters_test_R{}N{}_{}.csv'.format(
                                               c['epsilon']/100,
                                               c['min_samples'],
                                               fold_i)))

            # load data
            #compute individual PR curve
            precision, recall, _ = precision_recall_curve(data.matched, data.rating)
            precision_folds += list(precision)
            recall_folds += list(recall)
            y_real += list(data.matched)
            y_predicted += list(data.rating)
            draw_fold(ax, c, list(data.matched), list(data.rating))

        # make plot
        update_plot(ax, c, y_real, y_predicted)

    plot_filename = os.path.join(
        s['general']['working_directory'],
        'iterations',
        iteration_name, 'plots',
        'precision-recall_{}.pdf'.format('comparison'))
    finalize_plot(f, ax, plot_filename)

            # Create boxplot
            # boxplot(ax, classifier)


def boxplot(data, classifier_name):
    single = pd.DataFrame({
        'real': data.y_real_single,
        'pred': data.y_predicted_single
    })
    single['true'] = single.pred[single.real]
    single['false'] = single.pred[~single.real]
    multi = pd.DataFrame({
        'real': data.y_real_multi,
        'pred': data.y_predicted_multi
    })
    multi['true'] = multi.pred[multi.real]
    multi['false'] = multi.pred[~multi.real]

    labels = ['true positives', 'false positives']
    f, ax = plt.subplots(1, 2, figsize=(5, 5), sharey=True)
    # ax[0].set_xlabel('Recall')
    ax[0].set_ylabel('Prediction')
    ax[0].set_ylim(0, 1)
    ax[0].set_title('Single-view')
    ax[1].set_title('Multi-view')
    ax[0].violinplot([list(single.true),
                      list(single.false)],
                     # notch=True,  # notch shape
                     # vert=True,  # vertical box alignment
                     # patch_artist=True,  # fill with color
                     )  # will be used to label x-ticks
    ax[1].violinplot([list(multi.true),
                      list(multi.false)],
                     # notch=True,  # notch shape
                     # vert=True,  # vertical box alignment
                     # patch_artist=True,  # fill with color
                     )  # will be used to label x-ticks
    ax[0].set_xticklabels(labels)
    ax[1].set_xticklabels(labels)
    plot_file = os.path.join(
        s['general']['working_directory'],
        'iterations',
        iteration_name, 'plots',
        'boxplot_{}.png'.format(classifier_name))
    f.tight_layout()
    f.savefig(plot_file)


def initialize_plot():
    f, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('comparison')
    return f, ax


def draw_fold(ax, curve, y_real, y_predicted):
    # plot PR curves
    precision, recall, _ = precision_recall_curve(y_real, y_predicted)
    ax.plot(recall[recall < 1], precision[recall < 1],
            linestyle=curve['linestyle'], color=curve['color'], alpha=0.3, lw=1)
    return ax


def update_plot(ax, curve, y_real, y_predicted):
    # plot PR curves
    precision, recall, _ = precision_recall_curve(y_real, y_predicted)
    lab = '{} ({:.2f}AP)'.format(curve['title'], auc(recall[recall < 1], precision[recall < 1]))
    ax.plot(recall[recall < 1], precision[recall < 1],
            label=lab, linestyle=curve['linestyle'], color=curve['color'])
    return ax


def finalize_plot(f, ax, plot_file):
    # precision, recall, _ = precision_recall_curve(ax.y_real_single, ax.y_predicted_single)
    # lab = 'Single-view AUC: %.4f' % (auc(recall[recall < 1], precision[recall < 1]))
    # ax.plot(recall[recall < 1], precision[recall < 1], label=lab, lw=2, linestyle=':', color='#000000')
    ax.legend(loc='lower left', fontsize='small')
    f.tight_layout()
    f.savefig(plot_file)
    # plt.show()


main()
