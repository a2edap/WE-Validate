# This is a basic parser for NREL Toolkit NetCDF data.
#
# This input parser expects to be given a directory filled with netcdf
# files - each a grid at one particular time.
#
# We expect that the file has a field called latitude which is a matrix of
# latitude values for the grid and longitude which is a matrix of longitude
# values for the grid.

import os
import pathlib
from datetime import datetime
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from qc import check_input_data


class nrel_toolkit_netcdf:
    """NREL Toolkit data class, using data from NetCDF files.
    Each NetCDF file should contain 1 time step of data.
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

        try:
            self.select_method = conf['reference']['select_method']
        except KeyError:
            self.select_method = 'instance'

    # For WRF mountain wave demo case
    def get_ij(self, ih):
        """Return data index (i and j) for nc file at a specified target
        location.
        """

        # squeeze out time dimension from latitude and longitude
        lat = np.array(ih['latitude'])
        lat = np.squeeze(lat, axis= 0)
        lon = np.array(ih['longitude'])
        lon = np.squeeze(lon, axis=0)

        # If lat/lon were arrays (instead of matrixes)
        # something like this would work:
        # d = np.fromfunction(lambda x,y: (lon[x] - loc['lon'])**2
        # + (lat[y] - loc['lat'])**2, (len(lon), len(lat)), dype=float)

        # This is most appropriate for Equator coordinates
        d = (lat - self.loc['lat'])**2 + (lon - self.loc['lon'])**2

        i, j = np.unravel_index(np.argmin(d), d.shape)

        return i, j

    def get_ts(self, lev):
        """Get time series at a location at a certain height.
        Resample data according to user-defined data frequency.
        """
        self.var2 = self.var + "_" + str(lev) + "m"

        df = pd.DataFrame({'t': [], self.target_var: []})

        # To print an empty line before masked value error messages
        mask_i = 0

        for file in os.listdir(self.path):
            data = Dataset(os.path.join(self.path, file), 'r')
            i, j = self.get_ij(data)

            s = file.split('_')[3]+'_'+file.split('_')[4].split('.')[0]+':'\
                + file.split('_')[5]+':'+file.split('_')[6].split('.')[0]

            t = datetime.strptime(s, '%Y-%m-%d_%H:%M:%S')

            ws = data.variables[self.var2][0][i][j]

            ws, mask_i = check_input_data.convert_mask_to_nan(ws, t, mask_i)
            ws = check_input_data.convert_flag_to_nan(ws, self.flag, t)

            data.close()

            df = pd.concat([df, pd.DataFrame.from_records([{'t': t, self.target_var: ws}])])

        df = df.set_index('t').sort_index()

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

        df = check_input_data.verify_data_file_count(df, self.target_var,
                                                     self.path, self.freq
                                                     )

        return df