from Process import Process

import os
import subprocess


def mem_monitor(proc, process_folder):
    '''Reads data from top command and records in text file'''
    text_file = "%s/%s.txt" % (process_folder, process.get_file_name())
    total_mem = get_total_mem()

    print "\n%s PID: %s" % (proc.get_process_name(), proc.get_pid_num())
    print "Total Memory: %s kB" % total_mem
    if proc.get_stop_point() == 0:
        print "Program will run indefinitely until manual cancellation " \
              "(Ctrl + C)"
    else:    
        print "Program will finish at %s." % \
              show_eta(int(proc.get_stop_point()))
    print "Recording process...Press Ctrl+C at any time to stop monitoring."

    logging.info('Monitoring process has started')
    with open(text_file, "w") as txt_file:
        counter = 0
        txt_file.write("Date        Time       MEM         Total        "
                       "Percentage\n")

        try:
            while proc.get_stop_point() == 0:
                start = time.time()
                top_output = subprocess.Popen('top -b -n 1 | grep %s | '
                                              'awk \'{print $%s}\'' %
                                              (proc.get_pid_num(), '10'),
                                              shell=True,
                                              stdout=subprocess.PIPE, )
                mem_percent_output = top_output.stdout.read().strip()
                current_time = time.strftime("%H:%M:%S")
                current_date = datetime.now() 
                fmt_current_date = "%s/%s/%s" % (current_date.month,
                                                 current_date.day,
                                                 current_date.year)
                
                txt_file.write("{} | {} | {} / {} kB | {} %\n".
                               format(fmt_current_date, current_time,
                                      calculate_process_memory_usage
                                      (mem_percent_output, total_mem)
                                      , total_mem, mem_percent_output))
                txt_file.flush()

                counter += float(proc.get_refresh_time())
                time.sleep(float(proc.get_refresh_time()) - (time.time() -
                                                             start))
        except KeyboardInterrupt:
            logging.info('Monitoring process has ended')
            pass
        except IOError:
            logging.error('File does not exist')
            print "The file does not exist"
            sys.exit(1)
    txt_file.close()


def get_total_mem():
    '''Gets the total system RAM memory from /proc/meminfo. Only works on
    Linux machines'''
    meminfo_output = subprocess.Popen('awk \'/MemTotal/ {print $2}\' '
                                      '/proc/meminfo', shell=True,
                                      stdout=subprocess.PIPE, )
    return meminfo_output.stdout.read().strip()