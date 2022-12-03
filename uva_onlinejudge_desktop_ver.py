import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
import requests
from bs4 import BeautifulSoup
import easygui

class loginApp(tk.Toplevel):

    logindatas = {}

    def __init__(self, parent,logindatas, return_logindatas):
        super().__init__()

        self.logindatas = logindatas
        self.return_logindatas = return_logindatas

        self.title("login")
        self.geometry("400x300")
        self.usernameLabel = tk.Label(self, text="username")
        self.usernameLabel.pack()
        self.username = tk.Entry(self)
        self.username.pack()
        self.passwordLabel = tk.Label(self, text="password")
        self.passwordLabel.pack()
        self.password = tk.Entry(self, show='*')
        self.password.pack()
        self.loginBTN = tk.Button(self, text="Login", command=self.login)
        self.loginBTN.pack()

    def login(self):
        self.logindatas['username'] = self.username.get()
        self.logindatas['passwd'] = self.password.get()
        print(f'loginApp: {self.logindatas}')
        self.return_logindatas(self.logindatas)
        self.destroy()


class MianApp(tk.Tk):
    # web object
    session = requests.Session()
    logindatas = {}

    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("uva_onlinejudge_desktop_ver")
        self.get_headers()
        self.login()

    def login(self):

        window = loginApp(self,self.logindatas, self.get_logindatas)
        window.grab_set()


    def get_logindatas(self,logindatas):
        self.logindatas = logindatas
        print(f'MianApp: {self.logindatas}')

        url = "https://onlinejudge.org/index.php?option=com_comprofiler&task=login"
        res = self.session.post(url, data=self.logindatas)
        self.chech_login(res.text)

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


    def chech_login(self,res):
        if 'Quick Submit' in res:
            print('login success')
            return True
        else:
            print('login fail')
            return False


if __name__ == "__main__":
    app = MianApp()
    app.mainloop()
