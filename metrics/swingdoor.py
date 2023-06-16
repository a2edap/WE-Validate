
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%%
datadir = r'/Users/camp426/Library/CloudStorage/OneDrive-PNNL/Documents/PNNL/Projects/FY23/Active/GRAF-Plan/OSW_Travis/00_GRAF-Plan'
df = pd.read_csv(datadir+r'/coosBay_PNW20_2009_MT_5min_S1.csv').set_index('Time')
df.index=pd.to_datetime(df.index)
# %%

df_list = list(df.groupby(df.index.month))
x = df_list[0][1]
#%%
def swingdoor(x):
# Process data with swinging door method. 
#    (1) x.iloc[:,0] is the data series to be processed.
#    (2) The maximum error allowable is specified using "dev" parameter. 
#    (3)"dt" is the sampling interval of ACEData. 
#    (4) The new time stamp of the data series after processing is stored in
#    "tcomp".
#    (5) magnitude, rate and duration values along with each data point are stored in
#    "magnitude", "rate" and "duration", respectively.
    print(x.head())
    gp = np.array(x)
    timestamp_gp = np.array(x.index)
    dev = .1*gp.max()

    len_gp = len(gp)
    # len_gp = 200
    magnitude,rate,duration = np.zeros(len_gp),np.zeros(len_gp),np.zeros(len_gp)
    # Temperary arrays used for swinging door method
    ratemin,ratemax = np.zeros(len_gp),np.zeros(len_gp)
    magnitude_c,rate_c,duration_c,timestamp_c = np.zeros(len_gp),np.zeros(len_gp),np.zeros(len_gp),np.zeros(len_gp,dtype='datetime64[ns]')
    # swinging door algorithm
    magnitude[0] = gp[0]
    i = 0 # index of this group, gp
    m = 0 # index of compressed data set
    while i < len_gp:
        magnitude[i] = gp[i]
        magnitude_c[m] = magnitude[i]
        timestamp_c[m] = timestamp_gp[i]
        j = 0
        while j < len_gp - i:
            magnitude[i+j] = gp[i+j]
            rate[i+j] = (magnitude[i+j]-magnitude[i])/j
            ratemax[i+j] = (magnitude[i+j]-magnitude[i]+dev)/j
            ratemin[i+j] = (magnitude[i+j]-magnitude[i]-dev)/j
            flag = 0
            for k in range(j):
                if (ratemax[i+k] < rate[i+j]) | (ratemin[i+k]>rate[i+j]):
                    flag = 1
                    break
            if flag == 1:
                # set rate value for data points from i to i+j-2
                newrate = (magnitude[i+j-1]-magnitude[i])/(j-1)
                for k in range(j-1):
                    rate[i+k-1] = newrate
                    duration[i+k-1] = j-k
                break
            else:
                j +=1
        # when searching reaches the end of gp, store the rate value
        # for data points from i to i+j-2 (2nd to laast data point).
        # rate and duration of the last data point can not be determined
        if j == len_gp - i:
            newrate = (magnitude[i+j-1]-magnitude[i])/(j-1)
            for k in range(j-1):
                rate[i+k-1] = newrate
                duration[i+k-1] = j-k
        rate_c[m],duration_c[m] = rate[i],duration[i]
        i = i+j
        m +=1

    magnitude_c = np.trim_zeros(magnitude_c,'b')
    rate_c = np.trim_zeros(rate_c,'b')
    duration_c = np.trim_zeros(duration_c,'b')
    len_c = len(magnitude_c)
    timestamp_c = timestamp_c[:len_c]

    return magnitude_c,rate_c,duration_c,timestamp_c

#%%

b_mag,b_rate,b_dur,b_t = swingdoor(x.iloc[:,0])
c_mag,c_rate,c_dur,c_t = swingdoor(x.iloc[:,1])
plt.plot(b_t,b_dur)
plt.plot(c_t,c_dur)
plt.show()

# %%
