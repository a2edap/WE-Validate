import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

YEARS = [2018, 2019, 2020, 2021]
TIME_PERIODS  = ['', 'day', 'night']
plot_ovl_data = []
plot_cc_data = []
plot_acfd_data = []

for YEAR in YEARS:
    FOLDERS = f'output/{YEAR}/ERCOT_PLUSWIND_yearly_hsl'
    
    folders = [f for f in os.listdir(FOLDERS) 
                if os.path.isdir(os.path.join(FOLDERS, f))]
    for time_period in TIME_PERIODS:
        all_data = {}
        for plant in folders:
            plant_id = plant
            plant_path = os.path.join(FOLDERS, plant)
            if time_period == '':
                file_pattern = f'ERCOT {plant_id} {YEAR}_metrics_base_analysis_PLUSWIND_YE_average_15min.csv'
                time_period_label = 'Overall'
                csv_suffix = 'overall'
            else:
                file_pattern = f'ERCOT {plant_id} {YEAR}_metrics_base_analysis_PLUSWIND_YE_{time_period}_average_15min.csv'
                time_period_label = time_period.title()
                csv_suffix = time_period
            csv_files = glob.glob(os.path.join(plant_path, file_pattern))

            if csv_files: 
                df = pd.read_csv(csv_files[0])

                metrics = {}
                metric_names = ['rmse', 'crmse', 'bias', 'mae', 'bias_pct', 'mae_pct', 'cross_correlation', 'ovl', 'acfd']

                for metric in metric_names:
                    metrics[metric] = df[metric].iloc[0]

                all_data[plant_id] = metrics
                # Collect OVL data for plotting
                ovl_data = {
                    'Year': YEAR,
                    'Plant_ID': plant_id,
                    'Time_Period': time_period_label,
                    'OVL': metrics['ovl']
                }
                plot_ovl_data.append(ovl_data)

                cc_data = {
                    'Year': YEAR,
                    'Plant_ID': plant_id,
                    'Time_Period': time_period_label,
                    'Cross_Correlation': metrics['cross_correlation']
                }
                plot_cc_data.append(cc_data)

                acfd_data = {
                    'Year': YEAR,
                    'Plant_ID': plant_id,
                    'Time_Period': time_period_label,
                    'ACFD': metrics['acfd']
                }
                plot_acfd_data.append(acfd_data)

        OUTPUT_NAME = f'output/{YEAR}/ERCOT_plant_comparison_summary_{csv_suffix}.csv'
        result_df = pd.DataFrame(all_data).T
        result_df = result_df.reindex(sorted(result_df.columns), axis=1)
        result_df = result_df.sort_index()
        result_df = result_df.T
        print('number of columns: ', len(result_df.columns))
        result_df.to_csv(OUTPUT_NAME)
        print(f"Summary CSV saved to: {OUTPUT_NAME}")

    #Plot the results for all plants 
    plt.rcParams.update({
    'font.size': 16,          # General font size
    'axes.titlesize': 20,     # Title font size
    'axes.labelsize': 18,     # Axis label font size
    'xtick.labelsize': 16,    # X-axis tick font size
    'ytick.labelsize': 16,    # Y-axis tick font size
    'legend.fontsize': 16,    # Legend font size
    })

    cross_corr_data = result_df.loc['cross_correlation']
    plt.figure(figsize=(10, 6))
    bins = np.arange(0.62, 1.01, 0.01)

    plt.hist(cross_corr_data.values, bins=bins, alpha=0.7, edgecolor='black')
    plt.xlabel('Cross Correlation')
    plt.ylabel('Number of Plants')
    plt.title(f'Distribution of Yearly Cross Correlation Values for all {YEAR} ERCOT Plants Compared to PLUSWIND')
    plt.grid(True, alpha=0.3)

    mean_val = cross_corr_data.mean().round(2)
    median_val = cross_corr_data.median().round(2)
    plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
    plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'output/{YEAR}/ERCOT_cross_correlation_distribution.png')
    # plt.show()

    mae_pct_data = result_df.loc['mae_pct']
    plt.figure(figsize=(10, 6))
    bins = np.arange(0, 41, 1)

    plt.hist(mae_pct_data.values, bins=bins, alpha=0.7, edgecolor='black')
    plt.xlabel('MAE Percentage (%)')
    plt.ylabel('Number of Plants')
    plt.title(f'Distribution of Yearly MAE Percentage Values for all {YEAR} ERCOT Plants Compared to PLUSWIND')
    plt.grid(True, alpha=0.3)

    mean_val = mae_pct_data.mean()
    median_val = mae_pct_data.median()
    plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
    plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'output/{YEAR}/ERCOT_mae_pct_distribution.png')
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
    plt.savefig(f'output/{YEAR}/ERCOT_bias_pct_distribution.png')
    # plt.show()

    ovl_data = result_df.loc['ovl']
    plt.figure(figsize=(10, 6))
    bins = np.arange(0, 101, 2)

    plt.hist(ovl_data.values, bins=bins, alpha=0.7, edgecolor='black')
    plt.xlabel('OVL (%)')
    plt.ylabel('Number of Plants')
    plt.title(f'Distribution of Yearly OVL Values for all {YEAR} ERCOT Plants Compared to PLUSWIND')
    plt.grid(True, alpha=0.3)

    mean_val = ovl_data.mean()
    median_val = ovl_data.median()
    plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
    plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'output/{YEAR}/ERCOT_ovl_distribution.png')
    # plt.show()

    acfd_data = result_df.loc['acfd']
    plt.figure(figsize=(10, 6))
    bins = np.arange(-1.1, 1.1, 0.1)

    plt.hist(acfd_data.values, bins=bins, alpha=0.7, edgecolor='black')
    plt.xlabel('ACFD (%)')
    plt.ylabel('Number of Plants')
    plt.title(f'Distribution of Yearly ACFD Values for all {YEAR} ERCOT Plants Compared to PLUSWIND')
    plt.grid(True, alpha=0.3)

    mean_val = acfd_data.mean()
    median_val = acfd_data.median()
    plt.axvline(mean_val, color = 'orange', linestyle='--', label=f'Mean: {mean_val:.2f}')
    plt.axvline(median_val, color = 'red', linestyle='--', label=f'Median: {median_val:.2f}')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'output/{YEAR}/ERCOT_acfd_distribution.png')
    # plt.show()

plt.rcParams.update({
    'font.size': 16,          # General font size
    'axes.titlesize': 20,     # Title font size
    'axes.labelsize': 18,     # Axis label font size
    'xtick.labelsize': 16,    # X-axis tick font size
    'ytick.labelsize': 16,    # Y-axis tick font size
    'legend.fontsize': 16,    # Legend font size
})

df_ovl = pd.DataFrame(plot_ovl_data)
df_cc = pd.DataFrame(plot_cc_data)
df_acfd = pd.DataFrame(plot_acfd_data)

metrics_data = {
    'OVL': df_ovl,
    'Cross_Correlation': df_cc,
    'ACFD': df_acfd
}

time_periods = df_ovl['Time_Period'].unique()

for metric_name, df_metric in metrics_data.items():
    for time_period in time_periods:
        period_data = df_metric[df_metric['Time_Period'] == time_period]
        plt.figure(figsize=(10, 6))
        if metric_name == 'Cross_Correlation':
            metric_label = 'Cross Correlation'
        elif metric_name == 'OVL':
            metric_label = 'OVL (%)'
        elif metric_name == 'ACFD':
            metric_label = 'ACFD'

        sns.boxplot(data=period_data, x='Year', y=metric_name, palette='colorblind')
        # plt.title(f'{time_period} {metric_name} Distribution by Year')
        plt.xlabel('Year')
        plt.ylabel(metric_label)
        plt.grid(True, alpha=0.3)
        # plt.show()
        plt.savefig(f'output/ERCOT_{metric_name}_distribution_by_year_{time_period}_boxplot.png')

# Boxplot for Cross Correlation
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_cc, x='Year', y='Cross_Correlation', palette='colorblind')
# plt.title('Cross Correlation Distribution by Year')
plt.xlabel('Year')
plt.ylabel('Cross Correlation')
plt.grid(True, alpha=0.3)
# plt.show()
plt.savefig('output/ERCOT_CC_distribution_by_year_boxplot.png')

# Violin plot for Cross Correlation
plt.figure(figsize=(10, 6))
sns.violinplot(data=df_cc, x='Year', y='Cross_Correlation', palette='colorblind')
# plt.title('Cross Correlation Distribution by Year')
plt.xlabel('Year')
plt.ylabel('Cross Correlation')
plt.grid(True, alpha=0.3)
# plt.show()
plt.savefig('output/ERCOT_CC_distribution_by_year_violin.png')

# Boxplot for OVL 
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_ovl, x='Year', y='OVL', palette='colorblind')
# plt.title('OVL Distribution by Year')
plt.xlabel('Year')
plt.ylabel('OVL (%)')
plt.grid(True, alpha=0.3)
# plt.show()
plt.savefig('output/ERCOT_OVL_distribution_by_year_boxplot.png')

# Boxplot for ACFD
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_acfd, x='Year', y='ACFD', palette='colorblind')
# plt.title('ACFD Distribution by Year')
plt.xlabel('Year')
plt.ylabel('ACFD')
plt.grid(True, alpha=0.3)
# plt.show()
plt.savefig('output/ERCOT_ACFD_distribution_by_year_boxplot.png')

plot_all_metrics_data = []

for YEAR in YEARS:
    FOLDERS = f'output/{YEAR}/ERCOT_PLUSWIND_yearly_hsl'
    folders = [f for f in os.listdir(FOLDERS) 
                if os.path.isdir(os.path.join(FOLDERS, f))]
    
    for time_period in TIME_PERIODS:
        for plant in folders:
            plant_id = plant
            plant_path = os.path.join(FOLDERS, plant)
            
            if time_period == '':
                file_pattern = f'ERCOT {plant_id} {YEAR}_metrics_base_analysis_PLUSWIND_YE_average_15min.csv'
                time_period_label = 'Overall'
            else:
                file_pattern = f'ERCOT {plant_id} {YEAR}_metrics_base_analysis_PLUSWIND_YE_{time_period}_average_15min.csv'
                time_period_label = time_period.title()
            
            csv_files = glob.glob(os.path.join(plant_path, file_pattern))
            
            if csv_files: 
                df = pd.read_csv(csv_files[0])
                
                # Collect all metrics
                all_metrics_record = {
                    'Year': YEAR,
                    'Plant_ID': plant_id,
                    'Time_Period': time_period_label,
                    'RMSE': float(df['rmse'].iloc[0]),
                    'CRMSE': float(df['crmse'].iloc[0]),
                    'Bias_Pct': float(df['bias_pct'].iloc[0]),
                    'MAE_Pct': float(df['mae_pct'].iloc[0]),
                    'Cross_Correlation': float(df['cross_correlation'].iloc[0]),
                    'OVL': float(df['ovl'].iloc[0]),
                    'ACFD': float(df['acfd'].iloc[0])
                }
                plot_all_metrics_data.append(all_metrics_record)

df_all_metrics = pd.DataFrame(plot_all_metrics_data)
# Filter for only Day and Night
df_day_night = df_all_metrics[df_all_metrics['Time_Period'].isin(['Day', 'Night'])]


# Calculate averages by Year and Time_Period
metrics_list = ['RMSE', 'CRMSE', 'Bias_Pct', 'MAE_Pct', 'Cross_Correlation', 'OVL', 'ACFD']

avg_metrics = df_day_night.groupby(['Year', 'Time_Period'])[metrics_list].mean().reset_index()

# Create subplots for all metrics
fig, axes = plt.subplots(3, 3, figsize=(18, 15)) 
axes = axes.ravel()  

metrics_list = ['RMSE', 'CRMSE', 'Bias_Pct', 'MAE_Pct', 'Cross_Correlation', 'OVL', 'ACFD']
    
avg_metrics = df_day_night.groupby(['Year', 'Time_Period'])[metrics_list].mean().reset_index()
  # 2 colors for Day/Night
custom_colors = {'Day': 'goldenrod', 'Night': 'steelblue'}
# Create separate plot for each metric
for metric in metrics_list:
    plt.figure(figsize=(10, 6))
    
    sns.barplot(data=avg_metrics, x='Year', y=metric, hue='Time_Period', 
                palette=custom_colors)
    
    # plt.title(f'Average {metric} by Year (Day vs Night Comparison)')
    plt.xlabel('Year')
    plt.ylabel(f'Average {metric}')
    plt.legend(title='Time Period')
    plt.grid(True, alpha=0.3)
    # plt.show()
    plt.savefig(f'output/ERCOT_average_{metric}_by_year_day_night_comparison.png')

