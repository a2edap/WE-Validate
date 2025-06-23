import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os 

# Escape special characters in LaTeX
# def escape_latex_special_characters(text):
#     if isinstance(text, str):
#         replacements = {
#             '&': r'\&',
#             '%': r'\%',
#             '$': r'\$',
#             '_': r'\_',
#             '{': r'\{',
#             '}': r'\}',
#             '#': r'\#',
#             '~': r'\textasciitilde{}',
#             '^': r'\textasciicircum{}',
#             '\\': r'\textbackslash{}',
#         }
#         for char, escape in replacements.items():
#             text = text.replace(char, escape)
#     return text

def add_df_to_latex(df, section):
    latex_section = f"\\section{{{section}}}\n\n"
    
    if len(df.columns) > 6:
        latex_section += "\\begin{adjustbox}{width=\\textwidth,center}\n"
    
    latex_section += df.to_latex(
        index=False,
        escape=False,
        # booktabs=True,
        caption=section
    )
    
    if len(df.columns) > 6:
        latex_section += "\\end{adjustbox}\n"
    
    latex_section += "\n\\newpage\n\n"
    
    return latex_section



