#This is a Wasserstein distance calculation, which compares the value distribution of two datasets. 
#WD = mean(abs(sort(x) - sort(y)))

#Lauren Henderson <lauren.henderson at pnnl.gov>
import numpy as np

class wasserstein:

    def compute(self, x, y, z):
        # x is baseline
        assert len(x) == len(y)
        x_s = np.sort(x)
        y_s = np.sort(y)
        return np.mean(np.abs(x_s - y_s))