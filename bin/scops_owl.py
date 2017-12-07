# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:01:44 2017

@author: lib
"""
# ------------------
# Library
# ------------------
import tkinter as tk


# ------------------
# Class
# ------------------
from scopsowl.scopsowlgui import AppFetchAffilAuthorDoc


class ScopsOwl(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=False, padx=4, pady=4, ipadx=2, ipady=2)
        self.Apps = dict()
        self.buttons = dict()
        self.create_functions()
    
    def create_functions(self):
        def appfetchaffilauthordoc():
            self.Apps['FetchAffilAuthorDoc'] = AppFetchAffilAuthorDoc(self)
        self.buttons['FetchDoc'] = tk.Button(
            self,
            text='获取文献信息(作者和单位)',
            command=appfetchaffilauthordoc
        )
        self.buttons['FetchDoc'].pack(expand=True)


# ------------------
# Main
# ------------------


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Scops Owl')
    apps = ScopsOwl(root)
    apps.mainloop()

# ------------------
# EOF
# ------------------