# This script contains data plotting functions for csv files.
#
# This module is also called in other scripts.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import os
import pathlib


class plot_data_csv:
    """Class for plotting 1 dimensional data at 1 height level."""

    def __init__(self, conf):

        self.var = conf['reference']['var']

        self.savefig = conf['output']['save_figs']

        self.showfig = conf['output']['show_figs']

        self.path = conf['output']['path']

        self.org = conf['output']['org']

        if conf['reference']['units'] == 'ms-1':
            self.units = r'm $s^{-1}$'
        else:
            self.units = conf['reference']['units']

    def plot_ts_line(self, df, self_units=True):
        """Represent time series for each data column as a line,
        combine the lines in one plot.
        """

        for col in df.columns:
            plt.plot(df.index, df[col], label=col)

        plt.xticks(rotation=90)
        plt.legend()

        plt.xlabel('time')

        if self_units is True:
            plt.ylabel(self.var + ' (' + self.units + ')')
        else:
            plt.ylabel(self.var)

        plt.title(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])

        plt.show()

    def plot_pair_scatter(self, df, self_units=True):
        """Generate scatter plots for each column pair."""

        # 1:1 line and text color
        onetoone_c = 'grey'
        # Best fit line color
        fit_c = 'green'

        for pair in itertools.combinations(df.columns, 2):

            fig, ax = plt.subplots()

            plt.scatter(df[pair[0]], df[pair[1]], c='k')

            line_min = np.nanmin([df[pair[0]], df[pair[1]]])
            line_max = np.nanmax([df[pair[0]], df[pair[1]]])
            xy1to1 = np.linspace(line_min * 0.9, line_max * 1.1)

            plt.plot(xy1to1, xy1to1, c=onetoone_c, linestyle='--')
            plt.text(0.95, 0.9, '1:1', c=onetoone_c, transform=ax.transAxes)

            if self_units is True:
                plt.xlabel(pair[0] + ' (' + self.units + ')')
                plt.ylabel(pair[1] + ' (' + self.units + ')')
            else:
                plt.xlabel(pair[0])
                plt.ylabel(pair[1])

            compute_df = df.dropna()
            x_fit = compute_df[pair[0]]
            y_fit = compute_df[pair[1]]

            # np.polyfit(deg=1) is linear regression
            coeffs = np.polyfit(x_fit, y_fit, 1)
            model_fn = np.poly1d(coeffs)

            # Calculate R^2 for the fit
            yhat = model_fn(x_fit)
            ybar = np.sum(y_fit) / len(y_fit)
            ssreg = np.sum((yhat - ybar) ** 2)
            sstot = np.sum((y_fit - ybar) ** 2)
            r2 = ssreg / sstot

            # For linear regression, this works too
            # from scipy import stats
            # slope, intercept, r_value, p_value, std_err = stats.linregress(
            #     x_fit, y_fit)

            x_s = np.arange(compute_df.min().min(), compute_df.max().max())

            plt.plot(x_s, model_fn(x_s), color=fit_c)

            # Linear equation for title
            plt.title(self.var + ' '
                      + '\n linear fit: ' + pair[0] + ' = '
                      + str(round(coeffs[0], 3))
                      + ' * ' + pair[1] + ' + ' + str(round(coeffs[1], 3))
                      + r'$, R{^2} = $' + str(round(r2, 3))
                      )

            plt.show()

    def plot_histogram(self, df):
        """Generate histogram for each data column."""

        for col in df.columns:
            plt.hist(df[col], bins=15, alpha=0.4, label=col)

        plt.legend()

        plt.xlabel(self.var + ' (' + self.units + ')')
        plt.ylabel('count')
        plt.title(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])

        plt.show()

    def plot_ts_line_monthly(self, df, self_units=True):
        """Represent time series for each data column as a line,
        combine the lines in one plot.
        """

        months = df.index.month.unique()
        num_figures = len(months)
        grid_size = math.ceil(math.sqrt(num_figures))

        plt.rcParams["figure.figsize"] = (30, 15)
        # Set the default text font size
        plt.rc('font', size=16)
        # Set the axes title font size
        plt.rc('axes', titlesize=16)
        # Set the axes labels font size
        plt.rc('axes', labelsize=16)
        # Set the font size for x tick labels
        plt.rc('xtick', labelsize=16)
        # Set the font size for y tick labels
        plt.rc('ytick', labelsize=16)
        # Set the legend font size
        plt.rc('legend', fontsize=18)
        # Set the font size of the figure title
        plt.rc('figure', titlesize=20)

        count = 1
        for month in months:
            selected_month = df[df.index.month == month]
            plt.subplot(grid_size, grid_size, count)

            for col in df.columns:
                plt.plot(selected_month.index, selected_month[col], label=col)
            count += 1
            plt.title(selected_month.index.strftime("%B").any())
            plt.tight_layout(rect=[0,0,1,0.95])
            plt.xticks(rotation=90)
            plt.suptitle(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])

            if self_units is True:
                plt.ylabel(self.var + ' (' + self.units + ')')
            else:
                plt.ylabel(self.var)

        plt.legend()
        plt.show()
        plt.rcParams.update(plt.rcParamsDefault)

    def plot_ts_line_monthly_metric(self, monthly_dict, self_units=False):
        """Represent time series for each data column as a line,
        combine the lines in one plot.
        """
        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

        num_plots = sum(isinstance(val, pd.Series) for val in monthly_dict.values())
        grid_size = math.ceil(math.sqrt(num_plots))

        plt.rcParams["figure.figsize"] = (10, 5)

        count = 1
        for i, (key, val) in enumerate(monthly_dict.items()):
            if isinstance(val, pd.Series):
                plt.subplot(grid_size, grid_size, count)
                plt.plot(val.index, val, label=key)
                count += 1

            plt.xticks(rotation=90)
            plt.title(key)
            plt.tight_layout(rect=[0,0,1,0.95])
            suptitle = 'Monthly Metrics: ' + monthly_dict['base'] + " - "+ monthly_dict['compare']
            plt.suptitle(suptitle)

        plt.savefig(output_path + '\\monthly_metrics_' + monthly_dict['base'] + "-"+ monthly_dict['compare'] + '_' + self.org + '.png')
        plt.show()

        # if self.savefig is True & self.showfig is True:
        #     plt.savefig(output_path + '\\monthly_metrics_' + self.org + '.png')
        #     plt.show()
        #
        # elif self.savefig is True & self.showfig is False:
        #     plt.savefig(output_path + '\\monthly_metrics_' + self.org + '.png')



