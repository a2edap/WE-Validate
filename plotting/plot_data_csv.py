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

        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

        if self.savefig is True:

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
            plt.savefig(output_path + '\\timeseries_' + df.columns[0] + "-" + df.columns[
                1] + '_' + self.org + '.png')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:

            if self.showfig is True:

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



    def plot_ts_line_monthly(self, df, self_units=True):
        """Represent time series for each data column as a line,
        combine the lines in one plot per month.
        """
        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

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

        if self.savefig is True:

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

            plt.legend(bbox_to_anchor=(1, 0.5))
            plt.savefig(output_path + '\\timeseries_monthly_' + df.columns[0] + "-" + df.columns[
                1] + '_' + self.org + '.png', bbox_inches='tight')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:

            if self.showfig is True:

                count = 1
                for month in months:
                    selected_month = df[df.index.month == month]
                    plt.subplot(grid_size, grid_size, count)

                    for col in df.columns:
                        plt.plot(selected_month.index, selected_month[col], label=col)
                    count += 1
                    plt.title(selected_month.index.strftime("%B").any())
                    plt.tight_layout(rect=[0, 0, 1, 0.95])
                    plt.xticks(rotation=90)
                    plt.suptitle(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])

                    if self_units is True:
                        plt.ylabel(self.var + ' (' + self.units + ')')
                    else:
                        plt.ylabel(self.var)

                plt.legend(bbox_to_anchor=(1, 0.5))
                plt.show()


        plt.rcParams.update(plt.rcParamsDefault)

    def plot_pair_scatter(self, df, self_units=True):
        """Generate scatter plots for each column pair."""

        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

        # 1:1 line and text color
        onetoone_c = 'grey'
        # Best fit line color
        fit_c = 'green'

        if self.savefig is True:

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

                x_s = np.arange(compute_df.min().min(), compute_df.max().max())

                plt.plot(x_s, model_fn(x_s), color=fit_c)

                # Linear equation for title
                plt.title(self.var + ' '
                          + '\n linear fit: ' + pair[0] + ' = '
                          + str(round(coeffs[0], 3))
                          + ' * ' + pair[1] + ' + ' + str(round(coeffs[1], 3))
                          + r'$, R{^2} = $' + str(round(r2, 3))
                          )

                plt.savefig(output_path + '\\scatterplot_' + df.columns[0] + "-" + df.columns[
                    1] + '_' + self.org + '.png')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:

            if self.showfig is True:

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

    def plot_pair_scatter_monthly(self, df, self_units=True):
        """Generate scatter plots for each column pair for each month."""

        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

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

        # 1:1 line and text color
        onetoone_c = 'grey'
        # Best fit line color
        fit_c = 'green'


        if self.savefig is True:

            count = 1
            for month in months:
                selected_month = df[df.index.month == month]
                plt.subplot(grid_size, grid_size, count)

                for pair in itertools.combinations(selected_month.columns, 2):

                    plt.scatter(selected_month[pair[0]], selected_month[pair[1]], c='k')


                    line_min = np.nanmin([selected_month[pair[0]], selected_month[pair[1]]])
                    line_max = np.nanmax([selected_month[pair[0]], selected_month[pair[1]]])
                    xy1to1 = np.linspace(line_min * 0.9, line_max * 1.1)

                    plt.plot(xy1to1, xy1to1, c=onetoone_c, linestyle='--')

                    if self_units is True:
                        plt.xlabel(pair[0] + ' (' + self.units + ')')
                        plt.ylabel(pair[1] + ' (' + self.units + ')')
                    else:
                        plt.xlabel(pair[0])
                        plt.ylabel(pair[1])

                    compute_selected_month = selected_month.dropna()
                    x_fit = compute_selected_month[pair[0]]
                    y_fit = compute_selected_month[pair[1]]

                    # np.polyfit(deg=1) is linear regression
                    coeffs = np.polyfit(x_fit, y_fit, 1)
                    model_fn = np.poly1d(coeffs)

                    # Calculate R^2 for the fit
                    yhat = model_fn(x_fit)
                    ybar = np.sum(y_fit) / len(y_fit)
                    ssreg = np.sum((yhat - ybar) ** 2)
                    sstot = np.sum((y_fit - ybar) ** 2)
                    r2 = ssreg / sstot

                    x_s = np.arange(compute_selected_month.min().min(), compute_selected_month.max().max())

                    plt.plot(x_s, model_fn(x_s), color=fit_c)
                    count += 1

                    # Linear equation for title
                    plt.title(selected_month.index.strftime("%B").any() + ' '
                              + '\n linear fit: ' + pair[0] + ' = '
                              + str(round(coeffs[0], 3))
                              + ' * ' + pair[1] + ' + ' + str(round(coeffs[1], 3)) + '\n'
                              + r'$ R{^2} = $' + str(round(r2, 3))
                              )

                    plt.tight_layout(rect=[0, 0, 1, 0.9])
                    suptitle = 'Monthly ' + self.var + ' Scatterplot: ' + selected_month.columns[0] + " - " + selected_month.columns[1]
                    plt.suptitle(suptitle)

                    plt.savefig(output_path + '\\scatterplot_monthly_' + selected_month.columns[0] + "-" + selected_month.columns[
                        1] + '_' + self.org + '.png')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:
            if self.showfig is True:

                count = 1
                for month in months:
                    selected_month = df[df.index.month == month]
                    plt.subplot(grid_size, grid_size, count)

                    for pair in itertools.combinations(selected_month.columns, 2):

                        plt.scatter(selected_month[pair[0]], selected_month[pair[1]], c='k')

                        line_min = np.nanmin([selected_month[pair[0]], selected_month[pair[1]]])
                        line_max = np.nanmax([selected_month[pair[0]], selected_month[pair[1]]])
                        xy1to1 = np.linspace(line_min * 0.9, line_max * 1.1)

                        plt.plot(xy1to1, xy1to1, c=onetoone_c, linestyle='--')

                        if self_units is True:
                            plt.xlabel(pair[0] + ' (' + self.units + ')')
                            plt.ylabel(pair[1] + ' (' + self.units + ')')
                        else:
                            plt.xlabel(pair[0])
                            plt.ylabel(pair[1])

                        compute_selected_month = selected_month.dropna()
                        x_fit = compute_selected_month[pair[0]]
                        y_fit = compute_selected_month[pair[1]]

                        # np.polyfit(deg=1) is linear regression
                        coeffs = np.polyfit(x_fit, y_fit, 1)
                        model_fn = np.poly1d(coeffs)

                        # Calculate R^2 for the fit
                        yhat = model_fn(x_fit)
                        ybar = np.sum(y_fit) / len(y_fit)
                        ssreg = np.sum((yhat - ybar) ** 2)
                        sstot = np.sum((y_fit - ybar) ** 2)
                        r2 = ssreg / sstot

                        x_s = np.arange(compute_selected_month.min().min(), compute_selected_month.max().max())

                        plt.plot(x_s, model_fn(x_s), color=fit_c)
                        count += 1

                        # Linear equation for title
                        plt.title(selected_month.index.strftime("%B").any() + ' '
                                  + '\n linear fit: ' + pair[0] + ' = '
                                  + str(round(coeffs[0], 3))
                                  + ' * ' + pair[1] + ' + ' + str(round(coeffs[1], 3))+ '\n'
                                  + r'$ R{^2} = $' + str(round(r2, 3))
                                  )

                        plt.tight_layout(rect=[0, 0, 1, 0.9])
                        suptitle = 'Monthly ' + self.var + ' Scatterplot: ' + selected_month.columns[0] + " - " + \
                                   selected_month.columns[1]
                        plt.suptitle(suptitle)

                plt.show()

        plt.rcParams.update(plt.rcParamsDefault)

    def plot_histogram(self, df):
        """Generate histogram for each data column."""

        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

        if self.savefig is True:

            for col in df.columns:
                plt.hist(df[col], bins=15, alpha=0.4, label=col)

            plt.legend()

            plt.xlabel(self.var + ' (' + self.units + ')')
            plt.ylabel('count')
            plt.title(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])
            plt.savefig(output_path + '\\histogram_' + df.columns[0] + "-" + df.columns[1] + '_' + self.org + '.png')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:

            if self.showfig is True:

                for col in df.columns:
                    plt.hist(df[col], bins=15, alpha=0.4, label=col)

                plt.legend()

                plt.xlabel(self.var + ' (' + self.units + ')')
                plt.ylabel('count')
                plt.title(self.var + ': ' + df.columns[0] + ' - ' + df.columns[1])

                plt.show()


    def plot_histogram_monthly(self, df):
        """Generate histogram for each data column for each month."""

        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)

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

        if self.savefig is True:

            count = 1
            for month in months:
                selected_month = df[df.index.month == month]
                plt.subplot(grid_size, grid_size, count)

                for col in df.columns:
                    plt.hist(selected_month[col], bins=15, alpha=0.4, label=col)
                count += 1

                plt.xlabel(self.var + ' (' + self.units + ')')
                plt.ylabel('count')
                plt.title(selected_month.index.strftime("%B").any())
                plt.tight_layout(rect=[0, 0, 1, 0.95])
                suptitle = 'Monthly Histogram: ' + df.columns[0] + " - "+ df.columns[1]
                plt.suptitle(suptitle)
                plt.savefig(output_path + '\\histogram_monthly_' + df.columns[0] + "-" + df.columns[
                    1] + '_' + self.org + '.png')

            plt.legend()

            if self.showfig is True:
                plt.show()
            else:
                plt.close()

        if self.savefig is False:

            if self.showfig is True:

                count = 1
                for month in months:
                    selected_month = df[df.index.month == month]
                    plt.subplot(grid_size, grid_size, count)

                    for col in df.columns:
                        plt.hist(selected_month[col], bins=15, alpha=0.4, label=col)
                    count += 1

                    plt.xlabel(self.var + ' (' + self.units + ')')
                    plt.ylabel('count')
                    plt.title(selected_month.index.strftime("%B").any())
                    plt.tight_layout(rect=[0, 0, 1, 0.95])
                    suptitle = 'Monthly Histogram: ' + df.columns[0] + " - " + df.columns[1]
                    plt.suptitle(suptitle)

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

        if self.savefig is True:

            count = 1
            for i, (key, val) in enumerate(monthly_dict.items()):
                if isinstance(val, pd.Series):
                    plt.subplot(grid_size, grid_size, count)
                    # plt.plot(val.index, val, label=key)
                    plt.plot(val.index.strftime("%y-%m"), val, label=key)
                    count += 1

                plt.xticks(rotation=90)

                if str(key).endswith('pct'):
                    plt.ylabel('Percent (%)')
                else:
                    plt.ylabel(self.var + ' (' + self.units + ')')

                plt.title(key)
                plt.tight_layout(rect=[0,0,1,0.95])
                suptitle = 'Monthly Metrics: ' + monthly_dict['base'] + " - "+ monthly_dict['compare']
                plt.suptitle(suptitle)
                plt.savefig(output_path + '\\metrics_monthly_' + monthly_dict['base'] + "-"+ monthly_dict['compare'] + '_' + self.org + '.png', bbox_inches='tight')

            if self.showfig is True:
                plt.show()

            else:
                plt.close()

        if self.savefig is False:
            if self.showfig is True:
                count = 1
                for i, (key, val) in enumerate(monthly_dict.items()):
                    if isinstance(val, pd.Series):
                        plt.subplot(grid_size, grid_size, count)
                        plt.plot(val.index.strftime("%y-%m"), val, label=key)
                        count += 1

                        plt.xticks(rotation=90)

                        if str(key).endswith('pct'):
                            plt.ylabel('Percent (%)')
                        else:
                            plt.ylabel(self.var + ' (' + self.units + ')')

                        plt.title(key)
                        plt.tight_layout(rect=[0, 0, 1, 0.95])
                        suptitle = 'Monthly Metrics: ' + monthly_dict['base'] + " - " + monthly_dict['compare']
                        plt.suptitle(suptitle)

                plt.show()