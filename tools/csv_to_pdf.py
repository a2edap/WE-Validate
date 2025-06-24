import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
import numpy as np

def add_df_to_latex(df, section, aggregation):    
    # Create a copy for escaping
    df_latex = df.copy()

    #Round numerical data to 2 decimal places 
    numeric_columns = df_latex.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        df_latex[col] = df_latex[col].apply(lambda x: f"{x:.{2}f}")

    if pd.api.types.is_datetime64_any_dtype(df_latex.index):
        if aggregation == 'MS':
            date_format = '%b %Y'
        elif aggregation == 'D':
            date_format = '%m/%d/%Y'
        elif aggregation == 'H':
            date_format = '%Y-%m-%d %H:%M'
        else: 
            date_format = '%m/%d/%Y'  

        df_latex.index = df_latex.index.strftime(date_format)

    # Escape underscores
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

def generate_pdf_report(latex_tables, output_path, conf, title="WE-Validate Summary"):

    org = conf['output']['org']
    select_method = conf['reference']['select_method']
    filename = f"{org}_report_{select_method}"
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
    \geometry{{margin=1in}}
    \floatplacement{{table}}{{H}}
    \begin{{document}}
    \begin{{center}}
    \Large \textbf{{{conf['output']['org']+ ' ' + title}}}
    \end{{center}}
    """ + "".join(latex_tables) + r"""
    \end{document}"""
        
    # Write LaTeX file
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
        
        # Run pdflatex twice
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
    for ext in ['.aux', '.log', '.out', '.toc', '.tex']:
        aux_file = os.path.join(output_path, f'{filename}{ext}')
        if os.path.exists(aux_file):
            os.remove(aux_file)