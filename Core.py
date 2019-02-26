from Process import Process
import version
import Validations as Val
import Plot_data as Plot
import Monitoring as Mon

import sys
import os
import subprocess
import time
import imp
import logging


def create_folder(folder_name):
    ''' Creates a folder within the root directory '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_dir, folder_name)

    if os.path.exists(path) is False:
        os.makedirs(path)
        logging.info('%s folder has been created' % folder_name)
    else:
        logging.error('%s folder already exists' % folder_name)
        print "Folder already exists"

    return path


def create_subfolder(parent_folder, subfolder):
    ''' Creates a subfolder within the parent folder '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_dir, parent_folder, subfolder)

    if os.path.exists(path) is False:
        os.makedirs(path)
        logging.info('%s folder has been created' % subfolder)
    else:
        logging.error('%s folder already exists' % subfolder)
        print "Subfolder already exists"


def get_directory(folder_name, parent_folder = None):
    ''' Returns the directory path of folder '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    if parent_folder is not None:
        current_dir = os.path.join(current_dir, parent_folder)

    for folders in os.listdir(current_dir):
        if folders == folder_name:
            return os.path.join(current_dir, folders)
        
    return False


def confirmation_page(proc):
    '''Displays all the information to user before recording memory'''
    print "\nPlease confirm that the information is correct before continuing:"
    print "Process Name: %s" % proc.get_process_name()
    print "PID: %s" % proc.get_pid_num()
    print "Refresh Time: %s seconds" % proc.get_refresh_time()
    if proc.get_stop_point() == 0:
        print "Stop Point: Infinite (Manual Cancellation)"
    else:
        print "Stop Point: %d seconds" % proc.get_stop_point()

    while True:
        user_continue = raw_input("Continue (Y/N)?: ")
        if user_continue.lower() == 'n':
            sys.exit(1)
        elif user_continue.lower() == 'y':
            break
        else:
            print "\n**Please enter a valid response**\n"
            continue

    logging.info('Process Name: %s' % proc.get_process_name())
    logging.info('PID: %s' % proc.get_pid_num())
    logging.info('Refresh Time: %s' % proc.get_refresh_time())
    if proc.get_stop_point() == 0:
        logging.info('Stop Point: Infinite')
    else:
        logging.info('Stop Point: %s' % proc.get_stop_point())


def check_number_of_processes(pid_list):
    '''Lets users choose the process to record if the process has more than
    one ID'''
    logging.info('Number of processes found: %s' % len(pid_list))

    if len(pid_list) > 1:
        for x in pid_list:
            print x
        pid_input = Val.pid_input_validation(pid_list)
        return pid_input
    else: 
        return pid_list[0]


def convert_pid_to_list(pid):
    '''Converts the process string into a list'''
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
    '''Gets process information from user and initializes Process class'''
    pro_name = Val.process_validation()
    pid_output = pro_name[1]
    pid_list = convert_pid_to_list(pid_output)
    pid_num = check_number_of_processes(pid_list)

    process_name = pro_name[0].strip()
    refresh_time = Val.refreshtime_validation()
    stop_point = Val.stop_point_validation()

    process = Process(process_name, refresh_time, stop_point,
                      pid_num, time.strftime("%m-%d-%Y %H:%M"))

    return process


def get_dependencies():
    ''' Get a list of dependencies that will be used in check_modules_
    exist()'''
    dep = []
    with open("dependencies.txt", "r") as txt:
        for lines in txt:
            dep.append(lines.partition(" ")[0])

    return dep


def check_modules_exist():
    '''Check if modules are installed. If not then plotting will not be done'''
    list_mods = get_dependencies()

    for mods in list_mods:
        try:
            imp.find_module(mods)
        except ImportError as e:
            print e
            logging.error('%s' % e)
            print "Plotting will not execute since there are missing modules"
            logging.error('Plotting will not execute since there are missing '
                          'modules')
            return False
    return True


def unix_to_windows(file_name, process_folder):
    '''Converts unix text file to be readable on window machines'''
    print "\nCreating text file suitable for window machines..."
    logging.info('A windows compatible text file has been created')
    
    unix_text = format_string_to_unix(file_name)
    unix_process_folder = format_string_to_unix(process_folder)
    subprocess.Popen('awk \'sub("$", "\\r")\' {0}/{1}.txt > {0}/windowstxt.txt'
                     .format(unix_process_folder, unix_text), shell=True)
    time.sleep(1)


def format_string_to_unix(file_name):
    '''Converts string to be readable in unix'''
    count = 0

    for x in file_name:
        if x == " " or x == "(" or x == ")" or x == ":":
            file_name = file_name[:count] + "\\" + file_name[count:]
            count += 1
        count += 1

    return file_name


def end_message(execution_time, output_folder_location):
    '''Displays where the output files are saved at the end of the program'''
    print "\nTotal runtime: %s" % time.strftime("%H hr, %M min, %S sec",
                                                time.gmtime(execution_time))
    print "Program has finished executing. Files are located at %s\n" % \
          output_folder_location
    logging.info('Execution Time: %s seconds' % execution_time)
    logging.info('Output Folder Location: %s' % output_folder_location)
    logging.info('Program has ended')


if __name__ == "__main__":
    '''Main function'''
    logging.basicConfig(filename='monitor.log', level=logging.INFO, 
                        filemode='a', 
                        format='%(asctime)s - [%(levelname)s] - %(message)s')
    logging.info('')    # Easier to differentiate between processes in log

    output_files_name = "Output_Files"

    if get_directory(output_files_name) is False:
        output_folder_dir = create_folder(output_files_name)
    else:
        output_folder_dir = get_directory(output_files_name)

    print "Process Monitor: %s" % version.__version__ 
    process = get_process_info()
    confirmation_page(process)

    create_subfolder("Output_Files", process.get_file_name())
    process_folder_dir = get_directory(process.get_file_name(), "Output_Files")

    start = time.time()
    Mon.mem_monitor(process, process_folder_dir)
    unix_to_windows(process.get_file_name(), process_folder_dir)
    end_time = time.time() - start - 1

    if check_modules_exist():
        Plot.convert_to_excel(process_folder_dir)
        Plot.plot_data(process, end_time, process_folder_dir)

    end_message(end_time, output_folder_dir)
