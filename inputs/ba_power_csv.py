# This is a basic parser for balancing autority power production csv data.
#
# This input parser expects to be given a csv file with power production at each timestep
#
# We expect that the file has a column called time_stamp which is a timestamp, and a column called power which contains the power
# values for the grid.

import os
import pathlib
from datetime import datetime
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from qc import check_input_data


class ba_power_csv:
    """Balancing authority power data class, using data from a csv file.
    """

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd())), str(info['path'])
            )
        self.var = info['var']
        self.target_var = info['target_var']
        self.freq = info['freq']
        self.flag = info['flag']

        self.loc = conf['location']

        self.BA = conf['BA']

        try:
            self.select_method = conf['reference']['select_method']
        except KeyError:
            self.select_method = 'instance'



    def get_ts(self):
        """Get time series.
        """

        df = pd.read_csv(os.path.join(self.path))
        df.index = pd.to_datetime(df['time_stamp'])
       # df = df.drop(columns=['time_stamp'])
        df = df[[self.BA]]
        df = df.rename(columns={self.BA: self.target_var})

        # Same process as in the crosscheck_ts class
        time_diff = df.index.to_series().diff()

        if len(time_diff[1:].unique()) == 1:

            if self.freq > time_diff[1].components.minutes:

                df = df.resample(
                    str(self.freq)+'T', label='right',
                    closed='right')

                if self.select_method == 'average':
                    df = df.mean()
                if self.select_method == 'instance':
                    df = df.asfreq()

        return df