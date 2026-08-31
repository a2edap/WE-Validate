import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
import numpy as np

def add_df_to_latex(df, section, aggregation):    
    df_latex = df.copy()

    numeric_columns = df_latex.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        df_latex[col] = df_latex[col].apply(lambda x: f"{x:.{2}f}")

    if pd.api.types.is_datetime64_any_dtype(df_latex.index):
        if aggregation == 'MS'or aggregation == 'MS_day' or aggregation == 'MS_night':
            date_format = '%b %Y'
        elif aggregation == 'YE' or aggregation == 'YE_day' or aggregation == 'YE_night':
            date_format = '%Y'
        elif aggregation == 'D':
            date_format = '%m/%d/%Y'
        elif aggregation == 'H':
            date_format = '%Y-%m-%d %H:%M'
        else: 
            date_format = '%m/%d/%Y'  

        df_latex.index = df_latex.index.strftime(date_format)

    df_latex.columns = [col.replace('_', '\\_') for col in df_latex.columns]
    for col in df_latex.columns:
        if df_latex[col].dtype == 'object':
            df_latex[col] = df_latex[col].astype(str).str.replace('_', '\\_', regex=False)

    if df_latex.index.dtype == 'object':
        df_latex.index = df_latex.index.astype(str).str.replace('_', '\\_', regex=False)

    escaped_section = section.replace('_', '\\_')
    latex_section = ""
    # Use smaller font for wide tables
    if len(df.columns) > 6:
        latex_section += "\\footnotesize\n"
    
    latex_table = df_latex.to_latex(
        index=True,
        escape=False,
        longtable=True, 
        caption=escaped_section, 
        column_format='l' + 'c' * len(df_latex.columns)
    )
    
    latex_section += latex_table
    
    return latex_section

def generate_pdf_report(latex_tables, output_path, conf, title="WE-Validate Summary", plot_files = None):

    org = conf['output']['org']
    thresh = conf.get('threshold', 0.1)  # Default threshold if not specified
    select_method = conf['reference']['select_method']
    if any('swingdoor' in i for i in conf['analysis']):
        filename = f"{org}_report_{select_method}_{thresh:.2f}"
    else:
        filename = f"{org}_report_{select_method}"

     # Create plots section if plots are provided
    plots_latex = ""
    if plot_files:
        plots_latex = r"""
    \section*{Plots}
    """
        for i, plot_file in enumerate(plot_files):
            if plot_file and os.path.exists(plot_file):
                # Get relative path for LaTeX
                plot_name = os.path.basename(plot_file)
                plot_title = plot_name.replace('_', ' ').replace('.png', '')
                # plot_title = ' '.join(word.capitalize() for word in plot_title.split())

                width = 0.95 if 'Timeseries_Monthly' in plot_name else 0.8

                plots_latex += rf"""
    \begin{{figure}}[!htbp]
        \centering
        \includegraphics[width={width}\textwidth]{{{plot_name}}}
        \caption{{{plot_title}}}
    \end{{figure}}
    """
    org_title = org.replace('_', ' ')
    plant_capacity = conf['capacity']
    # Create LaTeX document
    final_latex = rf"""
    \documentclass[11pt]{{article}}
    \usepackage[utf8]{{inputenc}}
    \usepackage{{booktabs}}
    \usepackage{{longtable}}
    \usepackage{{geometry}}
    \usepackage{{adjustbox}}
    \usepackage{{array}}
    \usepackage{{float}}
    \usepackage{{graphicx}}
    \geometry{{margin=1in}}
    \floatplacement{{table}}{{H}}
    \begin{{document}}
    \begin{{center}}
    \Large \textbf{{{org_title + ' ' + '(' + str(plant_capacity) + ' ' +  'MW)' + ' ' + title}}}
    \end{{center}}
        """ + "".join(latex_tables) + plots_latex + r"""
    \end{document}"""

    tex_filepath = os.path.join(output_path, f'{filename}.tex')
    try:
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(final_latex)
    except Exception as e:
        print(f"Error writing LaTeX file: {e}")
        return False
    
    # Compile to PDF
    original_dir = os.getcwd()
    try:
        os.chdir(output_path)
    
        for i in range(2):
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', f'{filename}.tex'], 
                                  capture_output=True, text=True)
        
    except FileNotFoundError:
        print("pdflatex not found. Please install LaTeX distribution.")
        return False
    except Exception as e:
        print(f"Error during PDF compilation: {e}")
        return False
    finally:
        os.chdir(original_dir)
    
    # Clean up auxiliary files
    for ext in ['.aux', '.log', '.out', '.toc', ]:
        aux_file = os.path.join(output_path, f'{filename}{ext}')
        if os.path.exists(aux_file):
            os.remove(aux_file)

    
def create_ramping_tables(swingdoor_ts, df, conf, max_freq_str, c, start_time=None, end_time=None):

    filtered_df = df.copy()
    filtered_swingdoor_ts = {}

    if start_time is not None or end_time is not None:
        if start_time is not None and end_time is not None:
            mask = (filtered_df.index >= start_time) & (filtered_df.index <= end_time)
            filtered_df_ramp = df.loc[mask]
        elif start_time is not None:
            filtered_df_ramp = df.loc[filtered_df.index >= start_time]
        elif end_time is not None:
            filtered_df_ramp = filtered_df.loc[filtered_df.index <= end_time]
        
        for key, df in swingdoor_ts.items():
            if start_time is not None and end_time is not None:
                mask = (df.index >= start_time) & (df.index <= end_time)
                filtered_swingdoor_ts[key] = df.loc[mask]
            elif start_time is not None:
                filtered_swingdoor_ts[key] = df.loc[df.index >= start_time]
            elif end_time is not None:
                filtered_swingdoor_ts[key] = df.loc[df.index <= end_time]
    else:
        filtered_swingdoor_ts = swingdoor_ts.copy()
    
    time_stamps = list(filtered_df_ramp.index)
    total_rows = len(time_stamps)
    if total_rows == 0:
        return "% No data found for the specified time range\n"
    
    inc_dec_c = filtered_df_ramp.iloc[:, 1].diff().fillna(0)
    inc_dec_b = filtered_df_ramp.iloc[:, 0].diff().fillna(0)

    time_range_info = ""
    if start_time or end_time:
        time_range_info = f" (Time Range: {start_time or 'Start'} to {end_time or 'End'})"

    data_rows = []
    for i, timestamp in enumerate(time_stamps):
  
        inc_dec_c_string = f"{inc_dec_c.iloc[i]:.2f}"

        if 'swingdoor-ramp' in filtered_swingdoor_ts and i < len(filtered_swingdoor_ts['swingdoor-ramp']):
            ramp_rate_c = f"{filtered_swingdoor_ts['swingdoor-ramp'].loc[timestamp, c['name']]:.2f}"
            
        else:
            ramp_rate_c = "N/A"
        if 'swingdoor-dur' in filtered_swingdoor_ts and i < len(filtered_swingdoor_ts['swingdoor-dur']):
            ramp_dur_c = f"{filtered_swingdoor_ts['swingdoor-dur'].loc[timestamp, c['name']]:.2f}"
        else:
            ramp_dur_c = "N/A"

        inc_dec_b_string = f"{inc_dec_b.iloc[i]:.2f}"
        if 'swingdoor-ramp' in filtered_swingdoor_ts and i < len(filtered_swingdoor_ts['swingdoor-ramp']):
            ramp_rate_b = f"{filtered_swingdoor_ts['swingdoor-ramp'].loc[timestamp, conf['base']['name']]:.2f}"
        else:
            ramp_rate_b = "N/A"
        if 'swingdoor-dur' in filtered_swingdoor_ts and i < len(filtered_swingdoor_ts['swingdoor-dur']):
            ramp_dur_b = f"{filtered_swingdoor_ts['swingdoor-dur'].loc[timestamp, conf['base']['name']]:.2f}"
        else:
            ramp_dur_b = "N/A"

        base_name = conf['base']['name']
        base_name_clean = base_name.replace('_', ' ')
        c_name = c['name']
        units = conf['reference']['units']
        data_rows.append({
        'Time Stamp': timestamp,
        f'Inc/dec ({units}) {c_name}': inc_dec_c_string,
        f'Ramp rate ({units}/{max_freq_str}) {c_name}': ramp_rate_c,
        f'Ramp dur ({max_freq_str}) {c_name} ': ramp_dur_c,
        f'Inc/dec ({units}) {base_name_clean}': inc_dec_b_string,
        f'Ramp rate ({units}/{max_freq_str}) {base_name_clean}': ramp_rate_b,
        f'Ramp dur ({max_freq_str}) {base_name_clean}': ramp_dur_b
        })

        df_ramp = pd.DataFrame(data_rows)
        df_ramp.set_index('Time Stamp', inplace=True)

        latex_code = df_ramp.to_latex(
        index=True,
        escape=False,
        longtable=True,
        caption=f'Ramping Analysis Comparison{time_range_info}',
        label='tab:ramping_analysis_long',
        column_format='p{2.2cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}'
        )


    
    return latex_code
        

def save_ramping_to_pdf(latex_tables, output_path, conf, title="WE-Validate Ramping Analysis"):

    org = conf['output']['org']
    thresh = conf.get('threshold', 0.1)
    select_method = conf['reference']['select_method']
    filename = f"{org}_ramping_analysis_{select_method}_{thresh:.2f}"

    org_title = org.replace('_', ' ')
    # Create LaTeX document
    final_latex = rf"""
    \documentclass[11pt]{{article}}
    \usepackage[utf8]{{inputenc}}
    \usepackage{{booktabs}}
    \usepackage{{longtable}}
    \usepackage{{geometry}}
    \usepackage{{adjustbox}}
    \usepackage{{array}}
    \usepackage{{float}}
    \usepackage{{graphicx}}
    \geometry{{margin=1in}}
    \floatplacement{{table}}{{H}}
    \begin{{document}}
    \begin{{center}}
    \Large \textbf{{{org_title + ' ' + title}}}
    \end{{center}}
        """ + "".join(latex_tables) + r"""
    \end{document}"""

    tex_filepath = os.path.join(output_path, f'{filename}.tex')
    try:
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(final_latex)
    except Exception as e:
        print(f"Error writing LaTeX file: {e}")
        return False
    
    original_dir = os.getcwd()
    try:
        os.chdir(output_path)
    
        for i in range(2):
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', f'{filename}.tex'], 
                                  capture_output=True, text=True)
        
    except FileNotFoundError:
        print("pdflatex not found. Please install LaTeX distribution.")
        return False
    except Exception as e:
        print(f"Error during PDF compilation: {e}")
        return False
    finally:
        os.chdir(original_dir)

        # Clean up auxiliary files
    for ext in ['.aux', '.log', '.out', '.toc', ]:
        aux_file = os.path.join(output_path, f'{filename}{ext}')
        if os.path.exists(aux_file):
            os.remove(aux_file)


        

