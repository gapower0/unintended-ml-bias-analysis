"""Analysis of model bias.

We look at differences in model scores as a way to compare bias in different
models.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from model_tool import ToxModel, compute_auc

MODEL_DIR = '../models/'
ORIG_MADLIBS_PATH = '../eval_datasets/bias_madlibs_89k.csv'
SCORED_MADLIBS_PATH = '../eval_datasets/bias_madlibs_89k_scored.csv'

### Model scoring

# Scoring these dataset for dozens of models actually takes non-trivial amounts
# of time, so we save the results as a CSV. The resulting CSV includes all the
# columns of the original dataset, and in addition has columns for each model,
# containing the model's scores.

def postprocess_madlibs(madlibs):
    """Modifies madlibs data to have standard 'text' and 'label' columns."""
    # Native madlibs data uses 'Label' column with values 'BAD' and 'NOT_BAD'.
    # Replace with a bool.
    madlibs['label'] = madlibs['Label'] == 'BAD'
    madlibs.drop('Label', axis=1, inplace=True)
    madlibs.rename(columns={'Text': 'text'}, inplace=True)

def score_dataset(df, models, text_col):
    """Scores the dataset with each model and adds the scores as new columns."""
    for model in models:
        name = model.get_model_name()
        print('{} Scoring with {}...'.format(datetime.datetime.now(), name))
        df[name] = model.predict(df[text_col])

def load_scored_madlibs(models, scored_path=SCORED_MADLIBS_PATH,
                        orig_path=ORIG_MADLIBS_PATH):
    if os.path.exists(scored_path):
        print('Using previously scored data:', scored_path)
        return pd.read_csv(scored_path)

    madlibs = pd.read_csv(orig_path)
    postprocess_madlibs(madlibs)
    score_dataset(madlibs, models, 'text')
    print('Saving scores to:', scored_path)
    madlibs.to_csv(scored_path)
    return madlibs


### Model score analysis: AUC

def model_family_auc(dataset, model_names, label_col):
    aucs = [compute_auc(dataset[label_col], dataset[model_name])
            for model_name in model_names]
    return {
        'aucs': aucs,
        'mean': np.mean(aucs),
        'median': np.median(aucs),
        'std': np.std(aucs),
    }

def plot_model_family_auc(dataset, model_names, label_col, min_auc=0.9):
    result = model_family_auc(dataset, model_names, label_col)
    print('mean AUC:', result['mean'])
    print('median:', result['median'])
    print('stddev:', result['std'])
    plt.hist(result['aucs'])
    plt.gca().set_xlim([min_auc, 1.0])
    plt.show()
    return result
