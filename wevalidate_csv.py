# This script runs the comparison between timeseries data.
# This is the main routine for we-validate when using csv files
#
# Malcolm Moncheur de Rieudotte <malcolm.moncheurderieudotte at pnnl.gov>
#%%
import yaml
import sys
import os
import pathlib
import numpy as np
import pandas as pd
#%%
from tools import eval_tools, cal_print_metrics_csv
# import importlib
# importlib.reload(eval_tools)
config = 'config.yaml'

def swingdoor_func(x, thresh):
    # Process data with swinging door method.
    gp = np.array(x)
    timestamp_gp = np.array(x.index)
    # dev = max(.1*x.max(),.1*y.max())
    dev = thresh * gp.max()

    len_gp = len(gp)
    # len_gp = 200
    magnitude, rate, duration = np.zeros(len_gp), np.zeros(len_gp), np.zeros(len_gp)
    # Temperary arrays used for swinging door method
    ratemin, ratemax = np.zeros(len_gp), np.zeros(len_gp)
    magnitude_c, rate_c, duration_c, timestamp_c = np.zeros(len_gp), np.zeros(len_gp), np.zeros(
        len_gp), np.zeros(len_gp, dtype='datetime64[ns]')
    # swinging door algorithm
    magnitude[0] = gp[0]
    i = 0  # index of this group, gp
    m = 0  # index of compressed data set
    while i < len_gp:
        magnitude[i] = gp[i]
        magnitude_c[m] = magnitude[i]
        timestamp_c[m] = timestamp_gp[i]
        j = 0
        while j < len_gp - i:
            # print(j)
            magnitude[i + j] = gp[i + j]
            rate[i + j] = (magnitude[i + j] - magnitude[i]) / (j + 1)
            ratemax[i + j] = (magnitude[i + j] - magnitude[i] + dev) / (j + 1)
            ratemin[i + j] = (magnitude[i + j] - magnitude[i] - dev) / (j + 1)
            flag = 0
            for k in range(j):
                if (ratemax[i + k] < rate[i + j]) | (ratemin[i + k] > rate[i + j]):
                    flag = 1
                    break
            if flag == 1:
                # set rate value for data points from i to i+j-2
                newrate = (magnitude[i + j - 1] - magnitude[i]) / (j)
                for k in range(j - 1):
                    rate[i + k - 1] = newrate
                    duration[i + k - 1] = j - k
                break
            else:
                j += 1
        # when searching reaches the end of gp, store the rate value
        # for data points from i to i+j-2 (2nd to laast data point).
        # rate and duration of the last data point can not be determined
        if j == len_gp - i:
            newrate = (magnitude[i + j - 1] - magnitude[i]) / (j)
            for k in range(j - 1):
                rate[i + k - 1] = newrate
                duration[i + k - 1] = j - k
        rate_c[m], duration_c[m] = rate[i], duration[i]
        i = i + j
        m += 1

    magnitude_c = np.trim_zeros(magnitude_c, 'b')
    rate_c = np.trim_zeros(rate_c, 'b')
    duration_c = np.trim_zeros(duration_c, 'b')
    len_c = len(magnitude_c)
    timestamp_c = timestamp_c[:len_c]

    return magnitude_c, rate_c, duration_c, timestamp_c

def compute_sd(x, y):
    base_mag, base_rate, base_dur, base_t = swingdoor_func(x, .2)
    comp_mag, comp_rate, comp_dur, comp_t = swingdoor_func(y, .2)
    joined_mag = pd.DataFrame(base_mag, index=base_t).merge(pd.DataFrame(comp_mag, index=comp_t), how='outer',
                                                            left_index=True, right_index=True).ffill().resample(
        '1H').ffill()
    if len(base_rate) < len(base_t):
        base_rate = np.append(base_rate, 0)
    if len(comp_rate) < len(comp_t):
        comp_rate = np.append(comp_rate, 0)
    joined_rate = pd.DataFrame(base_rate[:len(base_t)], index=base_t).merge(
        pd.DataFrame(comp_rate[:len(comp_t)], index=comp_t), how='outer', left_index=True,
        right_index=True).ffill().resample('1H').ffill()
    df = pd.DataFrame(base_dur, index=base_t)
    df = pd.concat([df, pd.DataFrame({0: 0}, index=df.index[1:] - pd.Timedelta('1H'))])
    b_dur = df[~df.index.duplicated(keep='first')].sort_index().resample('1H').interpolate()
    df = pd.DataFrame(comp_dur[:len(comp_t)], index=comp_t)
    df = pd.concat([df, pd.DataFrame({0: 0}, index=df.index[1:] - pd.Timedelta('1H'))])
    c_dur = df[~df.index.duplicated(keep='first')].sort_index().resample('1H').interpolate()
    joined_dur = b_dur.merge(c_dur, how='outer', left_index=True, right_index=True)
    joined_mag, joined_rate, joined_dur = [df.rename(columns={'0_x':base['name'], '0_y':c['name']}) for df in [joined_mag, joined_rate, joined_dur]]
    return joined_mag, joined_rate, joined_dur
#%%

# this section checks to see if there is a set configuration. If so, it assigns the config file based on the configuratiom name.
# If not, it assigns the default configuration

def compare(config=None):

    config_dir = os.path.join(pathlib.Path(os.getcwd()), 'config')
    #print(config_dir)
    if config is None:
        config_file = os.path.join(config_dir, 'config.yaml')
    else:
        config_file = os.path.join(config_dir, config)
    #print(config_dir)
    #print(config_file)
    sys.path.append('.')

    conf = yaml.load(open(config_file), Loader=yaml.FullLoader)


    # set base and comparaison configurations from config file
    base = conf['base']
    comp = conf['comp']


    # Load modules

    metrics = [eval_tools.get_module_class('metrics', m)()
                for m in conf['metrics']]
    metrics

    aggregations = conf['aggregation']

    # loads QC module
    crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts_csv')(conf)

    # loads plotting module
    plotting = eval_tools.get_module_class('plotting', 'plot_data_csv')(conf)

    # Data frame containing data at all heights (empty data frames)
    all_lev_df = pd.DataFrame()
    all_lev_stat_df = pd.DataFrame()
    # all_lev_monthly_stat_df = pd.DataFrame()


    # For data storage and metrics computation
    results = []
    # monthly_results = []
    # weekly_results = []
    # annual_results = []
    # daily_results = []
    # hourly_results = []


    print()
    print('********** for '+base['name']+': **********')

    # Run __init__

    base['input'] = eval_tools.get_module_class(
        'inputs', base['function'])(base, conf)

    base['data'] = base['input'].get_ts()
    # For each specified comparison dataset
    analysis = conf['analysis']

    for ind, c in enumerate(comp):

        print()
        print('********** for '+c['name']+': **********')

        # Run __init__
        c['input'] = eval_tools.get_module_class(
            'inputs', c['function'])(c, conf)

        c['data'] = c['input'].get_ts()


        # if swingdoor is None:
        #     # calculate metrics for swingdoor components
        #     analysis_type = 'base_analysis'
        # else:
        #     analysis_type = 'swingdoor_analysis'
        combine_df = crosscheck_ts.align_time(base, c)
        if any('swingdoor' in i for i in analysis):
            magnitude, ramprate, duration = compute_sd(combine_df[base['name']], combine_df[c['name']])
            swingdoor_ts = {
                            'swingdoor-mag':magnitude,
                            'swingdoor-ramp':ramprate,
                            'swingdoor-dur':duration
                            }
        results = eval_tools.append_results(results, base, c, conf, analysis[0])

        for a_ind, analysis_type in enumerate(analysis):

            # Crosscheck between datasets

            if 'swingdoor' in analysis_type:
                full_df = swingdoor_ts[analysis_type].copy(deep=True)
            else:
                full_df = combine_df.copy(deep=True)
            
            cal_print_metrics_csv.run(
                full_df, metrics, results, ind, c, conf, base, aggregations, analysis_type
                )


# Malcolm: the lines below here will need some attention
        # the above changes broke the following lines of code:
        # to fix, we'll need to go into the key for the aggregation,
        # then go into the key for the metric
        metricstat_dict = {key: results[ind][key]
                            for key in conf['metrics']}
        metricstat_df = pd.DataFrame.from_dict(
            metricstat_dict, orient='index', columns=[c['name']]
            )

        metricstat_df.columns = pd.MultiIndex.from_product(
            [[c['name']], metricstat_df.columns]
            )


        if all_lev_stat_df.empty:
            all_lev_stat_df = pd.concat([all_lev_stat_df, metricstat_df], axis = 1)
        else:
            all_lev_stat_df = pd.concat(
                [all_lev_stat_df, metricstat_df], axis=1
                )

        all_lev_monthly_stat_df = [pd.DataFrame(d) for d in monthly_results]
        all_lev_monthly_stat_df = pd.concat(all_lev_monthly_stat_df)

        all_lev_weekly_stat_df = [pd.DataFrame(d) for d in weekly_results]
        all_lev_weekly_stat_df = pd.concat(all_lev_weekly_stat_df)

        all_lev_annual_stat_df = [pd.DataFrame(d) for d in annual_results]
        all_lev_annual_stat_df = pd.concat(all_lev_annual_stat_df)

        all_lev_daily_stat_df = [pd.DataFrame(d) for d in daily_results]
        all_lev_daily_stat_df = pd.concat(all_lev_daily_stat_df)

        all_lev_hourly_stat_df = [pd.DataFrame(d) for d in hourly_results]
        all_lev_hourly_stat_df = pd.concat(all_lev_hourly_stat_df)

        plotting.plot_ts_line(combine_df)
        plotting.plot_ts_line_monthly(combine_df)
        plotting.plot_histogram(combine_df)
        plotting.plot_histogram_monthly(combine_df)
        plotting.plot_pair_scatter(combine_df)
        plotting.plot_pair_scatter_monthly(combine_df)


        combine_df.columns = pd.MultiIndex.from_product(
            [[c['name']], combine_df.columns]
            )

        if all_lev_df.empty:
            all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)
        else:
            all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)

    if 'output' in conf:

        output_path = os.path.join(
        (pathlib.Path(os.getcwd())), conf['output']['path']
        )

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if conf['output']['save_metrics'] is True:

            all_lev_df.to_csv(
                os.path.join(output_path,
                                'time_series_'+conf['output']['org']+'.csv')
                )
            all_lev_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_'+conf['output']['org']+'.csv')
                )

            all_lev_monthly_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_monthly_'+conf['output']['org']+'.csv')
                )

            all_lev_weekly_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_weekly_' + conf['output']['org'] + '.csv')
            )

            all_lev_annual_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_annual_' + conf['output']['org'] + '.csv')
            )

            all_lev_daily_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_daily_' + conf['output']['org'] + '.csv')
            )

            all_lev_hourly_stat_df.to_csv(
                os.path.join(output_path,
                                'metrics_hourly_' + conf['output']['org'] + '.csv')
            )


        for item in monthly_results:
            plotting.plot_ts_line_monthly_metric(item)

            if conf['output']['print_results'] is True:
                print('==-- monthly metrics: '+item['compare']
                        + ' - '+item['base']+' --=='
                        )
                for key, val in item.items():
                    if isinstance(val, pd.Series):
                        end_units = ''
                        suffix_pct = 'pct'

                        if str(key).endswith(suffix_pct):
                            end_units = '%'
                        print(key)
                        for key2, val2 in val.items():
                            print('Month: ' + str(key2.month) + ', value:  '+str(np.round(val2, 3))+end_units)



if __name__ == '__main__':
    compare(config = config)