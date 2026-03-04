# This is a simple average capacity factor difference calculation 
# average capacity factor = mean(x-y)  / capacity

import numpy as np


class acfd:

    def compute(self, x, y, z):

        return float(np.mean(x - y) / z )