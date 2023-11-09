# WE-Validate

This infrastructure code enables comparison of time series from arbitrary data sources using user-defined metrics. The tool is designed to be simple, modulized, and extensible. We call our tool WE-Validate to gear towards forecast validation using observations and simulations for wind energy (“WE”) applications. 

The default branch is `main`, and active development is under `dev`. Pull requests from `dev` to `main` will be done regularly.

## Installation

### Clone this repo

For Mac users, in Terminal, `cd` to a destinated directory, then

`$ git clone https://github.com/joejoeyjoseph/WE-Validate.git`

For Windows users, [Git for Windows](https://gitforwindows.org/) or running Linux Bash Shell on Windows is an option. 

Alternatively, you can also use GitHub clients like [GitHub Desktop](https://desktop.github.com/) to clone this repo to your local machine.

### Install Python

This tool is built on Python 3.8. If you do not have Python on your machine, you can install [Python](https://www.python.org/) directly, or you can use package management software like [Anaconda](https://www.anaconda.com/). You can use this tool with your "root" Python, or you can use package and environment management systems like virtual environment or conda environment. Then in Terminal, 

`$ pip install -r requirements.txt`

This would download and install all the Python packages you need for this tool. 

If `pip` is not installed on your machine, you can visit the [pip website](https://pip.pypa.io/en/stable/installing/).

## Configuration

We use the YAML format for configuration file. An example configuration is provided in `config/config.yaml`. Explanations are embedded in `config.yaml`, in which the comments started with `#`.

In `config.yaml`, first, you need to specify the `location` (assumed to be the WGS84 latitude, `lat`, and longitude, `lon`, coordinates) as well as the evaluation duration in `time` (the `start` and `end` times).

To do a comparison, you will need at least one baseline dataset (called `base`) and one or more datasets to make comparisons to (called `comp`). For each dataset, you need to declare the data directory (`path`), data parser (`function`), and variable of interest (`var`). The `function` string must match one of the classes in the `inputs` folder.

If the nature of the variable of interest is wind speed (`ws`), you can choose a wind turbine power curve, specify its data directory (`path`), power curve file (`file`), and data parser (`function`), and the tool will compute metrics based on derived wind power.

Evaluation at different height levels above ground level is available, as long as the height levels exist in the baseline and comparison datasets.

Beyond the datasets, you can list which metrics to compute. Each must correspond to a metric class in the `metrics` folder. You can also specify the variable names (`var`) and units (`units`) to be displayed in the plots. 

Currently, only local datasets are supported. Future versions will fetch data over SFTP (i.e., PNNL DAP) and other protocols.

## Use this code

The main routine in this repo is the `compare` function in `ivalidate.py`. By calling `ivalidate.compare()`, it would run the default configuration listed in `config.yaml`. Users can choose a different YAML file for specific data and cases as well. For example, by calling `ivalidate.compare('config_test.yaml')`, it would use the configuration in `config_test.yaml`, which contains erroneous datasets for testing purposes.

Please refer to `/notebooks/demo_notebook.ipynb`, in which we summarize some example cases in the demo Jupyter Notebook.

## Community contribution

We encourage and welcome contribution from the wind energy community to this tool.

### Adding metrics

To add a new metric, create a new file in the `metrics` folder. The file name must match the class name. For example, if you wanted to write a script that computes mean absolute error, or MAE, you would label the file `mae.py` and the class inside would also be called `mae`.

The metric class interface is simple, it defines a single method called `compute` which takes two variables `x` (baseline) and `y` (comparison). Both are datetime-indexed pandas series.

The function `compute()` must return a float (single, scalar number).

Unit tests for the metrics are included in `test_metrics.py`. Travis CI should handle the software testing via `pytest`.

### Adding data inputs

To add a new data format (or source), create a new file in the `inputs` folder. As with metrics, the file name must match the class name. The naming convention is `{data name}_{data format}.py`. For example, if you wanted to parse an HDF5 file with LiDAR data, you might call it `lidar_hdf5.py` and the class name in the file would also be `lidar_hdf5`.

The input class interface expects a constructor that takes the path and variable and a single method called `get_ts()` which returns the time series as a datetime-indexed pandas dataframe.

### Adding preprocessors

To add a new preprocessor or quality control routine that operates on each time series, please visit the `qc` folder.

### Parallelism

The current implementation is serial, however future versions may exploit local or distributed parallelism by:

  * Loading time series data from files (or cache) in parallel
  * Computing metrics for each pair of time series in parallel

## Contributors

The [original version](https://github.com/somerandomsequence/nwtc-ivalidate) of the code was first developed by Caleb Phillips in 2016. Joseph Lee built onto Phillips's code and [implemented further development](https://github.com/joejoeyjoseph/nwtc-ivalidate) until 2022. Malcolm Moncheur and Heng Wang built onto Lee's code and developed the GUI.

# WE-Validate GUI

This is the GUI for the WE-Validate written in Python 3. 

## Requirements
To run this application, Python 3 and pip is required. The following installation instruction is for Windows only.

## Installation Instructions

To make it easy for you to get started with WE-Validate GUI, here's a list of recommended next steps.

1, git clone https://github.com/a2edap/WE-Validate.git \
2, python -m pip install virtualenv (optional, if you want to run the app in virtual environment and does not have virtualenv installed) \
3, python -m venv env (optional, setting up the virtual environment called env) \
4, source env/Scripts/activate (optional, starting the virtual environment) \
5, pip install -r requirements.txt \
6, python wevalidate_gui.py \
7, copy and paste the serve address (http://127.0.0.1:8088/ or localhost:8088) into web browser \
8, Crtl + c to stop server \
9, deactivate (optional, once done, deactivate the virtual environment) 

## Configuration

If a configuration yaml file already exists, drag and drop or select it.
If no config file exists, user can fill out the form and click the Run WeValidate button below.

## Input Parameters

The follow table describes the GUI's various input parameters:

| Input                        | Description                                                                                                                                                                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Time Window                  | Defines the start and end times of the validation period. Must be input in the following format: MM/DD/YYYY HH:MM:SS                                                                                                                                     |
| Metrics                      | Selects validation metrics. Any combination of the following metrics can be selected: Centered Root Mean Squared Error (CRMSE), Bias, Percent Bias, Mean Average Error (MAE), Percent MAE, Cross-correlation. Selecting at least one metric is required. |
| Output Directory             | Output directory path                                                                                                                                                                                                                                   |
| Name of the Run              | Simulation name. It is appended to the end of all saved files                                                                                                                                                                                           |
| Variable Name                | Validation variable name to be displayed on figures. The csv column header of the data being validated must match the ‘Variable Name’ input field (e.g. if the column header is ‘power’, then the ‘Variable Name’ should be ‘power’)                    |
| Variable Unit                | Validation variable units to be displayed on figures                                                                                                                                                                                                   |
| Name                         | Dataset name. Displays on figures and output files                                                                                                                                                                                                       |
| Data Path                    | Defines the path to the file. Must be an absolute file path                                                                                                                                                                                                                             |
| Variable Name                | Column header for the variable of interest in input csv file                                                                                                                                                                                             |
| Frequency                    | Validation variable frequency, in minutes                                                                                                                                                                                                                |


## Results
The  GUI provides the user graphical outputs of time series, histograms of the power, a scatterplot of correlation between time series, and plots that display each user-defined metric on a monthly basis, illustrating the temporal dependence of the relationship between the baseline and comparison data. The GUI supports zooming into specific time intervals to visually compare the baseline and comparison data sets.
WE-Validate also generates tabular data containing the seven user-defined metrics in the form of individual csv files, calculated on an hourly, daily, weekly, monthly, and annual basis.

