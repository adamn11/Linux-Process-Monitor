import matplotlib
import matplotlib.pyplot as plt
import xlwt


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