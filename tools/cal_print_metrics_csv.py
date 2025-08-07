# This script calculates and prints metrics results for csv files

import numpy as np
import itertools
from tools import eval_tools
import sys
import pandas as pd
import inspect
import pytz
import pvlib
import pandas as pd
import pytz

def classify_daynight(latitude, longitude, timezone, timestamps):
    """Classify timestamps as day/night using sunrise/sunset from specified location"""
    labels = []
    for timestamp in timestamps:
        date_time = pd.Timestamp(timestamp, tz=pytz.timezone(timezone))
        location = pvlib.location.Location(latitude, longitude, tz=timezone)
        solar_position = location.get_solarposition(date_time)
        altitude = solar_position['apparent_elevation'].iloc[0]
        if altitude > 0:
            labels.append('day')
            # print(f"It's daytime. Solar altitude: {altitude:.2f} degrees")
        else:
            labels.append('night')
            # print(f"It's nighttime. Solar altitude: {altitude:.2f} degrees")

    return labels

def remove_na(combine_df, conf, ramp_txt=False):

    compute_df = combine_df.dropna()

    only_na = combine_df[~combine_df.index.isin(compute_df.index)]

    if ramp_txt is True:
        print_txt = 'ramp metrics'
    else:
        print_txt = 'metrics'
    if conf['output']['print_NaN_values'] is True: 
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




def run(combine_df, metrics, results, ind, c, conf, base, aggregations, analysis_type):
    """Calculate metrics and print results.
    Remove NaNs in data frame.
    For each data column combination, split into baseline and
    compare data series.
    Calculate and print metrics, as listed in the yaml file.
    """

    compute_df = remove_na(combine_df, conf)

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
                if "z" in inspect.signature(m.compute).parameters:
                    aggregation_results[a][m.__class__.__name__] = calc_metrics(x, y, freq=a, func=m.compute, z=z)
                else:
                    aggregation_results[a][m.__class__.__name__] = calc_metrics(x, y, freq=a, func=m.compute, z=None)
            if conf['daynight'].get('classify', False):
                daynight_labels = classify_daynight(conf['daynight']['latitude'], conf['daynight']['longitude'], conf['daynight']['timezone'], compute_df.index)

                # Uncomment the following lines if you want to verify the day/night classification
                # verification_df = pd.DataFrame({
                #     'timestamp': compute_df.index,
                #     'classification': daynight_labels
                # })
                # verification_df.to_csv('daynight_check.csv', index=False)
          
                df_daynight = compute_df.copy()
                df_daynight['daynight'] = daynight_labels
                # Split data into day and night
                d_data = df_daynight[df_daynight['daynight'] == 'day']
                n_data = df_daynight[df_daynight['daynight'] == 'night']
       
                for period, period_data in [('day', d_data), ('night', n_data)]:
                    result_key = f"{a}_{period}"
                    aggregation_results[result_key] = {
                        'compare': c['name'],
                        'base': base['name']
                    }
                    
                    x_period = period_data[pair[0]]
                    y_period = period_data[pair[1]]
                    
                    if conf['capacity'] is None:
                        z_period = x_period.max()
                    else:
                        z_period = conf['capacity']
                    
                    # Calculate metrics for this period
                    for m in metrics:
                        if "z" in inspect.signature(m.compute).parameters:
                            aggregation_results[result_key][m.__class__.__name__] = calc_metrics(
                                x_period, y_period, freq=a, func=m.compute, z=z_period
                            )
                        else:
                            aggregation_results[result_key][m.__class__.__name__] = calc_metrics(
                                x_period, y_period, freq=a, func=m.compute, z=None
                            )

    
        print("Keys in aggregation_results:", list(aggregation_results.keys()))
        results[ind][analysis_type] = aggregation_results
