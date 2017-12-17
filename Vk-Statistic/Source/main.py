import datetime
import multiprocessing as mp
import sys
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
from threading import Thread

import Vk_API
from charts import show_charts

# looks like God object anti-pattern, try to separate logic by classes
class MyButton(ttk.Frame):  #really bad name for class
    def __init__(self, parent, text="", height=37, width=125, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width)

        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1)

    def _bind(self, button, func):
        self._btn.bind(button, func)

class Application(tk.Tk, Vk_API.MakeAPiConnect):
    def __init__(self):
        super().__init__()  # it is not obvious what this code will do with multiple inheritance, it's better to use composition
        self.title('Auth')
        self.geometry('150x130')
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))
        self.APP_ID = 5868794

        label = tk.Label(self, text='Way of entry')
        label.pack()
        # good case for decorators
        token_btn = MyButton(self, text='Token')
        token_btn._bind('<Button-1>', self.login_with_token)
        token_btn.pack()

        empty_label = tk.Label(self)
        empty_label.pack()

        login_btn = MyButton(self, text='Login/Password')
        login_btn._bind('<Button-1>', self.login_without_token)
        login_btn.pack()
    
    def login_with_token(self, event):
        self.withdraw()
        self.login_window = tk.Tk()
        self.login_window.geometry('150x170')
        self.login_window.title('Auth')
        self.login_window.eval('tk::PlaceWindow %s center' % self.login_window.winfo_pathname(self.login_window.winfo_id()))

        token_label = tk.Label(self.login_window, text='Token')
        token_label.pack()

        self.token_entry = ttk.Entry(self.login_window)
        self.token_entry.pack()

        empty_label = tk.Label(self.login_window)
        empty_label.pack()

        login_button = MyButton(self.login_window, text='Log in')
        login_button._bind('<Button-1>', self.main_auth)
        login_button.pack()

        empty_label = tk.Label(self.login_window)
        empty_label.pack()

        back_btn = MyButton(self.login_window, text='Back')
        back_btn._bind('<Button-1>', self.back)
        back_btn.pack()

    def back(self, event):
        self.login_window.destroy()
        if hasattr(self, 'token_entry'):
            del self.token_entry
        self.deiconify()

    def login_without_token(self, event):
        self.withdraw()
        self.login_window = tk.Tk()
        self.login_window.geometry('150x220')
        self.login_window.title('Auth')
        self.login_window.eval('tk::PlaceWindow %s center' % self.login_window.winfo_pathname(self.login_window.winfo_id()))

        label_log = tkinter.Label(self.login_window, text='Login', font='arial 14')
        label_log.pack()

        self.entry_log = ttk.Entry(self.login_window)
        self.entry_log.pack()

        label_pass = tkinter.Label(self.login_window, text='Password', font='arial 14')
        label_pass.pack()

        self.entry_pass = ttk.Entry(self.login_window, show='●')
        self.entry_pass.pack()

        empty_label = tk.Label(self.login_window)
        empty_label.pack()

        self.btn = MyButton(self.login_window, text='Login')
        self.btn._bind('<Button-1>', self.main_auth)
        self.btn.pack()

        empty_label = tk.Label(self.login_window)
        empty_label.pack()

        back_btn = MyButton(self.login_window, text='Back')
        back_btn._bind('<Button-1>', self.back)
        back_btn.pack()

    def main_auth(self, event):
        if hasattr(self, 'token_entry'):
            if not super(tk.Tk, self).init_token(token=self.token_entry.get()):
                return Application.login_error()
        else:
            if self.entry_log.get() == '' or self.entry_pass.get() == '':
                return tkinter.messagebox.showerror('Error', 'fill in the fields')
            else:
                if not super(tk.Tk, self).init_login(self.APP_ID, self.entry_log.get(), self.entry_pass.get()):
                    return Application.login_error()
        self.login_window.destroy()
        self.main_menu()


    # try to separate static functions
    @staticmethod
    def login_error():
        tkinter.messagebox.showerror('Error', 'Incorrect auth data')

    @staticmethod
    def charts(data):
        charts_win = tk.Tk()
        charts_win.title('Charts')
        charts_win.eval('tk::PlaceWindow %s center' % charts_win.winfo_pathname(charts_win.winfo_id()))

        age_chart_btn = MyButton(charts_win, text='Age chart')
        age_chart_btn._bind('<Button-1>', lambda event: mp.Process(target=show_charts, args=(set(data['age']), [data['age'].count(x) for x in set(data['age'])], 'Age chart')).start())
        age_chart_btn.pack()

        gender_chart_btn = MyButton(charts_win, text='Gender chart')
        gender_chart_btn._bind('<Button-1>', lambda event: mp.Process(target=show_charts, args=(['Male', 'Famale'], [len(data['men']), len(data['women'])], 'Gender chart')).start())
        gender_chart_btn.pack()

    @staticmethod
    def get_names(sex, data):
        if data[sex]:
            get_names_win = tk.Tk()
            get_names_win.title(sex)
            get_names_win.eval('tk::PlaceWindow %s center' % get_names_win.winfo_pathname(get_names_win.winfo_id()))

            text_field = tk.Text(get_names_win)
            text_field.pack()

            close_btn = ttk.Button(get_names_win, text='Close')
            close_btn.bind('<Button-1>', lambda event: get_names_win.destroy())
            close_btn.pack()

            for i in data[sex]:
                text_field.insert('end', f'Name: {i["first_name"]}, Last name: {i["last_name"]}, ID: {i["uid"]}\n')
            text_field['state'] = 'disabled'
        else:
            tkinter.messagebox.showinfo('info', 'Empty')
    
    def get_me(self):
        self.get_me_btn._btn.config(text='Process', state='disabled')
        data = super(tk.Tk, self).collect_friends()
        self.get_me_btn._btn.config(text='Friends data', state='active')
        if data['friends_count']:
            window = tk.Tk()
            window.title('Friends data')
            window.eval('tk::PlaceWindow %s center' % window.winfo_pathname(window.winfo_id()))
            
            male_label = tk.Label(window, text='Male count: ')
            male_label.grid(row=1, column=1)

            male_count_lbl = tk.Label(window, text=len(data['men']))
            male_count_lbl.grid(row=1, column=2)

            famale_label = tk.Label(window, text='Famale count: ')
            famale_label.grid(row=2, column=1)

            famale_count_lbl = tk.Label(window, text=len(data['women']))
            famale_count_lbl.grid(row=2, column=2)

            male_btn = ttk.Button(window, text='Male')
            male_btn.bind('<Button-1>', lambda event: Application.get_names('men', data))
            male_btn.grid(row=3, column=1)

            famale_btn = ttk.Button(window, text='Famale')
            famale_btn.bind('<Button-1>', lambda event: Application.get_names('women', data))
            famale_btn.grid(row=3, column=2)

            friends_label = tk.Label(window, text='Friends count: ')
            friends_label.grid(row=4, column=1)

            friends_count_lbl = tk.Label(window, text=data['friends_count'])
            friends_count_lbl.grid(row=4, column=2)

            classmates_lbl = tk.Label(window, text='Classmates: ')
            classmates_lbl.grid(row=5, column=1)

            classmates_count_lbl = tk.Label(window, text=len(data['classmates']))
            classmates_count_lbl.grid(row=5, column=2)

            cob_label = tk.Label(window, text='Same city: ')
            cob_label.grid(row=6, column=1)

            cob_count_lbl = tk.Label(window, text=len(data['cob']))
            cob_count_lbl.grid(row=6, column=2)

            names_btn = ttk.Button(window, text='Get names')
            names_btn.bind('<Button-1>', lambda event: Application.get_names('cob', data))
            names_btn.grid(row=7, column=1)

            charts_btn = ttk.Button(window, text='Charts')
            charts_btn.bind('<Button-1>', lambda event: Application.charts(data))
            charts_btn.grid(row=7, column=2)
            window.mainloop()
        else:
            tkinter.messagebox.showinfo('info', 'You have no friends')

    def delete_groups(self):
        self.clear_groups_btn._btn.config(text='Process', state='disabled')
        all_groups = super(tk.Tk, self).collect_all_groups()
        if all_groups[0]:
            ask = tkinter.messagebox.askyesno('ASK', 'Found {} groups. Delete?'.format(all_groups[0]))
            if ask:
                super(tk.Tk, self).delete_groups(all_groups)
                tkinter.messagebox.showinfo('info', 'Done')
        else:
            tkinter.messagebox.showinfo('info', 'You have no groups')
        self.clear_groups_btn._btn.config(text='Delete groups', state='active')

    def delete_friends(self):
        self.clear_friends_btn._btn.config(text='Process', state='disabled')
        all_friends = super(tk.Tk, self).collect_all_friends()
        if all_friends:
            ask = tkinter.messagebox.askyesno('ASK', 'Found {} friends. Delete?'.format(len(all_friends)))
            if ask:
                super(tk.Tk, self).delete_friends(all_friends)
                tkinter.messagebox.showinfo('info', 'Done')
        else:
            tkinter.messagebox.showinfo('info', 'You have no friends')
        self.clear_friends_btn._btn.config(text='Delete friends', state='active')

    def clear_wall(self):
        self.clear_wall_btn._btn.config(text='Process', state='disabled')
        all_posts = super(tk.Tk, self).collect_wall()
        if all_posts[0]:
            ask = tkinter.messagebox.askyesno('ASK', 'Found {} posts. Delete?'.format(all_posts[0]))
            if ask:
                super(tk.Tk, self).clear_wall(all_posts)
                tkinter.messagebox.showinfo('info', 'Done')
        else:
            tkinter.messagebox.showinfo('info', 'Wall is empty')
        self.clear_wall_btn._btn.config(text='Clear wall', state='active')
    
    def show_item(self, event):
        user_info = tk.Tk()
        user_info.title('User info')
        user_info.eval('tk::PlaceWindow %s center' % user_info.winfo_pathname(user_info.winfo_id()))

        uid = self.format_friends[self.listbox.get(event.widget.curselection()[0])]
        curr_user = super(tk.Tk, self).get_user(uid)

        label = tk.Label(user_info, text='Firstname: ')
        label.grid(row=1, column=1)

        firstname = tk.Label(user_info, text=curr_user[0]['first_name'])
        firstname.grid(row=1, column=2)

        lastname_lbl = tk.Label(user_info, text='Lastname: ')
        lastname_lbl.grid(row=2, column=1)

        lastname = tk.Label(user_info, text=curr_user[0]['last_name'])
        lastname.grid(row=2, column=2)

        birthday_lbl = tk.Label(user_info, text='Birthday: ')
        birthday_lbl.grid(row=3, column=1)

        birthday = tk.Label(user_info, text=curr_user[0]['bdate'] if curr_user[0].get('bdate') else 'not indicated')
        birthday.grid(row=3, column=2)

        lastseen_lbl = tk.Label(user_info, text='Last seen: ')
        lastseen_lbl.grid(row=4, column=1)

        lastseen = tk.Label(user_info, text=datetime.datetime.fromtimestamp(int(curr_user[0]['last_seen']['time'])).strftime('%Y-%m-%d %H:%M:%S'))
        lastseen.grid(row=4, column=2)

        online_lbl = tk.Label(user_info, text='Online: ')
        online_lbl.grid(row=5, column=1)

        online = tk.Label(user_info, text='Yes' if curr_user[0]['online'] else 'No')
        online.grid(row=5, column=2)

    def get_friends_info(self):
        self.get_friends._btn.config(text='Process', state='disabled')
        all_friends = super(tk.Tk, self).collect_all_friends()
        self.get_friends._btn.config(text='Get friends', state='active')
        if all_friends:
            f_root = tk.Tk()
            f_root.eval('tk::PlaceWindow %s center' % f_root.winfo_pathname(f_root.winfo_id()))
            self.format_friends = {f"{x['first_name']} {x['last_name']}": x['uid'] for x in all_friends}
            self.listbox = tk.Listbox(f_root)
            self.listbox.bind('<<ListboxSelect>>', self.show_item)
            self.listbox.pack()
            for i in self.format_friends:
                self.listbox.insert('end', i)
            f_root.mainloop()
        else:
            tkinter.messagebox.showinfo('info', 'You have no friends')

    def main_menu(self):
        root = tk.Tk()
        root.title(u'VK-Statistics')
        root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))

        self.get_me_btn = MyButton(root, text='Friends data')
        self.get_me_btn._bind('<Button-1>', lambda event: Thread(target=self.get_me).start())
        self.get_me_btn.pack()

        self.clear_groups_btn = MyButton(root, text='Delete groups')
        self.clear_groups_btn._bind('<Button-1>', lambda event: Thread(target=self.delete_groups).start())
        self.clear_groups_btn.pack()

        self.clear_friends_btn = MyButton(root, text='Delete friends')
        self.clear_friends_btn._bind('<Button-1>', lambda event: Thread(target=self.delete_friends).start())
        self.clear_friends_btn.pack()

        self.get_friends = MyButton(root, text='Get friends')
        self.get_friends._bind('<Button-1>', lambda event: Thread(target=self.get_friends_info).start())
        self.get_friends.pack()

        self.clear_wall_btn = MyButton(root, text='Clear wall')
        self.clear_wall_btn._bind('<Button-1>', lambda event: Thread(target=self.clear_wall).start())
        self.clear_wall_btn.pack()

        exit_btn = MyButton(root, text='Exit')
        exit_btn._bind('<Button-1>', lambda event: sys.exit())
        exit_btn.pack()
        root.mainloop()

if __name__ == '__main__':
    App = Application()
    App.mainloop()
