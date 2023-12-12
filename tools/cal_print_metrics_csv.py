# This script calculates and prints metrics results for csv files

import numpy as np
import itertools
from tools import eval_tools
import sys
import pandas as pd
import inspect


def remove_na(full_df, ramp_txt=False):

    compute_df = full_df.dropna()

    only_na = full_df[~full_df.index.isin(compute_df.index)]

    if ramp_txt is True:
        print_txt = 'ramp skill scores'
    else:
        print_txt = 'metrics'

    print()
    print('to calculate '+print_txt+', removing the following time steps ')
    print('that contain NaN values:')
    print(only_na.index.strftime('%Y-%m-%d %H:%M:%S').values)
    print()
    print('hence, only use '+str(len(compute_df))
          + ' time steps in data to calculate '+print_txt)

    return compute_df

def calc_metrics(x, y, freq, func=None, z=None): #'MS','W','A','D','H'

    if freq=='H':
        x_list = list(x.groupby([x.index.hour]))
        y_list = list(y.groupby([y.index.hour]))
    else:
        x_list = list(x.resample(freq))
        y_list = list(y.resample(freq))

    corr = [func(_x[1], _y[1], z) if z is not None else func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr


def run(full_df, metrics, results, ind, c, conf, base, aggregations, analysis_type):
    """Calculate metrics and print results.
    Remove NaNs in data frame.
    For each data column combination, split into baseline and
    compare data series.
    Calculate and print metrics, as listed in the yaml file.
    """

    compute_df = remove_na(full_df)

    # For future purposes,
    # In case of reading in multiple compare data columns
    for pair in itertools.combinations(compute_df.columns, 2):

        # Baseline should be the 1st (Python's 0th) column
        x = compute_df[pair[0]]
        y = compute_df[pair[1]]

        if conf['capacity'] is None:
            z = x.max()
        else:
            z = conf['capacity']

        if len(x) != len(y):

            sys.exit('Lengths of baseline and compare datasets are'
                     + ' not equal!'
                     )

        aggregation_results = {}
        for a in aggregations:
            aggregation_results[a]={'compare':c['name'],
                        'base': base['name']}
            for m in metrics:
                # bias_pct and mae_pct both use z (capacity of power plant)
                if "z" in inspect.signature(m.compute).parameters:
                    aggregation_results[a][m.__class__.__name__] = calc_metrics(x, y, freq=a, func=m.compute, z=z)
                else:
                    aggregation_results[a][m.__class__.__name__] = calc_metrics(x, y, freq=a, func=m.compute, z=None)

        results[ind][analysis_type] = aggregation_results
