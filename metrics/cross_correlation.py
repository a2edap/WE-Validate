# This is a cross-correlation calculation,


import numpy as np


class cross_correlation:

    def compute(self, x, y):

        # x is baseline
        z = np.corrcoef(x, y)
        return float(z[0,1])
