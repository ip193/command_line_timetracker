# command_line_timetracker
Command Line program to record and visualize time spent on projects. Create invoices and work overviews easily for multiple clients or projects and visualize the data using **matplotlib**. Written in Python.

### Features

#### Time Tracking
- Track starting and ending times for work sessions (timestamps and minute count)
- Easily take breaks or add/subtract minutes from the session if you forgot to turn it on
- All data is stored in a .csv file for easy access, output of all session data to the command line also supported
- Easily define a new client/project to track time in multiple separate areas (e.g. one client for work, one to track time spent on schoolwork)
- Set an hourly billing on a client level to track earnings for time worked
- Associate sessions with zero or more labels (e.g. "Programming") and subprojects (e.g. "Bug Nr. 208"), as well as a description of what was done

#### Data Visualization and Summary
- Visualize total time spent on a client/project, label or subproject using **matplotlib** (e.g. how much time did I spend doing math homework this last month?)
- Chart labeling in German or English
- Generate billings reports on the command line to quickly see total billings, split by client/project, labels, and subprojects
- Generate a forecast (to next full month) of total and client-specific earnings, broken down by subproject and label
- In the case of multiple labels/subprojects per session, time spent is split up evenly between labels/subprojects when generating reports or charts

### Installation
1. Make sure you have Python installed on your system (and that the environment variable is added to your PATH variable [as described here](https://geek-university.com/python/add-python-to-the-windows-path/))
2. Download this repository as a ZIP file (or clone the repository) and unpack it a directory
![Alt text](readme/download_zip.png?raw=true "Download as ZIP")
3. If you are using Windows and want to be able to use this utility from anywhere (not just the install directory), make sure you have [enabled execution of Powershell scripts](https://superuser.com/questions/106360/how-to-enable-execution-of-powershell-scripts)
    - Using a text editor, open **writebillings.ps1** and **drawbillings.ps1** in your install directory and replace the value in quotes with a complete path to your newly downloaded files writebillings.py and drawbillings.py, respectively
    - Add the install directory to your PATH variable ([as described here](https://stackoverflow.com/questions/44272416/how-to-add-a-folder-to-path-environment-variable-in-windows-10-with-screensho))
4. If you are not using Windows, replace "\<filename\>.ps1" with "python ./\<filename\>.py" in the below terminal commands, which will only work within the install directory. Future work on this project will include a bash script analogous to the included Powershell scripts (which merely pass the arguments to python)

### Usage
1. To begin using the program, open **billingsconstants.py** and replace the path at the top of the page with the path to your installation directory. Follow the instructions at the bottom of the file to add a new project. 
2. Open a Powershell Window and type **writebillings.ps1 NEW -n YourNameHere**, replacing YourNameHere with the new client name. This will initialize the .csv file in which your sessions will be stored 
3. Type **writebillings.ps1 -h** to see the help menu
4. General usage is of the form 

#### Example usage

>1. writebillings.ps1 start -l "Programming,Studying" -p Docker -d "Began working through Docker tutorial" -n Homework
>2. writebillings.ps1 reset -m 12
>3. writebillings.ps1 end  
>4. drawbillings.ps1

Start a session in which you spent your time *Programming* and *Studying* on the topic of *Docker*. Here, "Homework" is the name of the client that was created in step 1 of the previous section. Because you forgot to start tracking your time until 12 minutes in, you add 12 minutes to the beginning of the timer. Because you eventually switched to learning about React at the end of the session, you add *React* to the topics you spent time on. 

At the end of the session, show some graphics to see how you have spent your time since you started tracking time. Get an estimate for the billing at the end of the month for this client (this isn't relevant for homework, but if you were tracking your time as a freelancer, you would get an estimate for your earnings this month (over 31 days)).  


