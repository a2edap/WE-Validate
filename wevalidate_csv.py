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

    # loads QC module
    crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts_csv')(conf)

    # loads plotting module
    plotting = eval_tools.get_module_class('plotting', 'plot_data_csv')(conf)

    # Data frame containing data at all heights (empty data frames)
    all_lev_df = pd.DataFrame()
    all_lev_stat_df = pd.DataFrame()
    # all_lev_monthly_stat_df = pd.DataFrame()
    all_ramp_ts_df = pd.DataFrame()
    all_ramp_stat_df = pd.DataFrame()

    # For data storage and metrics computation
    results = []
    monthly_results = []
    weekly_results = []
    annual_results = []
    daily_results = []
    hourly_results = []


    print()
    print('********** for '+base['name']+': **********')

    # Run __init__

    base['input'] = eval_tools.get_module_class(
        'inputs', base['function'])(base, conf)

    base['data'] = base['input'].get_ts()
    # For each specified comparison dataset

    for ind, c in enumerate(comp):

        print()
        print('********** for '+c['name']+': **********')

        # Run __init__
        c['input'] = eval_tools.get_module_class(
            'inputs', c['function'])(c, conf)

        c['data'] = c['input'].get_ts()

        results = eval_tools.append_results(results, base, c, conf)

        # Crosscheck between datasets
        combine_df = crosscheck_ts.align_time(base, c)

        cal_print_metrics_csv.run(
            combine_df, metrics, results, ind, c, conf, base, monthly_results, weekly_results, annual_results, daily_results, hourly_results
            )

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