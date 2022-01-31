*The scripts require Python3.6 or newer to run.
*There are two runner files provided. run.sh is for Mac and Linux, run_windows.bat (as the name implies) is for Windows.
*All the input files need to be stored under Files subfolder. The input files need to be comma-separated CSV files.
*Output will be saved in the root folder (i.e. the folder under which the runner files and this README are located).
*Under the Scripts subfolder there is a configuration file, named config.py. Open this file using any text editor to edit input file names and adjust the maximum conversion share threshold value. The file also allows for specifying an output file name, which when left blank will be generated automatically by the script. The comments in the file include instructions on how to make these changes.
*After placing the input files under Files and editing & saving the configuration file, double click the runner file that is suitable for your operating system to run the scripts and generate the output.
*A terminal/shell/command prompt window (one of these, depending on your operating system) will pop up when the scripts are running. Do not close this window, as doing so will terminate the script. Some log lines will appear to inform you of the progress and print warnings wherever necessary (you do not need to do anything about the warnings). The script will be complete and the output file ready when you see a log line that reads 'INFO: DONE'

Troubleshooting:
*When I double click run.sh it does not seem to run the scripts.
    -You probably need to manually make the file executable. Open file properties, find the checkbox to allow the file to be executed as a program, check it and then try to run it again.
*I get an error that says python3 is not recognized as a command.
    -You likely need to edit the PATH variables of your operating system so that the directory under which python3 executable is located.
