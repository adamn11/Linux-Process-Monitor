import subprocess


def process_validation():
    '''Checks if the process ID is valid
    
    Args:
        None

    Returns (Tuple):
        Returns the process name and PID number as a tuple

    Raises:
        None
    '''
    while True:
        try:
            pro_name = raw_input("Enter process name: ")
            pid_num = subprocess.check_output("pgrep %s" % pro_name,
                                              shell=True)
        except subprocess.CalledProcessError as e:
            print "Not a valid process"
            continue 
        else:
            return (pro_name, pid_num)

def refreshtime_validation():
    '''Validates that the Refresh Time stays within the bounds > 0
    
    Args:
        None

    Returns (float):
        Returns user input for refresh time in seconds

    Raises:
        None
    '''
    while True:
        try:
            runtime_input = float(raw_input("Enter Refresh Time (in seconds): "))
        except ValueError:
            print "\n**Please enter a valid number (Must be an integer).**\n"
            continue
        if runtime_input <= 0:
            print "\n**Please enter a valid number (Must be greater than 0).**\n"
            continue
        else:
            return runtime_input

def stop_point_validation():
    '''Validates that the Stop Point stays within the bounds > 0'
    
    Args:
        None

    Returns (int):
        Returns users input for stop point in seconds

    Raises:
        None
    '''
    while True:
        try:
            stop_point_input = int(raw_input("Choose how long to run the program for (in seconds). Type 0 for manual cancelation: "))
        except ValueError:
            print "\n**Please enter a valid number (Must be an integer).**\n"
            continue
        if stop_point_input < 0:
            print "\n**Please enter a valid number (Must be 0 or greater).**\n"
            continue
        else:
            return stop_point_input

def pid_input_validation(list):
    '''Validates that the user chooses a valid PID (Within the available PID)
    
    Args:
        None

    Returns (int):
        Returns user input for PID

    Raises:
        None
    '''
    while True:
        try:
            pid_input = int(raw_input("Select a PID to use: "))
        except ValueError:
            print "Please enter a valid input (Select a PID)."
            continue
        if str(pid_input) not in list:
            print "Please enter a valid input (Select a PID)."
            continue
        else:
            return pid_input

