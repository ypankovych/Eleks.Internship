import datetime
import getpass
import json
import os
import tkinter.messagebox

import matplotlib as mpl
import matplotlib.pyplot as plt

# it will be better to separate functions by work they do


def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return '%3.1f %s' % (num, x)
        num /= 1024.0


def get_files_list(folder_path):
    files_tree = os.walk(folder_path)
    result = [os.path.join(folder, file) for folder, _, files in files_tree for file in files]
    # maybe better immediately return this set without additional variable
    return result


def get_tree(dir_name):
    all_files = get_files_list(dir_name)
    total_count = len(all_files) # another unnecessary variable
    total_size = 0
    for file in all_files:
        total_size += os.stat(file).st_size
    total_size = convert_bytes(total_size)
    return total_size, total_count


def delete_files(file):
    os.remove(file)


def change_log(file_names):
    current_path = os.path.join(os.path.dirname(__file__), 'log.json')
    # if you read and write into file maybe better to open him only once
    with open(current_path, mode='r', encoding='utf8') as log:
        current_data = json.load(log)
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d %H:%M:%S")
        current_user = getpass.getuser()
        with open(current_path, 'w') as _log:
            if current_user in current_data:
                current_data[current_user].update({date: file_names})
            else:
                current_data[current_user] = {date: file_names}
            json.dump(current_data, _log, indent=4)


def last_changes(dir_path):
    all_files = get_files_list(dir_path)
    date = datetime.datetime.now()
    delta = datetime.timedelta(days=14)  # another unnecessary variable
    difference = date - delta
    for file in all_files:
        edit_time = os.stat(file).st_mtime
        normalized_time = datetime.datetime.fromtimestamp(edit_time)
        if normalized_time < difference:
            yield os.path.basename(file), str(normalized_time)


def check_json():
    current_user = getpass.getuser()
    current_path = os.path.join(os.path.dirname(__file__), 'log.json')
    if os.path.exists(current_path):
        with open(current_path) as f:
            data = json.load(f)
            if current_user in data:
                return show_charts(current_user, data)
            return tkinter.messagebox.showinfo('Information', 'Current user not found')
    return tkinter.messagebox.showerror('Information', 'Log file does not exist')


def show_charts(current_user, data):
    data_names = [x for x in data[current_user]]
    data_values = [len(data[current_user][y]) for y in data[current_user]]

    dpi = 80  # looks like magic number
    fig = plt.figure(dpi = dpi, figsize = (512 / dpi, 384 / dpi))  # is this variable uses
    mpl.rcParams.update({'font.size': 11})

    plt.title('Deleted files for all time')
    plt.pie(data_values,
            labels = data_values,
            autopct='%.0f',
            radius = 1.1,
            explode = [0.15] + [0 for _ in range(len(data_names) - 1)],
            shadow=True)
    plt.legend(bbox_to_anchor = (-0.16, 0.45, 0.25, 0.25),
               loc = 'lower left',
               labels = data_names)
    plt.show()
