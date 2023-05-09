# This script contains data plotting functions for csv files.
#
# This module is also called in other scripts.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools


class plot_data_csv:
    """Class for plotting 1 dimensional data at 1 height level."""

    def __init__(self, conf):

        self.var = conf['reference']['var']

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

            # my attempt to plot for every month
            # months = df.index.month.unique()
            # for month in months:
            #     month_data = df[df.index.month == month]
            #
            #     # plot the data for the current month
            #     plt.plot(month_data.index, month_data[col], label=month)

        plt.xticks(rotation=90)
        plt.legend()

        plt.xlabel('time')

        if self_units is True:
            plt.ylabel(self.var+' ('+self.units+')')
        else:
            plt.ylabel(self.var)

        plt.title(self.var + ': ' + df.columns[0] +' - ' + df.columns[1])

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
            xy1to1 = np.linspace(line_min*0.9, line_max*1.1)

            plt.plot(xy1to1, xy1to1, c=onetoone_c, linestyle='--')
            plt.text(0.95, 0.9, '1:1', c=onetoone_c, transform=ax.transAxes)

            if self_units is True:
                plt.xlabel(pair[0]+' ('+self.units+')')
                plt.ylabel(pair[1]+' ('+self.units+')')
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
            ybar = np.sum(y_fit)/len(y_fit)
            ssreg = np.sum((yhat - ybar)**2)
            sstot = np.sum((y_fit - ybar)**2)
            r2 = ssreg/sstot

            # For linear regression, this works too
            # from scipy import stats
            # slope, intercept, r_value, p_value, std_err = stats.linregress(
            #     x_fit, y_fit)

            x_s = np.arange(compute_df.min().min(), compute_df.max().max())

            plt.plot(x_s, model_fn(x_s), color=fit_c)

            # Linear equation for title
            plt.title(self.var+' '
                      + '\n linear fit: '+pair[0]+' = '
                      + str(round(coeffs[0], 3))
                      + ' * '+pair[1]+' + '+str(round(coeffs[1], 3))
                      + r'$, R{^2} = $'+str(round(r2, 3))
                      )

            plt.show()

    def plot_histogram(self, df):
        """Generate histogram for each data column."""

        for col in df.columns:
            plt.hist(df[col], bins=15, alpha=0.4, label=col)

        plt.legend()

        plt.xlabel(self.var+' ('+self.units+')')
        plt.ylabel('count')
        plt.title(self.var + ': ' + df.columns[0] +' - ' + df.columns[1])

        plt.show()

    def plot_ts_line_monthly(self, monthly_dict, self_units=False):
        """Represent time series for each data column as a line,
        combine the lines in one plot.
        """

        for key, val in monthly_dict.items():
            if isinstance(val, pd.Series):
                plt.plot(val.index, val, label=key)

            # my attempt to plot for every month
            # months = df.index.month.unique()
            # for month in months:
            #     month_data = df[df.index.month == month]
            #
            #     # plot the data for the current month
            #     plt.plot(month_data.index, month_data[col], label=month)

        plt.xticks(rotation=90)
        plt.legend()

        plt.xlabel('time')

        if self_units is True:
            plt.ylabel(self.var+' ('+self.units+')')
        else:
            plt.ylabel(self.var)

        plt.title(self.var + ': ' + monthly_dict['compare'] +' - ' + monthly_dict['base'])

        plt.show()

