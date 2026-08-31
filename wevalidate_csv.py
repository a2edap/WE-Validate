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
import matplotlib.pyplot as plt
import datetime 
from tools import eval_tools, cal_print_metrics_csv, csv_to_pdf
import glob

config = 'southern_co_config/2025_actual/58766_2025.yaml'
config = 'southern_co_config/2025_actual/58766_2025.yaml'

# this section checks to see if there is a set configuration. If so, it assigns the config file based on the configuration name.
# If not, it assigns the default configuration

def compare(config=None, threshold=None):

    config_dir = os.path.join(pathlib.Path(os.getcwd()), 'config')
    if config is None:
        config_file = os.path.join(config_dir, 'config.yaml')
    else:
        config_file = os.path.join(config_dir, config)
    sys.path.insert(0, str(pathlib.Path(__file__).parent))

    conf = yaml.load(open(config_file), Loader=yaml.FullLoader)
    if threshold is not None:
        conf['ramping']['threshold'] = threshold
        conf['output']['path'] = conf['output']['path'] + f'/thresh_{threshold:.2f}'
    thresh = conf['ramping'].get('threshold', 0.1)
    thresh_str = f"{thresh:.2f}" 

    # define swingdoor functions
    def swingdoor_func(x, thresh):
        # Process data with swinging door method.

        # Remove NaN values but keep timestamp alignment
        valid_mask = ~x.isna()
        x_clean = x[valid_mask]
        gp = np.array(x_clean)
        timestamp_gp = np.array(x_clean.index)

        dev = thresh * gp.max()

        len_gp = len(gp)
        magnitude, rate, duration = np.zeros(len_gp), np.zeros(len_gp), np.zeros(len_gp)
        # Temporary arrays used for swinging door method
        ratemin, ratemax = np.zeros(len_gp), np.zeros(len_gp)
        magnitude_c, rate_c, duration_c, timestamp_c = np.zeros(len_gp), np.zeros(len_gp), np.zeros(
            len_gp), np.zeros(len_gp, dtype='datetime64[ns]')
        
        # swinging door algorithm
        magnitude[0] = gp[0]
        i = 0  # index of this group, gp
        m = 0  # index of compressed data set
        while i < len_gp - 1:
            magnitude[i] = gp[i]

            magnitude_c[m] = magnitude[i]
            timestamp_c[m] = timestamp_gp[i]
            j = 1
            while j < len_gp - i:
                # print(j)
                magnitude[i + j] = gp[i + j]
                rate[i + j] = (magnitude[i + j] - magnitude[i]) / (j)
                ratemax[i + j] = (magnitude[i + j] - magnitude[i] + dev) / (j)
                ratemin[i + j] = (magnitude[i + j] - magnitude[i] - dev) / (j)
                flag = 0
                for k in range(1, j+1):
                    if (ratemax[i + k] < rate[i + j]) | (ratemin[i + k] > rate[i + j]):
                        flag = 1
                        break
                if flag == 1:
                    # set rate value for data points from i to i+j-2
                    newrate = (magnitude[i + j - 1] - magnitude[i]) / (j-1)
                    for k in range(1, j):
                        rate[i + k - 1] = newrate
                        duration[i + k - 1] = j - k - 1
                    break
                else:
                    j += 1
            # when searching reaches the end of gp, store the rate value
            # for data points from i to i+j-2 (2nd to laast data point).
            # rate and duration of the last data point can not be determined
            if j == len_gp - i:
                newrate = (magnitude[i + j - 1] - magnitude[i]) / (j-1)
                for k in range(1, j):
                    rate[i + k - 1] = newrate
                    duration[i + k - 1] = j - k - 1
            rate_c[m], duration_c[m] = rate[i], duration[i]
            i = i + j - 1
            m += 1
        # set rate and duration for the last data point

        magnitude_c = np.trim_zeros(magnitude_c, 'b')
        rate_c = np.trim_zeros(rate_c, 'b')
        duration_c = np.trim_zeros(duration_c, 'b')
   
        len_c = min(len(magnitude_c), len(rate_c), len(duration_c))
        magnitude_c = magnitude_c[:len_c]
        rate_c = rate_c[:len_c]
        duration_c = duration_c[:len_c]
        timestamp_c = timestamp_c[:len_c]

        return magnitude_c, rate_c, duration_c, timestamp_c

    def compute_sd_single(x):
        """Run swinging door on a single series using its native timestamps."""
        mag, rate, dur, t = swingdoor_func(x, thresh)
        if len(rate) < len(t):
            rate = np.append(rate, 0)
        if len(dur) < len(t):
            dur = np.append(dur, 0)
        rate = rate[:len(t)]
        dur = dur[:len(t)]
        mag_df = pd.DataFrame({x.name: mag}, index=t)
        rate_df = pd.DataFrame({x.name: rate}, index=t)
        dur_df = pd.DataFrame({x.name: dur}, index=t)
        return mag_df, rate_df, dur_df


    def compute_sd_single(x):
        """Run swinging door on a single series using its native timestamps."""
        mag, rate, dur, t = swingdoor_func(x, thresh)
        if len(rate) < len(t):
            rate = np.append(rate, 0)
        if len(dur) < len(t):
            dur = np.append(dur, 0)
        rate = rate[:len(t)]
        dur = dur[:len(t)]
        mag_df = pd.DataFrame({x.name: mag}, index=t)
        rate_df = pd.DataFrame({x.name: rate}, index=t)
        dur_df = pd.DataFrame({x.name: dur}, index=t)
        return mag_df, rate_df, dur_df

    def compute_sd(x, y, freq):
        freq_str = f"{freq}min" if freq < 60 else f"{freq // 60}h"
        base_mag, base_rate, base_dur, base_t = swingdoor_func(x, thresh)
        comp_mag, comp_rate, comp_dur, comp_t = swingdoor_func(y, thresh)
        joined_mag = pd.DataFrame(base_mag, index=base_t).merge(pd.DataFrame(comp_mag, index=comp_t), how='outer',
                                                                left_index=True, right_index=True).ffill().resample(
            freq_str).ffill()
        if len(base_rate) < len(base_t):
            base_rate = np.append(base_rate, 0)
        if len(comp_rate) < len(comp_t):
            comp_rate = np.append(comp_rate, 0)
        joined_rate = pd.DataFrame(base_rate[:len(base_t)], index=base_t).merge(
            pd.DataFrame(comp_rate[:len(comp_t)], index=comp_t), how='outer', left_index=True,
            right_index=True).ffill().resample(freq_str).ffill()
        if len(base_dur) < len(base_t):
            base_dur = np.append(base_dur, 0)
        if len(base_dur) > len(base_t): 
            base_dur = base_dur[:len(base_t)]

        if len(comp_dur) < len(comp_t):
            comp_dur = np.append(comp_dur, 0)
        df = pd.DataFrame(base_dur, index=base_t)
        df = pd.concat([df, pd.DataFrame({0: 0}, index=df.index[1:] - pd.Timedelta(minutes=freq))])
        b_dur = df[~df.index.duplicated(keep='first')].sort_index().resample(freq_str).interpolate()
        df = pd.DataFrame(comp_dur[:len(comp_t)], index=comp_t)
        df = pd.concat([df, pd.DataFrame({0: 0}, index=df.index[1:] - pd.Timedelta(minutes=freq))])
        c_dur = df[~df.index.duplicated(keep='first')].sort_index().resample(freq_str).interpolate()
        joined_dur = b_dur.merge(c_dur, how='outer', left_index=True, right_index=True)
        joined_mag, joined_rate, joined_dur = [df.rename(columns={'0_x': base['name'], '0_y': c['name']}) for df in
                                               [joined_mag, joined_rate, joined_dur]]
        return joined_mag, joined_rate, joined_dur

    
    # set base and comparison configurations from config file
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
    ramp_plotting = eval_tools.get_module_class('plotting', 'plot_ramp')(conf)
    # For data storage and metrics computation
    results = []

    print()
    print('********** for '+base['name']+': **********')

    # Run __init__

    base['input'] = eval_tools.get_module_class(
        'inputs', base['function'])(base, conf)

    base['data'] = base['input'].get_ts()

    # Optional: run swingdoor on only the base dataset at native timestamps.
    if conf.get('ramping', {}).get('run_base_only', False) and conf.get('ramping', {}).get('run_comparison', True):
        ramp_cfg = conf.get('ramping', {})
        val_start = ramp_cfg.get('start', conf['time']['window']['start'])
        val_end = ramp_cfg.get('end', conf['time']['window']['end'])
        base_ts = base['data'].loc[(base['data'].index >= val_start) & (base['data'].index <= val_end)]

        if isinstance(base_ts, pd.DataFrame):
            base_series = base_ts.iloc[:, 0].copy()
            base_series.name = base['name']
        else:
            base_series = base_ts.copy()
            base_series.name = base['name']

        base_mag_df, base_rate_df, base_dur_df = compute_sd_single(base_series)

        if 'output' in conf:
            output_path = os.path.join((pathlib.Path(os.getcwd())), conf['output']['path'])
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if conf['output'].get('save_metrics', False):
                base_mag_df.to_csv(os.path.join(output_path, f"{conf['output']['org']}_swingdoor_base_native_mag.csv"))
                base_rate_df.to_csv(os.path.join(output_path, f"{conf['output']['org']}_swingdoor_base_native_ramp.csv"))
                base_dur_df.to_csv(os.path.join(output_path, f"{conf['output']['org']}_swingdoor_base_native_dur.csv"))

            if conf['output'].get('save_figs', False) or conf['output'].get('show_figs', False):
                ramp_plotting.plot_ramp_ts_single(base_mag_df, base_rate_df, base_dur_df, base['name'])

                ramp_plotting.plot_ramp_ts_single_diagnostic(base_series, base_mag_df, base_rate_df, base_dur_df, base['name'])

        print(f"Base-only swingdoor computed at native timestamps for {base['name']} ({len(base_mag_df)} points).")

    #Uncomment if need to check for outliers in the base data 
    # base_diff = base['data'].diff()
    # base_diff.to_csv('base_data_diff.csv', index=True)
    # summary = {
    # 'max': base_diff.max(),
    # 'min': base_diff.min(),
    # 'mean': base_diff.mean(),
    # 'median': base_diff.median(),
    # 'std': base_diff.std()
    # }
    # print(summary)
    # max_index = base_diff.idxmax()  # timestamp of maximum value
    # min_index = base_diff.idxmin()  # timestamp of minimum value

    # print(f"Max value occurred at {max_index}")
    # print(f"Min value occurred at {min_index}")

    # For each specified comparison dataset
    analysis = conf['analysis']
    start = conf['time']['window']['start']
    method = conf['reference']['select_method']
    all_latex_tables = []
    all_comp_df = pd.DataFrame()

    for ind, c in enumerate(comp):

        print()
        print('********** for '+c['name']+': **********')
        
        # Run __init__
        c['input'] = eval_tools.get_module_class(
            'inputs', c['function'])(c, conf)

        c['data'] = c['input'].get_ts()
        # c['data'].columns = [c['name']]
        # plotting.plot_ts_line_monthly_compare_only(c['data'])

        combine_df = crosscheck_ts.align_time(base, c)

        if all_comp_df.empty:
            all_comp_df = combine_df.copy()
        else:
            # keep the base's original timestamps; just align each comparison onto them
            all_comp_df = all_comp_df.merge(
                combine_df[[c['name']]], left_index=True, right_index=True, how='left')

        max_freq = max(c['freq'], base['freq'])
        if max_freq >= 60:
            max_freq_str = f"{max_freq // 60}h"
        else:
            max_freq_str = f"{max_freq}min"
        ramp_cfg = conf.get('ramping', {})
        run_ramp_comparison = ramp_cfg.get('run_comparison', True)
        if run_ramp_comparison and any('swingdoor' in i for i in analysis):
            ramp_start = ramp_cfg.get('start', conf['time']['window']['start'])
            ramp_end = ramp_cfg.get('end', conf['time']['window']['end'])
            ramp_df = combine_df.loc[(combine_df.index >= ramp_start) & (combine_df.index <= ramp_end)]
            magnitude, ramprate, duration = compute_sd(ramp_df[base['name']], ramp_df[c['name']], max_freq)

            swingdoor_ts = {
                            'swingdoor-mag':magnitude,
                            'swingdoor-ramp':ramprate,
                            'swingdoor-dur':duration
                            }
            ramp_plotting.plot_ramp_ts(swingdoor_ts, ramp_df)
            if ramp_cfg.get('plot_compare_diagnostic', False):
                ramp_plotting.plot_ramp_ts_compare_diagnostic(ramp_df, swingdoor_ts, base['name'], c['name'])
            
        results = eval_tools.append_results(results, base, c, analysis[0])

       
        
        for a_ind, analysis_type in enumerate(analysis):
            # Crosscheck between datasets

            # skip swingdoor comparison metrics if ramping comparison is disabled
            if 'swingdoor' in analysis_type and not run_ramp_comparison:
                continue

            if 'swingdoor' in analysis_type:
                full_df = swingdoor_ts[analysis_type].copy(deep=True)
            else:
                full_df = combine_df.copy(deep=True)
            
            cal_print_metrics_csv.run(
                full_df, metrics, results, ind, c, conf, base, aggregations, analysis_type
                )
        
            for a in results[ind][analysis_type].keys():


                if any('swingdoor' in i for i in analysis):
                    dfname = 'metrics_' + analysis_type +'_' + c['name'] + '_' + a + '_' + method + '_' + max_freq_str + '_' + thresh_str
                else: 
                    dfname = 'metrics_' + analysis_type +'_' + c['name'] + '_' + a + '_' + method + '_' + max_freq_str 

                metricstat_dict = {key: results[ind][analysis_type][a][key]
                                for key in conf['metrics']}
                metricstat_df = pd.DataFrame.from_dict(metricstat_dict, orient='columns')
 
                if a == 'H' and hasattr(metricstat_df.index, '__iter__'):
                    if any(isinstance(idx, tuple) for idx in metricstat_df.index):
                        metricstat_df.index = pd.date_range(start, periods=len(metricstat_df), freq='h')
                if conf['output']['print_results'] is True:
                    if a == "MS" or a == "D":
                        print(f"Metrics for {dfname}:")
                        print(metricstat_df)  
                globals()[dfname] = metricstat_df

                if 'output' in conf:

                    output_path = os.path.join(
                        (pathlib.Path(os.getcwd())), conf['output']['path']
                    )

                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

                    if conf['output']['save_metrics'] is True:
                        globals()[dfname].to_csv(os.path.join(output_path, conf['output']['org'] + '_' + dfname + '.csv'))
                    if conf['output']['save_to_pdf'] is True:
                        latex_table = csv_to_pdf.add_df_to_latex(metricstat_df, dfname, a)
                        all_latex_tables.append(latex_table)
                        if 'swingdoor' in analysis_type and conf['output']['save_ramping_comparison'] is True:
                            ramp_start = conf['ramping']['start']
                            ramp_end = conf['ramping']['end']
                            ramp_latex = csv_to_pdf.create_ramping_tables( swingdoor_ts, combine_df, conf, max_freq_str, c, ramp_start, ramp_end)
                            csv_to_pdf.save_ramping_to_pdf(ramp_latex, output_path, conf, title="WE-Validate Ramping Analysis")


        # latex_table = csv_to_pdf.create_ramping_tables()

    # plotting.plot_ts_line(all_comp_df)
    # plotting.plot_ts_line_monthly(all_comp_df)
    plotting.plot_ts_line_monthly_compare_only(all_comp_df)
    plotting.plot_histogram(all_comp_df)
    # plotting.plot_ts_line_seasonal(all_comp_df)
    # plotting.plot_ts_line_single_month(all_comp_df, month = 6, self_units=True)
    # plotting.plot_ts_line_monthly_compare_only_last_2(all_comp_df, self_units=True)
    # plotting.plot_histogram_monthly(all_comp_df)
    # plotting.plot_pair_scatter(all_comp_df)
    # try:
    #     plotting.plot_pair_scatter_monthly(all_comp_df)
    # except np.linalg.LinAlgError:
    #     plt.rcParams.update(plt.rcParamsDefault)
    #     plt.close('all')
    #     # plt.clf()         # Clear current figure 
    #     # plt.cla()         # Clear current axes
    #     # plt.rcParams.update(plt.rcParamsDefault)

    #     # # Reset matplotlib's date converters which might be corrupted
    #     # import matplotlib.units as munits
    #     # import matplotlib.dates as mdates
    #     # munits.registry.clear()
    #     # from pandas.plotting import register_matplotlib_converters
    #     # register_matplotlib_converters(explicit=True)

    #     print("Skipping scatter plot due to insufficient data for regression analysis")

    if conf['output']['save_to_pdf'] is True:
        if conf['output']['save_figs'] is True: 

            # Get all PNG files 
            png_files = glob.glob(os.path.join(output_path, "*.png"))
            plot_files = [f for f in png_files if conf['base']['name'] in os.path.basename(f)]
            
            # Generate PDF with plots
            csv_to_pdf.generate_pdf_report(all_latex_tables, output_path, conf, 
                                        title="WE-Validate Summary", plot_files=plot_files)
        else: 
            csv_to_pdf.generate_pdf_report(all_latex_tables, output_path, conf, title="WE-Validate Summary")

if __name__ == '__main__':
    compare(config = config)

