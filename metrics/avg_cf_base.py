# This is a simple average capacity factor calculation for the base dataset
# capacity factor = mean(x) / capacity
#Assuming x is the base data set 

#Lauren Henderson <lauren.henderson at pnnl.gov>

import numpy as np


class avg_cf_base:

    def compute(self, x, y, z):

        return float(np.mean(x) / z )
