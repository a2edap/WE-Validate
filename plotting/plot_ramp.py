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
        self.thresh = conf['ramping'].get('threshold', 0.1)
        self.base_freq = conf['base']['freq']

        self.freq = max(conf['base']['freq'], conf['comp'][0]['freq'])
        if self.freq >= 60:
            self.freq_str = f"{self.freq // 60}h"
        else:
            self.freq_str = f"{self.freq}min"

        if conf['reference']['units'] == 'ms-1':
            self.units = r'm $s^{-1}$'
        else:
            self.units = conf['reference']['units']

    def _format_freq_label(self, minutes):
        """Format a frequency label from minutes."""
        if minutes is None or minutes <= 0:
            return self.freq_str
        if minutes % 60 == 0:
            hours = minutes // 60
            return f"{hours}h"
        return f"{minutes}min"

    def _native_freq_label(self, index):
        """Infer native frequency label from a datetime index."""
        if len(index) < 2:
            return self.freq_str

        diffs = pd.Series(index).diff().dropna()
        if diffs.empty:
            return self.freq_str

        minutes = int(round(diffs.dt.total_seconds().median() / 60.0))
        return self._format_freq_label(minutes)

    def _format_freq_label(self, minutes):
        """Format a frequency label from minutes."""
        if minutes is None or minutes <= 0:
            return self.freq_str
        if minutes % 60 == 0:
            hours = minutes // 60
            return f"{hours}h"
        return f"{minutes}min"

    def _native_freq_label(self, index):
        """Infer native frequency label from a datetime index."""
        if len(index) < 2:
            return self.freq_str

        diffs = pd.Series(index).diff().dropna()
        if diffs.empty:
            return self.freq_str

        minutes = int(round(diffs.dt.total_seconds().median() / 60.0))
        return self._format_freq_label(minutes)

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
            axes[2].legend()
            axes[2].grid()

            # Adjust layout
            fig.tight_layout(rect=[0, 0, 1, 0.95])

            plt.savefig(os.path.join(self.path, f'Ramp_Timeseries_{df.columns[0]}-{df.columns[1]}_{self.org}.png'), dpi=300,bbox_inches="tight")
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
                selected_month = sd['swingdoor-mag'][sd['swingdoor-mag'].index.month == month]
                selected_month_mag = sd['swingdoor-mag'][sd['swingdoor-mag'].index.month == month]
                selected_month_rate = sd['swingdoor-ramp'][sd['swingdoor-ramp'].index.month == month]
                selected_month_dur = sd['swingdoor-dur'][sd['swingdoor-dur'].index.month == month]

                # Create figure and axes with shared x-axis
                fig, axes = plt.subplots(3, 1, sharex=True)
                for ax in axes:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  
                    ax.tick_params(axis='x', labelrotation=45) 

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
                plt.title(selected_month.index.strftime("%B")[0] )
                plt.savefig(os.path.join(self.path, f'Ramp_Timeseries_Monthly_{selected_month.index.strftime("%B")[0]}_{df.columns[0]}-{df.columns[1]}_{self.org}.png'), dpi=300, bbox_inches='tight')

            if self.showfig is True:
                plt.show()
            else:
                plt.close()
        if self.savefig is False: 
            if self.showfig is True: 
                for month in months:
                    selected_month = sd[sd.index.month == month]
                    selected_month_mag = sd['swingdoor-mag'][sd['swingdoor-mag'].index.month == month]
                    selected_month_rate = sd['swingdoor-ramp'][sd['swingdoor-ramp'].index.month == month]
                    selected_month_dur = sd['swingdoor-dur'][sd['swingdoor-dur'].index.month == month]

                    # Create figure and axes with shared x-axis
                    fig, axes = plt.subplots(3, 1, sharex=True)
                    for ax in axes:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  
                        ax.tick_params(axis='x', labelrotation=45) 

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
                    plt.title(selected_month.index.strftime("%B")[0] )

                    plt.show()

        plt.rcParams.update(plt.rcParamsDefault)

    def plot_ramp_ts_single(self, mag_df, rate_df, dur_df, base_name):
        """Plot base-only swingdoor magnitude/rate/duration on native timestamps."""
        if (self.savefig is False) and (self.showfig is False):
            return

        native_freq_str = self._format_freq_label(self.base_freq)

        plt.rcParams["figure.figsize"] = (20, 10)
        fig, axes = plt.subplots(3, 1, sharex=True)

        axes[0].plot(mag_df.index, mag_df.iloc[:, 0], label=base_name)
        axes[0].set_ylabel(f"Magnitude ({self.units})")
        axes[0].grid()
        axes[0].legend()

        axes[1].plot(rate_df.index, rate_df.iloc[:, 0], label=base_name)
        axes[1].axhline(0, color='0.4', linewidth=0.8)
        axes[1].set_ylabel(f"Rate ({self.units}/{native_freq_str})")
        axes[1].grid()
        axes[1].legend()

        axes[2].step(dur_df.index, dur_df.iloc[:, 0], where='post', label=base_name)
        axes[2].set_ylabel(f"Duration ({native_freq_str})")
        axes[2].set_xlabel("Date")
        axes[2].grid()
        axes[2].legend()

        fig.tight_layout(rect=[0, 0, 1, 0.98])

        if self.savefig is True:
            os.makedirs(self.path, exist_ok=True)
            plt.savefig(
                os.path.join(self.path, f"Ramp_Timeseries_BaseOnly_{self.org}.png"),
                dpi=300,
                bbox_inches="tight"
            )

        if self.showfig is True:
            plt.show()
        else:
            plt.close()

        plt.rcParams.update(plt.rcParamsDefault)

    def plot_ramp_ts_single_diagnostic(self, raw_series, mag_df, rate_df, dur_df, base_name):
        """Plot side-by-side diagnostics to verify detected ramps against original series."""
        if (self.savefig is False) and (self.showfig is False):
            return

        native_freq_str = self._format_freq_label(self.base_freq)

        plt.rcParams["figure.figsize"] = (22, 10)
        fig, axes = plt.subplots(3, 2, sharex='col')

        axes[0, 0].plot(raw_series.index, raw_series.values, color='0.7', linewidth=1.2, label='Original')
        axes[0, 0].plot(mag_df.index, mag_df.iloc[:, 0], color='tab:blue', linewidth=1.5, label='Swingdoor Magnitude')
        axes[0, 0].set_title('Original vs Swingdoor Magnitude')
        axes[0, 0].set_ylabel(f"Magnitude ({self.units})")
        axes[0, 0].grid()
        axes[0, 0].legend(loc='best')

        axes[1, 0].plot(rate_df.index, rate_df.iloc[:, 0], color='tab:orange', linewidth=1.2)
        axes[1, 0].axhline(0, color='0.4', linewidth=0.8)
        axes[1, 0].set_title('Swingdoor Ramp Rate')
        axes[1, 0].set_ylabel(f"Rate ({self.units}/{native_freq_str})")
        axes[1, 0].grid()

        axes[2, 0].step(dur_df.index, dur_df.iloc[:, 0], where='post', color='tab:green', linewidth=1.2)
        axes[2, 0].set_title('Swingdoor Duration')
        axes[2, 0].set_ylabel(f"Duration ({native_freq_str})")
        axes[2, 0].set_xlabel('Date')
        axes[2, 0].grid()

        axes[0, 1].plot(raw_series.index, raw_series.values, color='tab:gray', linewidth=1.0)
        axes[0, 1].set_title('Original Time Series')
        axes[0, 1].set_ylabel(f"Magnitude ({self.units})")
        axes[0, 1].grid()

        axes[1, 1].plot(mag_df.index, mag_df.iloc[:, 0], color='tab:blue', linewidth=1.3)
        axes[1, 1].set_title('Swingdoor Magnitude Only')
        axes[1, 1].set_ylabel(f"Magnitude ({self.units})")
        axes[1, 1].grid()

        axes[2, 1].plot(rate_df.index, rate_df.iloc[:, 0], color='tab:orange', linewidth=1.2, label='Rate')
        ax2 = axes[2, 1].twinx()
        ax2.step(dur_df.index, dur_df.iloc[:, 0], where='post', color='tab:green', linewidth=1.1, alpha=0.8, label='Duration')
        axes[2, 1].set_title('Rate and Duration Overlay')
        axes[2, 1].set_ylabel(f"Rate ({self.units}/{native_freq_str})")
        ax2.set_ylabel(f"Duration ({native_freq_str})")
        axes[2, 1].set_xlabel('Date')
        axes[2, 1].grid()

        rate_lines, rate_labels = axes[2, 1].get_legend_handles_labels()
        dur_lines, dur_labels = ax2.get_legend_handles_labels()
        axes[2, 1].legend(rate_lines + dur_lines, rate_labels + dur_labels, loc='best')

        thresh_mw = self.thresh * raw_series.max()
        fig.suptitle(
            f'Swingdoor Ramp Diagnostic ({base_name})\n'
            f'Threshold: {self.thresh * 100:.1f}% = {thresh_mw:.1f} MW',
            fontsize=14
        )
        fig.tight_layout(rect=[0, 0, 1, 0.97])

        if self.savefig is True:
            os.makedirs(self.path, exist_ok=True)
            plt.savefig(
                os.path.join(self.path, f"Ramp_Diagnostic_BaseOnly_{self.org}_{self.thresh}.png"),
                dpi=300,
                bbox_inches="tight"
            )

        if self.showfig is True:
            plt.show()
        else:
            plt.close()

        plt.rcParams.update(plt.rcParamsDefault)

    def plot_ramp_ts_compare_diagnostic(self, raw_df, swingdoor_ts, base_name, comp_name):
        """Plot side-by-side diagnostics for base AND comparison swingdoor outputs.

        Left column = base, right column = comparison.
        Row 0: original time series vs swingdoor magnitude.
        Row 1: swingdoor ramp rate.
        Row 2: swingdoor duration.
        """
        if (self.savefig is False) and (self.showfig is False):
            return

        mag_df  = swingdoor_ts['swingdoor-mag']
        rate_df = swingdoor_ts['swingdoor-ramp']
        dur_df  = swingdoor_ts['swingdoor-dur']

        freq_str = self.freq_str

        plt.rcParams["figure.figsize"] = (24, 12)
        fig, axes = plt.subplots(3, 2, sharex='col')

        # ---- left column: base ----
        axes[0, 0].plot(raw_df.index, raw_df.iloc[:, 0], color='0.7', linewidth=1.0, label='Original')
        axes[0, 0].plot(mag_df.index, mag_df.iloc[:, 0], color='tab:blue', linewidth=1.5, label='Swingdoor')
        axes[0, 0].set_title(f'Base: {base_name} — Original vs Swingdoor')
        axes[0, 0].set_ylabel(f"Magnitude ({self.units})")
        axes[0, 0].legend(loc='best')
        axes[0, 0].grid()

        axes[1, 0].plot(rate_df.index, rate_df.iloc[:, 0], color='tab:orange', linewidth=1.2)
        axes[1, 0].axhline(0, color='0.4', linewidth=0.8)
        axes[1, 0].set_title('Base Ramp Rate')
        axes[1, 0].set_ylabel(f"Rate ({self.units}/{freq_str})")
        axes[1, 0].grid()

        axes[2, 0].step(dur_df.index, dur_df.iloc[:, 0], where='post', color='tab:green', linewidth=1.2)
        axes[2, 0].set_title('Base Duration')
        axes[2, 0].set_ylabel(f"Duration ({freq_str})")
        axes[2, 0].set_xlabel('Date')
        axes[2, 0].grid()

        # ---- right column: comparison ----
        axes[0, 1].plot(raw_df.index, raw_df.iloc[:, 1], color='0.7', linewidth=1.0, label='Original')
        axes[0, 1].plot(mag_df.index, mag_df.iloc[:, 1], color='tab:red', linewidth=1.5, label='Swingdoor')
        axes[0, 1].set_title(f'Comp: {comp_name} — Original vs Swingdoor')
        axes[0, 1].set_ylabel(f"Magnitude ({self.units})")
        axes[0, 1].legend(loc='best')
        axes[0, 1].grid()

        axes[1, 1].plot(rate_df.index, rate_df.iloc[:, 1], color='tab:red', linewidth=1.2)
        axes[1, 1].axhline(0, color='0.4', linewidth=0.8)
        axes[1, 1].set_title('Comp Ramp Rate')
        axes[1, 1].set_ylabel(f"Rate ({self.units}/{freq_str})")
        axes[1, 1].grid()

        axes[2, 1].step(dur_df.index, dur_df.iloc[:, 1], where='post', color='tab:purple', linewidth=1.2)
        axes[2, 1].set_title('Comp Duration')
        axes[2, 1].set_ylabel(f"Duration ({freq_str})")
        axes[2, 1].set_xlabel('Date')
        axes[2, 1].grid()

        thresh_mw = self.thresh * raw_df.iloc[:, 0].max()
        fig.suptitle(
            f'Swingdoor Ramp Diagnostic — {base_name} vs {comp_name}\n'
            f'Threshold: {self.thresh * 100:.1f}% = {thresh_mw:.1f} MW',
            fontsize=14
        )
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        if self.savefig is True:
            os.makedirs(self.path, exist_ok=True)
            plt.savefig(
                os.path.join(self.path, f"Ramp_Diagnostic_Compare_{base_name}-{comp_name}_{self.org}.png"),
                dpi=300,
                bbox_inches="tight"
            )

        if self.showfig is True:
            plt.show()
        else:
            plt.close()

        plt.rcParams.update(plt.rcParamsDefault)

