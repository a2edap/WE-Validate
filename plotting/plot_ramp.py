import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import os
import pathlib
from pathlib import Path
import matplotlib.dates as mdates

class plot_ramp:
    """Plot ramping events from a reference dataset."""

    def __init__(self, conf):
        self.var = conf['reference']['var']

        self.savefig = conf['output']['save_figs']

        self.showfig = conf['output']['show_figs']

        self.path = conf['output']['path']
        output_path = Path(self.path)

        self.org = conf['output']['org']

        self.freq = max(conf['base']['freq'], conf['comp'][1]['freq'])
        if self.freq >= 60:
            self.freq_str = f"{self.freq // 60}h"
        else:
            self.freq_str = f"{self.freq}min"

        if conf['reference']['units'] == 'ms-1':
            self.units = r'm $s^{-1}$'
        else:
            self.units = conf['reference']['units']

    def plot_ramp_ts(self, sd, df):
            
        output_path = os.path.join(
                (pathlib.Path(os.getcwd())), self.path)
        
        plt.rcParams["figure.figsize"] = (20, 10)
        # Set the default text font size
        plt.rc('font', size=14)
        # Set the axes title font size
        plt.rc('axes', titlesize=16)
        # Set the axes labels font size
        plt.rc('axes', labelsize=16)
        # Set the font size for x tick labels
        plt.rc('xtick', labelsize=16)
        # Set the font size for y tick labels
        plt.rc('ytick', labelsize=16)
        # Set the legend font size
        plt.rc('legend', fontsize=16)
        # Set the font size of the figure title
        plt.rc('figure', titlesize=18)
        

        if self.savefig is True:

            mag_df = sd['swingdoor-mag']  
            rate_df = sd['swingdoor-ramp']  
            dur_df = sd['swingdoor-dur']  
        

            # Create figure and axes with shared x-axis
            fig, axes = plt.subplots(3, 1, sharex=True)
            for ax in axes:
                ax.tick_params(axis='x', labelrotation=45)  # Rotate x-axis labels

            # Plot magnitude
            axes[0].plot(mag_df.index, mag_df.iloc[:, 0])
            axes[0].plot(mag_df.index, mag_df.iloc[:, 1])
            axes[0].set_ylabel(f"Magnitude ({self.units})")
            axes[0].grid()

            # Plot ramp rate 
            axes[1].plot(rate_df.index, rate_df.iloc[:, 0])
            axes[1].plot(rate_df.index, rate_df.iloc[:, 1])
            axes[1].set_ylabel(f"Rate({self.units}/{self.freq_str})")
            axes[1].grid()

            # Plot duration
            axes[2].plot(dur_df.index, dur_df.iloc[:, 0], label=df.columns[0])
            axes[2].plot(dur_df.index, dur_df.iloc[:, 1], label=df.columns[1])
            axes[2].set_ylabel(f"Duration ({self.freq_str})")
            axes[2].legend()
            axes[2].grid()

            # Adjust layout
            fig.tight_layout(rect=[0, 0, 1, 0.95])

            plt.savefig(os.path.join(self.path, f'ramp_timeseries_{df.columns[0]}-{df.columns[1]}_{self.org}.png'), dpi=300,bbox_inches="tight")
            if self.showfig is True:
                plt.show()
            else:
                plt.close()


        if self.savefig is False:

            if self.showfig is True: 
                mag_df = sd['swingdoor-mag']  # Magnitude
                rate_df = sd['swingdoor-ramp']  # Ramp Rate
                dur_df = sd['swingdoor-dur']  # Duration
            

                # Create figure and axes with shared x-axis
                fig, axes = plt.subplots(3, 1, sharex=True, figsize=(9, 8))
                for ax in axes:
                    ax.tick_params(axis='x', labelrotation=45)

                # Plot magnitude
                axes[0].plot(mag_df.index, mag_df.iloc[:, 0])
                axes[0].plot(mag_df.index, mag_df.iloc[:, 1])
                axes[0].set_ylabel(f"Magnitude ({self.units})")
                axes[0].grid()

                # Plot ramp rate 
                axes[1].plot(rate_df.index, rate_df.iloc[:, 0])
                axes[1].plot(rate_df.index, rate_df.iloc[:, 1])
                axes[1].set_ylabel(f"Rate({self.units}/{self.freq_str})")
                axes[1].grid()

                # Plot duration
                axes[2].plot(dur_df.index, dur_df.iloc[:, 0], label=df.columns[0])
                axes[2].plot(dur_df.index, dur_df.iloc[:, 1], label=df.columns[1])
                axes[2].set_ylabel(f"Duration ({self.freq_str})")
                axes[2].set_xlabel("Date")
                axes[2].legend()
                axes[2].grid()

                plt.show()

        plt.rcParams.update(plt.rcParamsDefault)

    def plot_ramp_ts_monthly(self, sd, df):
        
        output_path = os.path.join(
            (pathlib.Path(os.getcwd())), self.path)
        
        months = pd.unique(sd['swingdoor-mag'].index.month)
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

            for month in months:
                selected_month_mag = sd['swingdoor-mag'][sd['swingdoor-mag'].index.month == month]
                selected_month_rate = sd['swingdoor-ramp'][sd['swingdoor-ramp'].index.month == month]
                selected_month_dur = sd['swingdoor-dur'][sd['swingdoor-dur'].index.month == month]

                fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 8))
                for ax in axes:
                    # ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))  # Tick every 3 days
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format: 'YYYY-MM-DD'
                    ax.tick_params(axis='x', labelrotation=45)  # Rotate x-axis labels

                # Plot magnitude
                axes[0].plot(selected_month_mag.index, selected_month_mag.iloc[:, 0])
                axes[0].plot(selected_month_mag.index, selected_month_mag.iloc[:, 1])
                axes[0].set_ylabel(f"Magnitude ({self.units})")
                axes[0].grid()

                # Plot ramp rate 
                axes[1].plot(selected_month_rate.index, selected_month_rate.iloc[:, 0])
                axes[1].plot(selected_month_rate.index, selected_month_rate.iloc[:, 1])
                axes[1].set_ylabel(f"Rate({self.units}/{self.freq_str})")
                axes[1].grid()

                # Plot duration
                axes[2].plot(selected_month_dur.index, selected_month_dur.iloc[:, 0], label=df.columns[0])
                axes[2].plot(selected_month_dur.index, selected_month_dur.iloc[:, 1], label=df.columns[1])
                axes[2].set_ylabel(f"Duration ({self.freq_str})")
                axes[2].set_xlabel("Date")
                axes[2].set_xlim(selected_month_dur.index.min(), selected_month_dur.index.max())
                axes[2].legend()
                axes[2].grid()

                # Adjust layout
                fig.tight_layout(rect=[0, 0, 1, 0.95])

                plt.savefig(os.path.join(self.path, f'ramp_timeseries_monthly{month}_{df.columns[0]}-{df.columns[1]}_{self.org}.png'), bbox_inches='tight')

            if self.showfig is True:
                plt.show()
            else:
                plt.close()


    
