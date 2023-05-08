# This script runs the comparison between timeseries data,
# as specified in config_ba_pc.yaml. This is the main routine for we-validate when using csv files
#
# Joseph Lee <joseph.lee at pnnl.gov>
#%reload_ext autoreload
#%autoreload 2

# import importlib
# importlib.reload(eval_tools)
# importlib.reload(cal_print_metrics)

import yaml
import sys
import os
import pathlib
import numpy as np
import pandas as pd

from tools import eval_tools, cal_print_metrics_csv

config = 'config_ba_pc.yaml'

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

    # conf

    # set base, comparaison, and power curve configurations from config file
    base = conf['base']
    comp = conf['comp']
    # p_curve
    # print('validation start time:', conf['time']['window']['start'])
    # print('validation end time:', conf['time']['window']['end'])
    # print('location:', conf['location'])
    # print('baseline dataset:', base['name'])
    # print('variable:', conf['reference']['var'])

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
    all_ramp_ts_df = pd.DataFrame()
    all_ramp_stat_df = pd.DataFrame()

    # For data storage and metrics computation
    results = []
    monthly_results = []


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

        # added this code to edit year if comparing data from different years. uncomment if comparing 2016 base with 2018 comp
        # c['data']['datetime'] = c['data'].index.to_pydatetime()
        # c['data']['newdatetime'] = c['data']['datetime'] - pd.DateOffset(years=2)
        # c['data'].set_index('newdatetime', inplace= True)
        # c['data'].drop('datetime', axis = 1, inplace = True)


        results = eval_tools.append_results(results, base, c, conf)

        # Crosscheck between datasets
        combine_df = crosscheck_ts.align_time(base, c)

        cal_print_metrics_csv.run(
            combine_df, metrics, results, ind, c, conf, base, monthly_results
            )

        metricstat_dict = {key: results[ind][key]
                           for key in conf['metrics']}
        metricstat_df = pd.DataFrame.from_dict(
            metricstat_dict, orient='index', columns=[c['target_var']]
            )

        metricstat_df.columns = pd.MultiIndex.from_product(
            [[c['name']], metricstat_df.columns]
            )

        if all_lev_stat_df.empty:
           # all_lev_stat_df = all_lev_stat_df.append(metricstat_df)
            all_lev_stat_df = pd.concat([all_lev_stat_df, metricstat_df], axis = 1)
        else:
            all_lev_stat_df = pd.concat(
                [all_lev_stat_df, metricstat_df], axis=1
                )

        plotting.plot_ts_line(combine_df)
        plotting.plot_histogram(combine_df)
        plotting.plot_pair_scatter(combine_df)

        if 'ramps' in conf:

            ramp_data = cal_print_metrics.remove_na(
                combine_df, ramp_txt=True
                )

            for ramps in conf['ramps']:

                r = eval_tools.get_module_class(
                    'ramps', ramps['definition'])(
                        conf, c, ramp_data, ramps)

                print()
                print('@@@@@~~ calculating ramp skill scores at '+str(lev)
                      + ' '+conf['levels']['height_units']
                      + ' using definition: '
                      + r.__class__.__name__+' ~~@@@@@')

                ramp_df = r.get_rampdf()

                process_ramp = eval_tools.get_module_class(
                    'ramps', 'process_ramp')(ramp_df)

                ramp_df = process_ramp.add_contingency_table()

                plot_ramp = eval_tools.get_module_class(
                    'plotting', 'plot_ramp')(
                        ramp_df, combine_df, conf, lev, ramps)

                # Generating all the ramp texts and plots can take up memory space
                if 'plotting' in ramps:

                    if ramps['plotting'] is True:

                        plot_ramp.plot_ts_contingency()
                        process_ramp.print_contingency_table()
                        # Print skill scores
                        # process_ramp.cal_print_scores()

                ramp_summary_df = process_ramp.generate_ramp_summary_df()

                ramp_summary_df.columns = pd.MultiIndex.from_product(
                    [[lev], [c['name']], [c['target_var']],
                     [r.ramp_nature], [r.get_ramp_method_name()]]
                    )

                ramp_df.columns = pd.MultiIndex.from_product(
                    [[lev], [c['name']], [c['target_var']],
                     [r.ramp_nature], [r.get_ramp_method_name()], ramp_df.columns]
                    )

                if all_ramp_stat_df.empty:
                    all_ramp_stat_df = all_ramp_stat_df.append(
                        ramp_summary_df
                        )
                    all_ramp_ts_df = all_ramp_ts_df.append(
                        ramp_df
                        )
                else:
                    all_ramp_stat_df = pd.concat(
                        [all_ramp_stat_df, ramp_summary_df], axis=1
                        )
                    all_ramp_ts_df = pd.concat(
                        [all_ramp_ts_df, ramp_df], axis=1
                        )

        combine_df.columns = pd.MultiIndex.from_product(
            [[c['name']], combine_df.columns]
            )

        if all_lev_df.empty:
            # all_lev_df = all_lev_df.append(combine_df)
            all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)
        else:
            all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)

    if 'output' in conf and conf['output']['writing'] is True:

        output_path = os.path.join(
        (pathlib.Path(os.getcwd())), conf['output']['path']
        )

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if conf['output']['format'] == 'csv':

            all_lev_df.to_csv(
                os.path.join(output_path,
                             'ts_'+conf['output']['org']+'.csv')
                )
            all_lev_stat_df.to_csv(
                os.path.join(output_path,
                             'metrics_'+conf['output']['org']+'.csv')
                )

            if 'ramps' in conf:

                all_ramp_stat_df.to_csv(
                    os.path.join(output_path,
                                 'ramp_'+conf['output']['org']+'.csv')
                    )
                all_ramp_ts_df.to_csv(
                    os.path.join(output_path,
                                 'ramp_ts_'+conf['output']['org']+'.csv')
                    )
    for item in monthly_results:
        print(key)
        print(item)
        #     for key2, val2 in val.items():
        #         print('Month: ' + str(key2.month) + ' '+str(np.round(val2, 3))+end_units)

if __name__ == '__main__':
    compare(config = config)