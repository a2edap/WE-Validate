# This is a simple weighted average percent absolute error calculation,
# wmape = sum(|x - y|) / sum(|x|),
# assuming x is the truth.
#
# Lauren Henderson <lauren.henderson at pnnl.gov>

import numpy as np 

class wmape: 
    def compute(self, x, y, z):

        numerator = np.sum(np.abs(x - y))
        denominator = np.sum(np.abs(x))

        if denominator == 0:
            print('- in calculating wmape percentage, denominator is zero')
            print('led to undefined results (division by zero), returning NaN.')
            return float('nan')

        fraction_array = np.ma.masked_invalid(numerator/denominator)

        invalid_num = fraction_array.mask.sum()

        if invalid_num > 0:
            print()
            print('- in calculating mae percentage, '
                  + str(invalid_num)+' invalid data points, which would have')
            print('led to undefined results '
                  + '(e.g., division by zero), are ignored.')
            
            
        return float(fraction_array)