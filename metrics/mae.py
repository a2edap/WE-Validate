# This is a simple average mae calculation, mae = mean(|x - y|).
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class mae:

    def compute(self, x, y):

        return float(np.mean(abs(x - y)))


# dummy code for monthly
# class mae_monthly:
#
#     def compute(self, x, y):
#
#         for i in range(1, 12):
#             mo = df.index.month == i
#             return float(np.mean(abs(x[mo] - y[mo])))

# dummy code for hourly
# class mae_hourly:
#
#     def compute(self, x, y):
#
#         for i in range(1, 24):
#             hr = df.index.hour == i
#             return float(np.mean(abs(x[hr] - y[hr])))

