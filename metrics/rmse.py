# This is a naive root mean squared error (RMSE) calculation,
# rmse = root(mean((x - y)^2))
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class rmse:

    def compute(self, x, y, z):

        return float(np.sqrt(np.mean((x - y)**2)))
