# This is a simple average capacity factor difference calculation 
# average capacity factor = mean(x-y)  / capacity

#Lauren Henderson <lauren.henderson at pnnl.gov>

import numpy as np


class acfd:

    def compute(self, x, y, z):

        return float(np.mean(x - y) / z )