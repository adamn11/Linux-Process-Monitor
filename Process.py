class Process(object):
    def __init__(self, process_name, refresh_time, stop_point,
                 pid_num, start_time):
        self.process_name = process_name
        self.refresh_time = refresh_time
        self.stop_point = stop_point
        self.pid_num = pid_num
        self.start_time = start_time

    def set_new_pid(self, new_pid):
        self.pid_num = new_pid 

    def get_process_name(self):
        return self.process_name

    def get_pid_num(self):
        return self.pid_num

    def get_file_name(self):
        return "%s (%s)" % (self.process_name, self.start_time)

    def get_stop_point(self):
        return self.stop_point

    def get_refresh_time(self):
        return self.refresh_time
