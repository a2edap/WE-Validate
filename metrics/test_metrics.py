# This script runs unit tests for metrics files.

import importlib
import pandas as pd
import math

from tools import cal_print_metrics_csv, eval_tools

test_dir = 'metrics'

# Example data series
x_eg = pd.Series([2, 2, 2, 2, 16])
y_eg = pd.Series([4, 5, 6, -7, 8])


def read_metric(metric):

    return eval_tools.get_module_class(test_dir, metric)()


def test_bias():

    assert read_metric('bias').compute(5, 4) == -1


def test_series_bias():

    assert read_metric('bias').compute(x_eg, y_eg) == -1.6


def test_bias_pct():

    assert read_metric('bias_pct').compute(5, 4) == -20


def test_series_bias_pct():

    assert read_metric('bias_pct').compute(x_eg, y_eg) == -10


def test_mae():

    assert read_metric('mae').compute(5, 4) == 1


def test_series_mae():

    assert read_metric('mae').compute(x_eg, y_eg) == 5.2


def test_mae_pct():

    assert read_metric('mae_pct').compute(5, 4) == 20


def test_series_mae_pct():

    assert read_metric('mae_pct').compute(x_eg, y_eg) == 190


def test_series_rmse():

    result = read_metric('rmse').compute(x_eg, y_eg)

    assert math.isclose(result, 5.899, rel_tol=1e-4)


def test_series_crmse():

    result = read_metric('crmse').compute(x_eg, y_eg)

    assert math.isclose(result, 5.678, rel_tol=1e-4)


def test_seasonal_metrics_pool_winter_samples():
    timestamps = pd.to_datetime([
        '2025-01-01', '2025-02-01', '2025-03-01',
        '2025-06-01', '2025-09-01', '2025-12-01'
    ])
    base = pd.Series([0, 0, 0, 0, 0, 0], index=timestamps)
    comparison = pd.Series([0, 0, 1, 2, 3, 9], index=timestamps)

    result = cal_print_metrics_csv.calc_metrics(
        base, comparison, 'QS-DEC', func=read_metric('rmse').compute, z=1
    )

    assert list(result.index) == ['Winter', 'Spring', 'Summer', 'Fall']
    assert math.isclose(result.loc['Winter'], math.sqrt(27))
    assert list(result.iloc[1:]) == [1, 2, 3]


def test_seasonal_metrics_pool_years_and_keep_missing_seasons():
    timestamps = pd.to_datetime([
        '2024-01-01', '2024-12-01', '2025-02-01', '2025-12-01'
    ])
    base = pd.Series([0, 0, 0, 0], index=timestamps)
    comparison = pd.Series([0, 4, 0, 8], index=timestamps)

    result = cal_print_metrics_csv.calc_metrics(
        base, comparison, 'QS-DEC', func=read_metric('rmse').compute, z=1
    )

    assert list(result.index) == ['Winter', 'Spring', 'Summer', 'Fall']
    assert math.isclose(result.loc['Winter'], math.sqrt(20))
    assert result.iloc[1:].isna().all()


def test_seasonal_metrics_pass_capacity():
    timestamps = pd.to_datetime(['2025-01-01', '2025-12-01'])
    base = pd.Series([10, 10], index=timestamps)
    comparison = pd.Series([10, 20], index=timestamps)

    result = cal_print_metrics_csv.calc_metrics(
        base, comparison, 'QS-DEC', func=read_metric('bias_pct').compute, z=100
    )

    assert math.isclose(result.loc['Winter'], 5)
