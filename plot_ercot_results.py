import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np

FOLDERS = f'output/ERCOT_PLUSWIND_yearly_hsl'
OUTPUT_NAME = f'output/ERCOT_plant_comparison_summary.csv'

all_data = {}
folders = [f for f in os.listdir(FOLDERS) 
              if os.path.isdir(os.path.join(FOLDERS, f)) and f.isdigit()]

for plant in folders:
    plant_id = int(plant)
    plant_path = os.path.join(FOLDERS, plant)

    csv_files = glob.glob(os.path.join(plant_path, f'ERCOT {plant_id} 2018_metrics_base_analysis_PLUSWIND_YE_average_15min.csv'))
    if csv_files: 
        df = pd.read_csv(csv_files[0])

        metrics = {}
        metric_names = ['rmse', 'crmse', 'bias', 'mae', 'bias_pct', 'mae_pct', 'cross_correlation', 'ovl']

        for metric in metric_names:
            metrics[metric] = df[metric].iloc[0]

        all_data[plant_id] = metrics

result_df = pd.DataFrame(all_data).T
result_df = result_df.reindex(sorted(result_df.columns), axis=1)
result_df = result_df.sort_index()
result_df = result_df.T
print('number of columns: ', len(result_df.columns))
result_df.to_csv(OUTPUT_NAME)
print(f"Summary CSV saved to: {OUTPUT_NAME}")

#Plot the results for all plants 
# cross_corr_data = result_df.loc['cross_correlation']
# plt.figure(figsize=(10, 6))
# bins = np.arange(0.62, 1.01, 0.01)

# plt.hist(cross_corr_data.values, bins=bins, alpha=0.7, edgecolor='black')
# plt.xlabel('Cross Correlation')
# plt.ylabel('Number of Plants')
# plt.title('Distribution of Yearly Cross Correlation Values for all 2018 ERCOT Plants Compared to PLUSWIND')
# plt.grid(True, alpha=0.3)

# mean_val = cross_corr_data.mean().round(2)
# median_val = cross_corr_data.median().round(2)
# plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
# plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
# plt.legend()

# plt.tight_layout()
# plt.show()

# mae_pct_data = result_df.loc['mae_pct']
# plt.figure(figsize=(10, 6))
# bins = np.arange(0, 41, 1)

# plt.hist(mae_pct_data.values, bins=bins, alpha=0.7, edgecolor='black')
# plt.xlabel('MAE Percentage (%)')
# plt.ylabel('Number of Plants')
# plt.title('Distribution of Yearly MAE Percentage Values for all 2018 ERCOT Plants Compared to PLUSWIND')
# plt.grid(True, alpha=0.3)

# mean_val = mae_pct_data.mean()
# median_val = mae_pct_data.median()
# plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
# plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
# plt.legend()

# plt.tight_layout()
# plt.show()

bias_pct_data = result_df.loc['bias_pct']
plt.figure(figsize=(10, 6))
bins = np.arange(0, 41, 1)

plt.hist(bias_pct_data.values, bins=bins, alpha=0.7, edgecolor='black')
plt.xlabel('Bias Percentage (%)')
plt.ylabel('Number of Plants')
plt.title('Distribution of Yearly Bias Percentage Values for all 2018 ERCOT Plants Compared to PLUSWIND')
plt.grid(True, alpha=0.3)

mean_val = bias_pct_data.mean()
median_val = bias_pct_data.median()
plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
plt.legend()

plt.tight_layout()
plt.show()