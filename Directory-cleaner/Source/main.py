import os
import sys
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
from threading import Thread
from tkinter.filedialog import askdirectory, askopenfilenames, asksaveasfile
import functions
# try to separate classes per files


class MyButton(ttk.Frame):  # is it really good name for class
    def __init__(self, parent, text="", height=37, width=125, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width)

        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1)

    def _bind(self, button, func):
        self._btn.bind(button, func)

# maybe better create more than one window class for diiferent states or implement State pattern
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Directory Cleaner')
        self.geometry('220x210')
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))
        self.resizable(width=False, height=False)

        logo = tk.Label(self, text='Directory Cleaner', font='Helvetica 18 bold')
        logo.pack()

        # good reason to use python decorators for button initializing
        choice_button = MyButton(self, text='Set dir')
        choice_button._bind('<Button-1>', self.choice_dir)
        choice_button.pack()

        empty_label = tk.Label(self)
        empty_label.pack()

        charts_btn = MyButton(self, text='Chart')
        charts_btn._bind('<Button-1>', lambda event: functions.check_json())
        charts_btn.pack()

        empty_label_1 = tk.Label(self)
        empty_label_1.pack()

        exit_button = MyButton(self, text='Exit')
        exit_button._bind('<Button-1>', lambda event: sys.exit())
        exit_button.pack()

        self.delete_flag = True
        self.collect_flag = True
        MainWindow.create_log_file()

    def choice_dir(self, event):
        self.dir_path = askdirectory()
        if self.dir_path:
            self.get_info()

    def get_info(self):
        self.withdraw()
        self.main_menu = tk.Tk()
        self.main_menu.resizable(width=False, height=False)

        self.main_menu.title('Directory Cleaner')
        self.main_menu.geometry('220x220')
        self.main_menu.eval('tk::PlaceWindow %s center' % self.main_menu.winfo_pathname(self.main_menu.winfo_id()))

        self.data_button = MyButton(self.main_menu, text='Get dir info')
        self.data_button._bind('<Button-1>', lambda event: Thread(target=self.dir_info).start())
        self.data_button.pack()

        empty_label_1 = tk.Label(self.main_menu)
        empty_label_1.pack()

        delete_files_btn = MyButton(self.main_menu, text='Delete files')
        delete_files_btn._bind('<Button-1>', self.pick_files)
        delete_files_btn.pack()

        empty_label_2 = tk.Label(self.main_menu)
        empty_label_2.pack()

        self.get_edited_btn = MyButton(self.main_menu, text='Get edited')
        self.get_edited_btn._bind('<Button-1>', lambda event: Thread(target=self.is_checked).start())
        self.get_edited_btn.pack()

        empty_label_3 = tk.Label(self.main_menu)
        empty_label_3.pack()

        back_btn = MyButton(self.main_menu, text='Back')
        back_btn._bind('<Button-1>', self.back)
        back_btn.pack()

        self.main_menu.mainloop()

    def back(self, event):
        self.main_menu.destroy()
        self.deiconify()

    def dir_info(self):
        if self.delete_flag:
            self.delete_flag = False
            self.data_button._btn.config(text='Loading', state='disabled')
            dir_data = functions.get_tree(self.dir_path)
            if sum([float(dir_data[0].split()[0]), dir_data[1]]):
                tkinter.messagebox.showinfo('Information', 'Total size: {dir_data[0]}\nTotal count: {dir_data[1]}')
            else:
                tkinter.messagebox.showinfo('Information', 'Folder is empty')
            self.data_button._btn.config(text='Get dir info', state='active')
            self.delete_flag = True

    def pick_files(self, event):
        counter = 0
        picked_files = []
        files = askopenfilenames(initialdir=self.dir_path)
        if files:
            for file in files:
                functions.delete_files(file)
                counter += 1
                picked_files.append(file)
            functions.change_log(picked_files)
            tkinter.messagebox.showinfo('Information', '{counter} files was deleted.')

    def save_results(self, event):
        target_file = asksaveasfile(mode='w', defaultextension=".txt", initialfile='Modiffed files')
        if target_file is None:
            return
        target_file.write(self.files.encode().decode(target_file.encoding))
        target_file.close()
        tkinter.messagebox.showinfo('Information', 'Successfully')

    def is_checked(self):
        if self.collect_flag:
            self.collect_flag = False
            self.run_collecting()
            self.collect_flag = True

    def run_collecting(self):
        self.get_edited_btn._btn.config(text='Loading', state='disabled')
        files = list(functions.last_changes(self.dir_path))
        if files:
            self.files = '\n'.join([' WAS MODIFFED: '.join(x) for x in files])
            return self.get_edited_files()
        self.get_edited_btn._btn.config(text='Get edited', state='enabled')
        tkinter.messagebox.showinfo('Error', 'No results')

    def get_edited_files(self):
        text_window = tk.Tk()
        text_window.eval('tk::PlaceWindow %s center' % text_window.winfo_pathname(text_window.winfo_id()))
        text_window.resizable(width=False, height=False)

        text_entry = tk.Text(text_window)
        text_entry.pack()

        save_btn = ttk.Button(text_window, text='Save results')
        save_btn.bind('<Button-1>', self.save_results)
        save_btn.pack()

        close_btn = ttk.Button(text_window, text='Close')
        close_btn.bind('<Button-1>', lambda event: text_window.destroy())
        close_btn.pack()

        text_entry.insert('end', self.files)
        text_entry['state'] = 'disabled'

        self.get_edited_btn._btn.config(text='Get edited', state='enabled')
        text_entry.mainloop()

    @staticmethod
    def create_log_file():
        current_path = os.path.join(os.path.dirname(__file__), 'log.json')
        if not os.path.exists(current_path):
            with open(current_path, mode='w') as log:
                log.write('{}')


if __name__ == '__main__':
    Application = MainWindow()
    Application.mainloop()
