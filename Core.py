from Process import Process
import version
import Validations as v
import Plot_data as plot

import sys
import os
import subprocess
import time
import imp
from datetime import datetime, timedelta


def create_folder():
    '''Creates a folder that stores the output files of the program
    
    Args:
        None

    Returns (String):
        Returns the absolute path for Output File folder
        Example: "/Document/Linux-Process-Monitor/Output_Files"

    Raises:
        None
    '''

    current_dir = os.path.dirname(os.path.realpath(__file__))
    new_folder = os.path.join(current_dir, 'Output_Files')

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    return new_folder

def show_eta(seconds_to_completion):
    '''If program is not infinite, then show the date and time of when the
    program will finish running.
    
    Args:
        seconds_to_completion (int): how many seconds the program will be
        running for

    Returns (String):
        Returns the time till completion

    Raises:
        None
    '''

    return datetime.now() + timedelta(seconds=seconds_to_completion)

def get_total_mem():
    '''Gets the total system RAM memory from /proc/meminfo. Only works on
    Linux machines

    Args:
        None

    Returns (String):
        Returns the total system RAM memory

    Raises:
        None
    
    '''
    meminfo_output = subprocess.Popen('awk \'/MemTotal/ {print $2}\' /proc/meminfo', shell=True, stdout=subprocess.PIPE, )
    return meminfo_output.stdout.read().strip()

def calculate_process_memory_usage(proc_usage, total_memory):
    '''Calculates memory in kb using process percentage and total memory of
    the system
    
    Args:
        proc_usage (String): Taken from top command used in linux. Process
            usage in percent
        total_memory (String): Taken from get_total_mem(). Total RAM mem

    Returns (Int):
        Returns process memory usage in kbs

    Raises:
        ValueError: If the application closes, then close the program
    '''
    try:
        if "\n" not in proc_usage:
            return round((((float(proc_usage) / 100) * int(total_memory))), 2)
    except ValueError as e:
        print 'Application has been closed'
        print repr(e)
        sys.exit(1)

def mem_monitor(process):
    '''Reads data from top command and records in text file
    
    Args:
        process (Process class): Uses data from Process class for monitoring 

    Returns:
        None

    Raises:
        KeyboardInterrupt: Ends monitoring process when Ctrl+C is pressed by
            the user
        IOError: Closes the program if output file does not exist, for some
            reason
    '''
    abs_path = create_folder()
    full_name = "%s/%s.txt" % (abs_path, process.get_file_name())
    total_mem = get_total_mem()

    print "\n%s PID: %s" % (process.process_name, process.pid_num)
    print "Total Memory: %s kB" % total_mem
    if process.stop_point == 0:
        print "Program will run indefinitely until manual cancelation (Ctrl + C)" 
    else:    
        print "Program will finish at %s." % show_eta(int(process.stop_point))
    print "Recording process...Press Ctrl+C at any time to stop monitoring."

    with open(full_name, "w") as txt_file:
        counter = 0
        txt_file.write("Date        Time       MEM         Total        Percentage\n")

        try:
            while process.stop_point == 0:
                start = time.time()
                top_output = subprocess.Popen('top -b -n 1 | grep %s | awk \'{print $%s}\'' % (process.pid_num, '10'), shell=True, stdout=subprocess.PIPE, )
                mem_percent_output = top_output.stdout.read().strip()
                current_time = time.strftime("%H:%M:%S")
                current_date = datetime.now() 
                fmt_current_date = "%s/%s/%s" % (current_date.month, current_date.day, current_date.year)
                
                txt_file.write("{} | {} | {} / {} kB | {} %\n".format(fmt_current_date, current_time, calculate_process_memory_usage(mem_percent_output, total_mem), total_mem, mem_percent_output))
                txt_file.flush()

                counter += float(process.refresh_time)
                time.sleep(float(process.refresh_time) - (time.time() - start))
        except KeyboardInterrupt:
            pass
        except IOError:
            print "The file does not exist"
            sys.exit(1)
    txt_file.close()

def unix_to_windows(file_name):
    '''Converts unix text file to be readable on window machines
    
    Args:
        file_name (String): Gets the process name and start time from Process
            class.
            Example: file_name = "Firefox 02/13/19 3:36"

    Returns:
        None

    Raises:
        None
    '''
    print "Creating text file suitable for window machines..."
    output_folder_dir = create_folder()
    unix_text = format_string_to_unix(file_name)
    subprocess.Popen('''awk 'sub("$", "\\r")' {0}/{1}.txt > {0}/windowstxt.txt'''.format(output_folder_dir, unix_text), shell=True)
    time.sleep(1)

def format_string_to_unix(file_name):
    '''Converts string to be readable in unix
    
    Args:
        file_name (String): Gets the process name and start time from Process
            class.
            Example: file_name = "Firefox 02/13/19 3:36"
    
    Returns:
        file_name (string): Returns the converted file_name that is suitable
            for windows"
    
    Raises:
        None
    '''
    count = 0

    for x in file_name:
        if x == " " or x == "(" or x == ")" or x == ":":
            file_name = file_name[:count] + "\\" + file_name[count:]
            count += 1
        count += 1

    return file_name

def confirmation_page(process):
    '''Displays all the information to user before recording memory
    
    Args:
        process (Process class): Uses data from Process class

    Returns:
        None

    Raises:
        None
    '''
    print "\nPlease confirm that the information is correct before continuing:"
    print "Process Name: %s" % process.process_name
    print "PID: %s" % process.pid_num
    print "Refresh Time: %s seconds" % process.refresh_time
    if process.stop_point == 0:
        print "Stop Point: Infinite (Manual Cancelation)"
    else:
        print "Stop Point: %d seconds" % process.stop_point

    while True:
        user_continue = raw_input("Continue (Y/N)?: ")
        if user_continue.lower() == 'n':
            sys.exit(1)
        elif user_continue.lower() == 'y':
            break
        else:
            print "\n**Please enter a valid response**\n"
            continue

def end_message(execution_time):
    '''Displays where the output files are saved at the end of the program
    
    Args:
        execution_time (time): How long the process monitor was running for.

    Returns:
        None

    Raises:
        None
    '''
    print "\nTotal runtime: %s" % time.strftime("%H hr, %M min, %S sec",
                                                time.gmtime(execution_time))
    print "Program has finished executing. Files are located at %s\n" % create_folder()

def check_number_of_processes(pid_list):
    '''Lets users choose the process to record if the process has more than
    one ID
    
    Args:
        pid_list (list of string): A string of PIDs (assuming there are
            multiple IDs)
            Example: "283 274 18237 295817 4958". Want to convert this into a
                list so the user can choose which PID to use.

    Returns:
        (1) pid_input: Returns PID that user has selected to use
        (2) pid_list[0]: Return 0th index if there is only one process

    Raises:
        None
    '''
    if len(pid_list) > 1:
        for x in pid_list:
            print x
        pid_input = v.pid_input_validation(pid_list)
        return pid_input
    else: 
        return pid_list[0]

def convert_pid_to_list(pid):
    '''Converts the process string into a list
    
    Args:
        pid (string): A string of pids (assuming there are multiple IDs)

    Returns:
        pid_list (list of strings): Returns a list of PIDs (assuming there are
            multiple IDs)

    Raises:
        None
    '''
    pid_str = ""
    pid_list = []

    for x in pid:
        if x == "\n":
            pid_list.append(pid_str)
            pid_str = ""
            continue
        pid_str += x

    return pid_list

def get_process_info():
    '''Gets process information from user and initializes Process class
    
    Args:
        None

    Returns:
        process (process class): returns initialized process class

    Raises:
        None
    '''
    pro_name = v.process_validation()
    pid_output = pro_name[1]
    pid_list = convert_pid_to_list(pid_output)
    pid_num = check_number_of_processes(pid_list)

    process_name = pro_name[0].strip()
    refresh_time = v.refreshtime_validation()
    stop_point = v.stop_point_validation()

    process = Process(process_name, refresh_time, stop_point,
                      pid_num, time.strftime("%m-%d-%Y %H:%M"))

    return process

def get_dependencies():
    ''' Get a list of dependencies.txt that will be used in
    check_modules_exist()
    
    Args:
        None

    Returns:
        dep (list of string): Returns a list of dependencies from
            dependencies.txt

    Raises:
        None
    '''
    dep = []
    with open("dependencies.txt", "r") as txt:
        for lines in txt:
            dep.append(lines.partition(" ")[0])

    return dep

def check_modules_exist():
    '''Check if modules are installed. If not then plotting will not be done
    
    Args:
        None

    Returns:
        True: if modules are installed
        False: if modules are NOT installed

    Raises:
        None
    '''
    list_mods = get_dependencies()

    for mods in list_mods:
        try:
            imp.find_module(mods)
        except ImportError as e:
            print e
            print "Plotting will not execute since there are missing modules"
            return False
    return True


if __name__ == "__main__":
    '''Main function'''

    print "Process Monitor: %s" % version.__version__ 
    process = get_process_info()
    confirmation_page(process)

    start = time.time()
    mem_monitor(process)
    unix_to_windows(process.get_file_name())
    execution_time = time.time() - start - 1

    if check_modules_exist():
        plot.convert_to_excel(process.get_file_name(), create_folder())
        plot.plot_data(process, execution_time, create_folder())

    end_message(execution_time)

