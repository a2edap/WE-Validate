# Overlapping Coefficient (OVL)

import numpy as np
from sklearn.neighbors import KernelDensity

class ovl:
    """Overlapping Coefficient (OVL)

    Measures the similarity between two probability distributions by
    calculating the area of intersection between their Kernel Density Estimates.

    Range: 0 to 100 (100 is a perfect match)
    """

    def __init__(self, kernel='gaussian'):
        self.kernel = kernel

    def _estimate_overlap(self, x, y, grid=None):
        """Helper function to calculate OVL based on user-provided code.
        x: baseline data (observation)
        y: comparison data (simulation)
        grid: grid for KDE
        """
        # Ensure inputs are numpy arrays and handle NaNs
        x = np.asarray(x)
        y = np.asarray(y)
        mask = ~np.isnan(x) & ~np.isnan(y)
        x = x[mask].reshape(-1, 1)
        y = y[mask].reshape(-1, 1)

        # Handle case with too few data points for KDE, which requires at least 2.
        if len(x) < 2 or len(y) < 2:
            return np.nan

        kde_obs = KernelDensity(kernel=self.kernel).fit(x)
        kde_pred = KernelDensity(kernel=self.kernel).fit(y)

        if grid is None:
            xmin = min(np.min(x), np.min(y))
            xmax = max(np.max(x), np.max(y))
            grid = np.linspace(xmin, xmax, 1000)[:, np.newaxis]

        p = np.exp(kde_obs.score_samples(grid))
        q = np.exp(kde_pred.score_samples(grid))
        return np.trapz (np.minimum(p, q), grid.ravel())

    def compute(self, x, y):
        """Compute OVL.

        x: baseline data (observation)
        y: comparison data (simulation)
        """
        overlap_coeff = self._estimate_overlap(x, y)
        # Return as a percentage for similarity score
        return overlap_coeff * 100
