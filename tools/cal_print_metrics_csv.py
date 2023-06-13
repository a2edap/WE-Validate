# This script calculates and prints metrics results for csv files

import numpy as np
import itertools
from tools import eval_tools
import sys
import pandas as pd


def remove_na(combine_df, ramp_txt=False):

    compute_df = combine_df.dropna()

    only_na = combine_df[~combine_df.index.isin(compute_df.index)]

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

def monthly_metrics(x, y, freq='MS', func=None):
    x_list = list(x.resample(freq))
    y_list = list(y.resample(freq))

    corr = [func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr

def weekly_metrics(x, y, freq='W', func=None):
    x_list = list(x.resample(freq))
    y_list = list(y.resample(freq))

    corr = [func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr

def annual_metrics(x, y, freq='A', func=None):
    x_list = list(x.resample(freq))
    y_list = list(y.resample(freq))

    corr = [func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr

def daily_metrics(x, y, freq='D', func=None):
    x_list = list(x.resample(freq))
    y_list = list(y.resample(freq))

    corr = [func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr

def hourly_metrics(x, y, freq='H', func=None):

    x_grouped = x.groupby([x.index.hour]).mean().reset_index()
    x_grouped.set_index(pd.to_datetime( x_grouped['time_stamp'], format = "%H"), inplace=True)
    x_grouped.drop(['time_stamp'], axis = 1, inplace = True)
    x_grouped =  x_grouped.squeeze()
    y_grouped = y.groupby([y.index.hour]).mean().reset_index()
    y_grouped.set_index(pd.to_datetime(y_grouped['time_stamp'], format = "%H"), inplace=True)
    y_grouped.drop(['time_stamp'], axis = 1, inplace = True)
    y_grouped = y_grouped.squeeze()

    x_list = list(x_grouped.resample(freq))
    y_list = list(y_grouped.resample(freq))

    corr = [func(_x[1], _y[1]) for _x, _y in zip(x_list, y_list)]
    corr = pd.Series(corr, index=[_x[0] for _x in x_list])
    return corr


def run(combine_df, metrics, results, ind, c, conf, base, monthly_results, weekly_results, annual_results, daily_results, hourly_results):
    """Calculate metrics and print results.
    Remove NaNs in data frame.
    For each data column combination, split into baseline and
    compare data series.
    Calculate and print metrics, as listed in the yaml file.
    """

    compute_df = remove_na(combine_df)

    # For future purposes,
    # In case of reading in multiple compare data columns
    for pair in itertools.combinations(compute_df.columns, 2):

        # Baseline should be the 1st (Python's 0th) column
        x = compute_df[pair[0]]
        y = compute_df[pair[1]]

        if len(x) != len(y):

            sys.exit('Lengths of baseline and compare datasets are'
                     + ' not equal!'
                     )

        monthly_dict = {}
        monthly_dict['compare'] = c['name']
        monthly_dict['base'] = base['name']

        weekly_dict = {}
        weekly_dict['compare'] = c['name']
        weekly_dict['base'] = base['name']

        annual_dict = {}
        annual_dict['compare'] = c['name']
        annual_dict['base'] = base['name']

        daily_dict = {}
        daily_dict['compare'] = c['name']
        daily_dict['base'] = base['name']

        hourly_dict = {}
        hourly_dict['compare'] = c['name']
        hourly_dict['base'] = base['name']

        for m in metrics:

            results[ind][m.__class__.__name__] = m.compute(x, y)
            monthly_dict[m.__class__.__name__] = monthly_metrics(x, y, func=m.compute)
            weekly_dict[m.__class__.__name__] = weekly_metrics(x, y, func=m.compute)
            annual_dict[m.__class__.__name__] = annual_metrics(x, y, func=m.compute)
            daily_dict[m.__class__.__name__] = daily_metrics(x, y, func=m.compute)
            hourly_dict[m.__class__.__name__] = hourly_metrics(x, y, func=m.compute)

        monthly_results.append(monthly_dict)
        weekly_results.append(weekly_dict)
        annual_results.append(annual_dict)
        daily_results.append(daily_dict)
        hourly_results.append(hourly_dict)

        if conf['output']['print_results'] is True:

            print()
            print('==-- '+conf['reference']['var']+' metrics: '+c['name']
                  + ' - '+base['name']+' --=='
                  )
            print()

            for key, val in results[ind].items():

                if isinstance(val, float):

                    end_units = ''
                    suffix_pct = 'pct'

                    if str(key).endswith(suffix_pct):
                        end_units = '%'

                    print(str(key)+': '+str(np.round(val, 3))+end_units)
