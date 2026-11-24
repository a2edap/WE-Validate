"""
Capacity-based timestamp filtering module. Filters validation timestamps based on available capacity thresholds.
"""
import pandas as pd
from pathlib import Path


def save_filter_stats(config, capacity_mask, exception_mask, index, nameplate_capacity,
                      threshold_percent, tolerance_mw):
    """Save a one-row summary of the capacity filter to the configured output directory."""
    total = len(index)
    final_mask = capacity_mask | exception_mask
    removed = int((~final_mask).sum())
    exceptions_retained = int((~capacity_mask & exception_mask).sum())
    retained = int(final_mask.sum())
    stats = {
        'nameplate_capacity_mw': nameplate_capacity,
        'minimum_capacity_threshold_mw': nameplate_capacity * threshold_percent / 100.0,
        'minimum_capacity_threshold_percent': threshold_percent,
        'actual_vs_available_tolerance_mw': tolerance_mw,
        'total_timestamps': total,
        'timestamps_below_threshold_or_missing': int((~capacity_mask).sum()),
        'timestamps_removed': removed,
        'timestamps_removed_percent': 100 * removed / total if total else 0.0,
        'timestamps_retained_by_exception': exceptions_retained,
        'timestamps_retained_by_exception_percent': 100 * exceptions_retained / total if total else 0.0,
        'timestamps_after_filtering': retained,
        'timestamps_after_filtering_percent': 100 * retained / total if total else 0.0,
        'date_start': index.min(),
        'date_end': index.max(),
    }
    output = config['output']
    output_dir = Path(output['path'])
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([stats]).to_csv(
        output_dir / f"{output['org']}_capacity_filter_stats.csv", index=False
    )

class CapacityFilter:
    """
    Filter validation timestamps based on available nameplate capacity.
    
    This filter removes timestamps where available capacity is below a specified threshold. However, timestamps where actual generation significantly exceeds available capacity are retained.
    """

    def __init__(self, config, base_data, available_capacity_data):
        self.config = config
        self.base_data = base_data
        self.available_capacity_data = available_capacity_data

        # Extract filtering configuration with safe defaults
        filter_config = config.get('capacity_filtering', {})
        self.enabled = filter_config.get('enabled', False)
        self.threshold_percent = filter_config.get('threshold_percent', 95.0)
        self.tolerance_mw = filter_config.get('actual_vs_available_tolerance_mw', 15)
        self.save_stats = filter_config.get('save_config_stats', False)

        # Extract capacity value
        self.nameplate_capacity = float(config.get('capacity', max(self.base_data.max(), self.available_capacity_data.max())))

        # Calculate threshold value in MW
        self.min_capacity_threshold = self.nameplate_capacity * (self.threshold_percent / 100.0)

    def _validate_inputs(self):
        """
        Validate that inputs are properly aligned and have required data.
        """
        if self.base_data is None or len(self.base_data) == 0:
            raise ValueError("Base data is empty")

        if self.available_capacity_data is None or len(self.available_capacity_data) == 0:
            raise ValueError("Available capacity data is empty")

        if len(self.base_data) != len(self.available_capacity_data):
            raise ValueError(f"Data length mismatch: base={len(self.base_data)}, "f"available={len(self.available_capacity_data)}")

        if not self.base_data.index.equals(self.available_capacity_data.index):
            raise ValueError("Data timestamps are not aligned")

        return True

    def _calculate_capacity_mask(self):
        # Timestamps where available capacity >= threshold
        capacity_sufficient = self.available_capacity_data >= self.min_capacity_threshold
        return capacity_sufficient

    def _calculate_exception_mask(self):
        """
        Calculate boolean mask for timestamps where actual generation significantly exceeds available capacity.
        """
        # Calculate the difference: actual - available
        generation_above_available = self.base_data - self.available_capacity_data

        # Timestamps where actual exceeds available by more than tolerance
        exception_mask = generation_above_available >= self.tolerance_mw

        return exception_mask

    def _generate_filter_report(self, capacity_mask, exception_mask, combined_df):
        """
        Save filtering statistics when enabled.
        """
        if not self.save_stats:
            return

        save_filter_stats(
            self.config, capacity_mask, exception_mask, combined_df.index,
            self.nameplate_capacity, self.threshold_percent, self.tolerance_mw
        )

    def apply_filtering(self, combined_df):
        """
        Apply capacity-based filtering to the combined dataframe.
        """
        if not self.enabled:
            return combined_df

        # Validate that inputs are properly prepared
        self._validate_inputs()

        # Calculate filtering masks
        capacity_mask = self._calculate_capacity_mask()
        exception_mask = self._calculate_exception_mask()

        # Combined mask: retain if either capacity threshold met OR exception applies
        final_mask = capacity_mask | exception_mask

        # Generate statistics before filtering
        self._generate_filter_report(capacity_mask, exception_mask, combined_df)

        # Apply filter to combined dataframe
        filtered_df = combined_df[final_mask].copy()

        return filtered_df

    def get_filtering_config(self):
        """
        Return the active filtering configuration for reference/logging.
        """
        return {
            'enabled': self.enabled,
            'nameplate_capacity_mw': self.nameplate_capacity,
            'threshold_percent': self.threshold_percent,
            'min_capacity_threshold_mw': self.min_capacity_threshold,
            'actual_vs_available_tolerance_mw': self.tolerance_mw,
        }