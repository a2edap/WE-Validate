# This is a cross-correlation calculation,


import numpy as np


class cross_correlation:

    def compute(self, x, y, z):

        # x is baseline
        q = np.corrcoef(x, y)
        return float(q[0,1])
