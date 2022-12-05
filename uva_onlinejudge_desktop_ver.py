import time
import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
from tkinter import messagebox
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
import tkinter.font as tkfont
import threading


class loginApp(tk.Toplevel):
    logindatas = {}

    def __init__(self, parent, logindatas, return_logindatas, return_exit):
        super().__init__(parent)

        self.logindatas = logindatas
        self.return_logindatas = return_logindatas
        self.return_exit = return_exit

        self.title("login")
        self.geometry("400x300")
        self.username_label = tk.Label(self, text="username")
        self.username_label.pack()
        self.username = tk.Entry(self)
        self.username.pack()
        self.password_label = tk.Label(self, text="password")
        self.password_label.pack()
        self.password = tk.Entry(self, show='*')
        self.password.pack()
        self.login_btn = tk.Button(self, text="Login", command=self.login)
        self.login_btn.pack()
        self.exit_btn = tk.Button(self, text="Exit", command=self.exit_program)
        self.exit_btn.pack()

    def login(self):
        self.logindatas['username'] = self.username.get()
        self.logindatas['passwd'] = self.password.get()
        # print(f'loginApp: {self.logindatas}')
        self.return_logindatas(self.logindatas)
        self.destroy()

    def exit_program(self):
        print("exit")
        self.return_exit()
        self.destroy()


class MianApp(tk.Tk):
    # web object
    session = requests.Session()
    logindatas = {}
    login_status = False

    # uhunt object
    uid = ''
    Verdict_ID = {10: 'Submission error',
                  15: 'Can\'t be judged',
                  20: 'In queue',
                  30: 'CE',
                  35: 'Restricted function',
                  40: 'RE',
                  45: 'Output limit',
                  50: 'TLE',
                  60: 'MLT',
                  70: 'WA',
                  80: 'PE',
                  90: 'AC'
                  }

    Language_ID = {
        1: "ANSI C",
        2: "Java",
        3: "C++",
        4: "Pascal",
        5: "C++11"
    }

    # app object
    exited = False
    insert_lock = False

    def __init__(self):
        super().__init__()

        self.geometry("1000x600")
        self.title("uva_onlinejudge_desktop_ver")
        self.problem_id_label = tk.Label(self, text="problem_id")
        self.problem_id = tk.Entry(self)
        self.open_file_btn = tk.Button(self, text="open file", command=self.open_file)

        self.language_var = tk.StringVar()
        self.language_label = tk.Label(self, text="language")
        self.language1 = tk.Radiobutton(self,
                                        text="ANSI C 5.3.0 - GNU C Compiler with options: -lm -lcrypt -O2 -pipe -ansi -DONLINE_JUDGE",
                                        value=1, variable=self.language_var)
        self.language2 = tk.Radiobutton(self, text="JAVA 1.8.0 - OpenJDK Java", value=2, variable=self.language_var)
        self.language3 = tk.Radiobutton(self,
                                        text="C++ 5.3.0 - GNU C++ Compiler with options: -lm -lcrypt -O2 -pipe -DONLINE_JUDGE",
                                        value=3, variable=self.language_var)
        self.language4 = tk.Radiobutton(self, text="PASCAL 3.0.0 - Free Pascal Compiler", value=4,
                                        variable=self.language_var)
        self.language5 = tk.Radiobutton(self,
                                        text="C++11 5.3.0 - GNU C++ Compiler with options: -lm -lcrypt -O2 -std=c++11 -pipe -DONLINE_JUDGE",
                                        value=5, variable=self.language_var)
        self.language6 = tk.Radiobutton(self, text="PYTH3 3.5.1 - Python 3", value=6, variable=self.language_var)
        self.code_label = tk.Label(self, text="Paste your code...")
        self.code_text = tk.Text(self)
        self.submit_btn = tk.Button(self, text="submit", command=self.submit)
        self.submit_result_label = tk.Label(self, text="submit result")
        self.submit_result_list = tk.Listbox(self, width=40)

        font = tkfont.Font(font=self.code_text['font'])
        tab = font.measure('    ')
        self.code_text.config(tabs=tab)

        self.language_var.set('1')
        self.problem_id_label.grid(row=0, column=0)
        self.problem_id.grid(row=0, column=1, sticky="WE")
        self.open_file_btn.grid(row=0, column=1, sticky="E")
        self.language_label.grid(row=1, column=0, rowspan=6)
        self.language1.grid(row=1, column=1, sticky='W')
        self.language2.grid(row=2, column=1, sticky='W')
        self.language3.grid(row=3, column=1, sticky='W')
        self.language4.grid(row=4, column=1, sticky='W')
        self.language5.grid(row=5, column=1, sticky='W')
        self.language6.grid(row=6, column=1, sticky='W')
        self.code_label.grid(row=7, column=0)
        self.code_text.grid(row=7, column=1, sticky="WE")
        self.submit_btn.grid(row=8, column=1)
        self.submit_result_label.grid(row=0, column=2)
        self.submit_result_list.grid(row=1, column=2, rowspan=7, sticky="NS")

        #menu
        self.menubar = tk.Menu(self)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='help', menu=self.helpmenu)
        self.helpmenu.add_command(label='about', command=self.about)
        self.config(menu=self.menubar)

        #control panel
        self.control_panel = tk.Frame(self)
        self.control_panel.grid(row=9, column=0, columnspan=3, sticky="WE")

        self.user_label = tk.Label(self.control_panel, text="user:")
        self.user_label.pack(side="left")

        self.get_headers()  # initializate logindatas aka headers
        self.login()

    def login(self):
        window = loginApp(self, self.logindatas, self.get_logindatas, self.set_exit)
        window.attributes('-topmost', True)
        window.wait_window()
        window.destroy()

        if self.exited:
            self.exit_program()
            return

        self.lift()
        # print(f'MianApp: {self.logindatas}')

        url = "https://onlinejudge.org/index.php?option=com_comprofiler&task=login"
        res = self.session.post(url, data=self.logindatas)

        if not self.check_login(res.text):
            messagebox.showerror("error", "login failed!\nplease check your username and password")
            self.login()
        else:
            self.get_uid()
            messagebox.showinfo("info", "login success!")
            self.user_label.config(text=f"user: {self.logindatas['username']}")

    # get logindatas and login onlinejudge
    def get_logindatas(self, logindatas):
        self.logindatas = logindatas

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as f:
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(1.0, f.read())

    def submit(self):
        if not self.login_status:
            print('please login first')
            return
        if not self.problem_id.get():
            print('please input problem_id')
            return
        if not self.code_text.get(1.0, 'end'):
            print('please input code')
            return

        datas = {}
        datas['problemid'] = ''
        datas['category'] = ''
        datas['localid'] = self.problem_id.get()
        datas['language'] = self.language_var.get()
        datas['code'] = self.code_text.get(1.0, 'end')
        datas['codeupl'] = ''

        print(f"{datas=}")

        subid = ''

        try:
            res = self.session.post(
                'https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25&page=save_submission', data=datas,
                timeout=10)
            if not self.check_login(res.text):
                messagebox.showerror("error", "you are not logged in!\nplease login again")
                self.login()
                return
            res_id = res.url.split('&')[-1].split('=')[-1]
            if res_id == 'You+have+to+input+a+problem+ID.':
                print('submit fail')
            else:
                print('submit success')
                print(res_id.split('+')[-1])
                subid = res_id.split('+')[-1]
        except requests.exceptions.Timeout:
            print('timeout')
            return

        self.submit_result_list.insert(tk.END, f"{subid} {datas['localid']} wait")

        t = threading.Thread(target=self.get_summit_result,
                             args=(subid, self.submit_result_list.size() - 1, datas['localid']))
        t.start()

    def get_summit_result(self, subid, index, problem_id):
        flag = True
        subres = []
        while flag:
            res = requests.get(f"https://uhunt.onlinejudge.org/api/subs-user/{self.uid}/{str(int(subid) - 1)}").json()
            for i in sorted(res['subs'], key=lambda x: x[0]):
                if i[0] == int(subid):
                    if i[2] == 0:
                        print('waiting')
                        time.sleep(3)
                        break
                    else:
                        print(i)
                        print('done')
                        subres = i
                        flag = False
                        break

        while self.insert_lock:
            time.sleep(0.1)

        self.insert_lock = True
        self.submit_result_list.delete(index)
        self.submit_result_list.insert(index,
                                       f"{subid} {problem_id} {self.Verdict_ID[subres[2]]} "
                                       f"{self.Language_ID[subres[5]]} {subres[3]/1000}ms")
        self.insert_lock = False

    def set_exit(self):
        self.exited = True

    def exit_program(self):
        self.destroy()

    # get headers
    def get_headers(self):
        url = 'https://onlinejudge.org/'
        headers = {'user-agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print("get_headers fail")
            exit(f"can not open {url}")

        inputs = BeautifulSoup(r.text, 'html.parser').find_all('input')
        for i in inputs:
            # print(i)
            if i.get('value') != None:
                self.logindatas[i['name']] = i['value']
            else:
                self.logindatas[i['name']] = ''

    def get_uid(self):
        self.uid = requests.get(f"https://uhunt.onlinejudge.org/api/uname2uid/{self.logindatas['username']}").text

    def check_login(self, res):
        if 'Quick Submit' in res:
            print('login success')
            self.login_status = True
            return True
        else:
            print('login fail')
            self.login_status = False
            return False

    def about(self):
        messagebox.showinfo("about", "author: Andrew-Liang\ngithub:https://github.com/567andrew567/uva_onlinejudge_desktop_ver")

if __name__ == "__main__":
    app = MianApp()
    app.mainloop()
