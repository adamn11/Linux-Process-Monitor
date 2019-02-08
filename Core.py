from Process import Process
import version
import Validations as v

# To record in offline mode, comment out:
#   - convert_to_excel()
#   - plot_data()
#   - import matplotlib
#   - import matplotlib.pyplot as plt
#   - import xlwt

import sys
import os
import subprocess
import time
#import matplotlib
#import matplotlib.pyplot as plt
#import xlwt
from datetime import datetime, timedelta

# Creates a folder that stores the output files of the program
def create_folder():
    '''Creates a folder that stores the output files of the program'''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    new_folder = os.path.join(current_dir, 'Output_Files')

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    return new_folder

def show_eta(seconds_to_completion):
    '''If program is not infinite, then show the date and time of when the program will finish running.'''
    return datetime.now() + timedelta(seconds=seconds_to_completion)

def get_total_mem():
    '''Gets the total system RAM memory from /proc/meminfo. Only works on Linux machines'''
    meminfo_output = subprocess.Popen('awk \'/MemTotal/ {print $2}\' /proc/meminfo', shell=True, stdout=subprocess.PIPE, )
    return meminfo_output.stdout.read().strip()

def calculate_process_memory_usage(proc_usage, total_memory):
    '''Calculates memory in kb using process percentage and total memory of the system'''
    try:
        if "\n" not in proc_usage:
            return round((((float(proc_usage) / 100) * int(total_memory))), 2)
    except ValueError as e:
        print 'Application has been closed'
        print repr(e)
        sys.exit(1)

def mem_monitor(process):
    '''Reads data from top command and records in text file'''
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
                #print repr("%s %s" % (current_time, calculate_process_memory_usage(mem_percent_output, total_mem)))  # Comment out if you don't want values to show during execution
                fmt_current_date = "%s/%s/%s" % (current_date.month, current_date.day, current_date.year)
                txt_file.write("{} | {} | {} / {} kB | {}%\n".format(fmt_current_date, current_time, calculate_process_memory_usage(mem_percent_output, total_mem), total_mem, mem_percent_output))

                txt_file.flush()

                counter += float(process.refresh_time)
                time.sleep(float(process.refresh_time) - (time.time() - start))
        except KeyboardInterrupt:
            pass
        except IOError:
            print "The file does not exist"
            sys.exit(1)
    txt_file.close()

def convert_to_excel(file_name):
    '''Converts text file created from mem_monitor() to an excel sheet'''
    print "Formatting text file to excel..."
    style = xlwt.XFStyle()
    style.num_format_str = "#,###0.00"
    path = create_folder()
    f = open(r"%s/windowstxt.txt" % path, 'r+')
    row_list = []

    for row in f:
        row_list.append(row.split(' '))

    column_list = zip(*row_list)
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet1')

    i = 0
    for column in column_list:
        for item in range(len(column)):
            value = column[item].strip()
            if is_number(value):
                worksheet.write(item, i, float(value), style=style)
            else:
                worksheet.write(item, i, value)
        i += 1

    workbook.save(r'/%s/monitor_output.xls' % path)

def is_number(s):
    '''Returns true if value passed through is a number.'''
    try:
        float(s)
        return True
    except ValueError:
        return False

def unix_to_windows(file_name):
    '''Converts unix text file to be readable on window machines'''
    print "Creating text file suitable for window machines..."
    output_folder_dir = create_folder()
    unix_text = format_string_to_unix(file_name)
    subprocess.Popen('''awk 'sub("$", "\\r")' {0}/{1}.txt > {0}/windowstxt.txt'''.format(output_folder_dir, unix_text), shell=True)
    time.sleep(1)

def format_string_to_unix(file_name):
    '''Converts string ot be readable in unix'''
    count = 0

    for x in file_name:
        if x == " " or x == "(" or x == ")" or x == ":":
            file_name = file_name[:count] + "\\" + file_name[count:]
            count += 1
        count += 1

    return file_name

def plot_data(process, execution_time):
    '''Reads from text file and plots data into graph'''
    print "Plotting data..."
    file_path = create_folder()

    with open("%s/%s.txt" % (file_path, process.get_file_name())) as t:
        data = t.readlines()[1:]

    x = [row.split()[0] for row in data]  # Time
    y = [row.split()[1] for row in data]  # Top column

    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.set_title("%s Memory Monitor (Runtime: %s)" % (process.process_name,
                    time.strftime("%H hr, %M min, %S sec",
                    time.gmtime(execution_time))))
    ax.set_xlabel("Time (%s Second Intervals)" % process.refresh_time)
    ax.set_ylabel("Memory (in mb)")
    dates = matplotlib.dates.datestr2num(x)
    ax.xaxis.set_major_formatter(matplotlib.
                                 dates.DateFormatter('%d/%m/%Y %H:%M:%S'))
    ax.plot_date(dates, y, ls='-', marker='o')

    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig("%s/graph.png" % file_path)

    plt.show()

def confirmation_page(process):
    '''Displays all the information to user before recording memory'''
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
    '''Displays where the output files are saved at the end of the program'''
    print "\nTotal runtime: %s" % time.strftime("%H hr, %M min, %S sec",
                                                time.gmtime(execution_time))
    print "Program has finished executing. Files are located at %s\n" % create_folder()

def check_number_of_processes(pid_list):
    '''Lets users choose the process to record if the process has more than one ID'''
    if len(pid_list) > 1:
        for x in pid_list:
            print x
        pid_input = v.pid_input_validation(pid_list)
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

def main():
    '''Main function'''
    # To record in offline mode, comment out concert_to_excel() and plot_data()
    print "Process Monitor: %s" % version.__version__ 
    process = get_process_info()
    confirmation_page(process)

    start = time.time()
    mem_monitor(process)
    unix_to_windows(process.get_file_name())
    #convert_to_excel(process.get_file_name())
    execution_time = time.time() - start - 1
    #plot_data(process, execution_time)
    end_message(execution_time)

if __name__ == "__main__":
    main()
