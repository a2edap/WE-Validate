# This is a basic parser for site wind speed comparison csv data.
#
# This input parser expects to be given a csv file with wind speed at each timestep
#
# We expect that the file has a column called time_stamp which is a timestamp, and a column called wind_speed which contains the wind speed


import os
import pathlib
from datetime import datetime
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from qc import check_input_data


class csv:
    """wind speed data class, using data from a csv file.
    """

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd())), str(info['path'])
        )
        self.var = info['var']
        self.name = info['name']
        self.freq = info['freq']
        self.flag = info['flag']
        if 'df' in info:
            self.df = info['df'][info['path']]

        # self.loc = conf['location']

        try:
            self.select_method = conf['reference']['select_method']
        except KeyError:
            self.select_method = 'instance'

    def get_ts(self):
        """Get time series.
        """

        df = pd.read_csv(os.path.join(self.path))
        df.index = pd.to_datetime(df['time_stamp'])
        df = df[[self.var]]
        df = df.rename(columns={self.var: self.name})

        # Same process as in the crosscheck_ts class
        time_diff = df.index.to_series().diff()

        if len(time_diff[1:].unique()) == 1:

            if self.freq > time_diff[1].components.minutes:

                df = df.resample(
                    str(self.freq) + 'T', label='right',
                    closed='right')

                if self.select_method == 'average':
                    df = df.mean()
                if self.select_method == 'instance':
                    df = df.asfreq()

        return df

    def get_ts_gui(self):
        """Get time series.
        """

        df = self.df
        df.index = pd.to_datetime(df['time_stamp'])
        df = df[[self.var]]
        df = df.rename(columns={self.var: self.name})

        # Same process as in the crosscheck_ts class
        time_diff = df.index.to_series().diff()

        if len(time_diff[1:].unique()) == 1:

            if self.freq > time_diff[1].components.minutes:

                df = df.resample(
                    str(self.freq) + 'T', label='right',
                    closed='right')

                if self.select_method == 'average':
                    df = df.mean()
                if self.select_method == 'instance':
                    df = df.asfreq()

        return df
