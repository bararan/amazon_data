Instructions
*The scripts require Python3.6 or newer to run.
*There are two runner files provided. run_windows.bat (as the name implies) is for Windows; run.sh is for Mac and Linux.
*All the input files need to be stored under Files subfolder. The input files need to be comma-separated CSV files. Place all the input files in the Files subfolder before running the script.
*After placing the input files under Files double click the runner file that is suitable for your operating system to run the scripts and generate the output.
*A terminal/shell/command prompt window (one of these, depending on your operating system) will pop up when the scripts are running. Do not close this window, as doing so will terminate the script.
*In the terminal window that pops up a series of dialogues will appear, asking for used input:
    -First, the script will ask you to enter a value for conversion share cutoff. Enter this in terms of percentage points (that is, type 50 if you want to set the cutoff as fifty percent) and hit Enter to submit.
    -Then you will be presented with a list of files found in the Files folder, with a number to the left of each. You will then be asked to enter the number that corresponds to the first month's file. Find the file, type the number and hit Enter.
    -You will need to do the same for second and third month's files. Type in the numbers that belong to these files and hit Enter to submit each.
    -Finally, you will be given the option to provide an output filename. If you hit Enter without typing anything a filename will be automatically generated. The generated filename will follow the format 'FinalFile_<YEAR>-<MONTH>-<DAY>-<HOURS><MINUTES><SECONDS><AM or PM>.csv' where the time fields will be generated using the time at which the file is created. If you need to specift a filename you can type the name you desire and hit Enter to submit. 
*You are encouraged to let the filename be generated automatically as this will ensure that a new, unique filename will be used each time the script is run and prevent overwriting any previous files.
*The output file will be created in the root folder (i.e. the folder under which the runner files and this README are located). Please note that while the script is running the file will be there but it will continue to be written. While in most cases it should be OK to take a peek at the file while it's being written it's best practice to leave it to when the script completes to avoid corrupting the file.
*Some log lines will appear to inform you of the progress and print warnings wherever necessary (you do not need to do anything about the warnings, if you see any). 
*The script will be complete and the output file ready when you see a log line that reads 'INFO: DONE'

Troubleshooting:
*When I double click run.sh it does not seem to run the scripts.
    -You probably need to manually make the file executable. Open file properties, find the checkbox to allow the file to be executed as a program, check it and then try to run it again.
*I get an error that says python3 is not recognized as a command.
    -You likely need to edit the PATH variables of your operating system so that the directory under which python3 executable is located.
