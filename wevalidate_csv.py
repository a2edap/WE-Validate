# This script runs the comparison between timeseries data.
# This is the main routine for we-validate when using csv files
#
# Malcolm Moncheur de Rieudotte <malcolm.moncheurderieudotte at pnnl.gov>
import yaml
import sys
import os
import pathlib
import numpy as np
import pandas as pd
from tools import eval_tools, cal_print_metrics_csv

config = 'config.yaml'

def compare(config=None):

    # this section checks to see if there is a set configuration. If so, it assigns the config file based on the configuratiom name.
    # If not, it assigns the default configuration
    config_dir = os.path.join(pathlib.Path(os.getcwd()), 'config')
    if config is None:
        config_file = os.path.join(config_dir, 'config.yaml')
    else:
        config_file = os.path.join(config_dir, config)
    sys.path.append('.')

    conf = yaml.load(open(config_file), Loader=yaml.FullLoader)

    # define swingdoor functions
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
        joined_mag, joined_rate, joined_dur = [df.rename(columns={'0_x': base['name'], '0_y': c['name']}) for df in
                                               [joined_mag, joined_rate, joined_dur]]
        return joined_mag, joined_rate, joined_dur


    # set base and comparaison configurations from config file
    base = conf['base']
    comp = conf['comp']

    # Load modules
    metrics = [eval_tools.get_module_class('metrics', m)()
                for m in conf['metrics']]

    aggregations = conf['aggregation']
    metric_dict = conf['metrics']

    # loads QC module
    crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts_csv')(conf)

    # loads plotting module
    plotting = eval_tools.get_module_class('plotting', 'plot_data_csv')(conf)

    # For data storage and metrics computation
    results = []

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

        combine_df = crosscheck_ts.align_time(base, c)
        if any('swingdoor' in i for i in analysis):
            magnitude, ramprate, duration = compute_sd(combine_df[base['name']], combine_df[c['name']])
            swingdoor_ts = {
                            'swingdoor-mag':magnitude,
                            'swingdoor-ramp':ramprate,
                            'swingdoor-dur':duration
                            }
        results = eval_tools.append_results(results, base, c, analysis[0])

        for a_ind, analysis_type in enumerate(analysis):

            # Crosscheck between datasets

            if 'swingdoor' in analysis_type:
                full_df = swingdoor_ts[analysis_type].copy(deep=True)
            else:
                full_df = combine_df.copy(deep=True)
            
            cal_print_metrics_csv.run(
                full_df, metrics, results, ind, c, conf, base, aggregations, analysis_type
                )


            for a in aggregations:

                dfname = 'metrics_' + analysis_type +'_' + c['name'] + '_' + a

                metricstat_dict = {key: results[ind][analysis_type][a][key]
                                for key in conf['metrics']}
                metricstat_df = pd.DataFrame.from_dict(metricstat_dict, orient='columns')

                globals()[dfname] = metricstat_df

                if 'output' in conf:

                    output_path = os.path.join(
                        (pathlib.Path(os.getcwd())), conf['output']['path']
                    )

                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

                    if conf['output']['save_metrics'] is True:
                        globals()[dfname].to_csv(os.path.join(output_path, conf['output']['org'] + '_' + dfname + '.csv'))


        plotting.plot_ts_line(combine_df)
        plotting.plot_ts_line_monthly(combine_df)
        plotting.plot_histogram(combine_df)
        plotting.plot_histogram_monthly(combine_df)
        plotting.plot_pair_scatter(combine_df)
        plotting.plot_pair_scatter_monthly(combine_df)

if __name__ == '__main__':
    compare(config = config)