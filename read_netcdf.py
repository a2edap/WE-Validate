import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import xarray as xr

datadir = r"C:\Users\monc573\PycharmProjects\a2e_wevalidate\WE-Validate\data\2km_pnnl"

df = xr.open_dataset(datadir +"\wtk_ts.nc")

df.values
df.var
df.dims
df.coords
df.attrs

df.latitude
df.windspeed_10m

lat = df.latitude.sel()

lat.plot()
plt.show()

dir = r"C:\Users\monc573\PycharmProjects\a2e_wevalidate\WE-Validate\data\data_nrel_toolkit\custom_wrfout_d01_2018-09-23_00_00_00.nc"

dt = xr.open_dataset(dir)

dt.windspeed_10m
# latitude is constant
df.wind_speed.plot()

modeldir = r"C:\Users\monc573\PycharmProjects\WE-Validate\data\2km_pnnl"
dd = xr.open_dataset(modeldir + "\\" + "20160801_120000.nc")


def _read(datadir, site, time=None, height=None, freq=None):
    if site[0]=="L":
        prefix="lidar"
        vname='wind_speed'
    if site[0]=="S":
        prefix="sodar"
        vname='speed'
    if site in ["S03", "S04", "S07", "S10"]:
        prefix="sodar"
        vname='wind_speed'
    ds = xr.open_dataset(f"{datadir}/{prefix}_z{site[1:]}.nc")[vname].compute()
    if ds.size==0: return None
    if height is not None: ds = ds.sel(height=height)
    if freq is not None: ds = ds.resample(time=freq).nearest()
    if time is not None:
        time1, time2 = time
        ds = ds.sel(time=slice(time1, time2))
    return ds

def read(datadir, sitename, time=None, height=None, freq=None):
    if not isinstance(sitename, (tuple, list)): sitename = (sitename,)
    sitename_valid = []
    ds = []
    for site in sitename:
        _ds = _read(datadir, site, time=time, height=height, freq=freq)
        if _ds is not None:
            sitename_valid.append(site)
            ds.append(_ds)
    ds = xr.concat(ds, dim='sites')
    ds.coords['sites'] = sitename_valid
    return ds

Lidar = ["L01", "L02", "L03", "L05", "L07", "L08"]
Sodar = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S10", "S12", "S18", "S14", "S17"]
sitename = Lidar + Sodar

start_day  = '2015-10-01'
end_day    = '2017-03-31'
start_hour = pd.to_datetime(start_day)+ pd.Timedelta('12H')
end_hour   = pd.to_datetime(end_day)+ pd.Timedelta('12H')

obs = read(datadir, sitename, time=(start_hour, end_hour), height=80, freq='15min')
print(obs)

modeldir = r"C:\Users\monc573\PycharmProjects\WE-Validate\data\2km_pnnl"

def read_wtk_ts_2km_pnnl(datadir, vname, time=None, site=None, height=None, freq=None):
    sitename = [
    "L01", "L02", "L03", "L05", "L07", "L08",
    "S01", "S02", "S03", "S04", "S05", "S06", "S07",
    "S10", "S12", "S18", "S14", "S17", "S20",
    ]
    vname = f'{vname}_{height}m'
    mod = xr.open_dataset(f'{datadir}/wtk_ts.nc')
    mod.coords['sites'] = ('sites', sitename)
    mod = mod[vname]

    if site is not None: mod = mod.sel(sites=site)
    if time is not None: mod = mod.sel(time=slice(*time))
    return mod

pnnl_2km = dataset_wtk.read_wtk_ts_2km_pnnl(modeldir, 'windspeed', time=(start_day, end_day), site=sitename,  height=80)
