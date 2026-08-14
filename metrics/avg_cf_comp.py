# This is a simple average capacity factor calculation for the comparison dataset
# capacity factor = mean(y) / capacity
#Assuming y is the comparison data set 

#Lauren Henderson <lauren.henderson at pnnl.gov>

import numpy as np


class avg_cf_comp:

    def compute(self, x, y, z):

        return float(np.mean(y) / z )