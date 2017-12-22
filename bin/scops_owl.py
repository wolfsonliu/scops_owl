# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:01:44 2017

@author: lib
"""
# ------------------
# Import Library
# ------------------
import tkinter as tk
import logging


# ------------------
# Import Functions and Classes
# ------------------
from scopsowl.scopsowlgui import AppFetchAffilAuthorDoc
from scopsowl.scopsowlgui import AppFetchDocInfo
from scopsowl.scopsowlgui import AppFetchAuthorInfo
from scopsowl.scopsowlgui import AppFetchAffiliationInfo
from scopsowl.guitool import TextBox
from scopsowl.guitool import WidgetLogger

# ------------------
# Errors and logs
# ------------------
logger = logging.getLogger('scops_owl')
logger.setLevel(logging.DEBUG)


# ------------------
# Function
# ------------------


# ------------------
# Class
# ------------------
class ScopsOwl(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=False, padx=4, pady=4)
        self.Apps = dict()
        self.Buttons = dict()
        self._create_functions()
        self._create_log_box()
    
    def _create_functions(self):
        # 获取文献信息按钮
        function_frame = tk.Frame(self)
        function_frame.pack(side=tk.TOP, expand=True, padx=2, pady=2)
        function_frame.grid_columnconfigure(0, weight=1)
        function_frame.grid_columnconfigure(1, weight=1)

        # make AppFetchAffilAuthorDoc button
        def app_fetch_affil_author_doc():
            self.Apps['FetchAffilAuthorDoc'] = AppFetchAffilAuthorDoc(self)
        self.Buttons['FetchDoc'] = tk.Button(
            function_frame,
            text='获取作者和单位文献列表',
            command=app_fetch_affil_author_doc
        )
        self.Buttons['FetchDoc'].grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        # make AppFetchDocInfo button
        def app_fetch_doc_info():
            self.Apps['FetchDocInfo'] = AppFetchDocInfo(self)
        self.Buttons['FetchDocInfo'] = tk.Button(
            function_frame,
            text='获取文献基本信息（SCOPUS ID）',
            command=app_fetch_doc_info
        )
        self.Buttons['FetchDocInfo'].grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

        # make AppFetchAuthorInfo button
        def app_fetch_author_info():
            self.Apps['FetchAuthorInfo'] = AppFetchAuthorInfo(self)
        self.Buttons['FetchAuthorInfo'] = tk.Button(
            function_frame,
            text='获取作者基本信息（AUTHOR ID）',
            command=app_fetch_author_info
        )
        self.Buttons['FetchAuthorInfo'].grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        # make AppFetchAuthorInfo button
        def app_fetch_affiliation_info():
            self.Apps['FetchAffiliationInfo'] = AppFetchAffiliationInfo(self)
        self.Buttons['FetchAffiliationInfo'] = tk.Button(
            function_frame,
            text='获取单位基本信息（AUTHOR ID）',
            command=app_fetch_affiliation_info
        )
        self.Buttons['FetchAffiliationInfo'].grid(row=1, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

    def _create_log_box(self):
        log_box = tk.Frame(self)
        log_box.pack(side=tk.BOTTOM, expand=True, padx=2, pady=2)
        self.log_text_box = TextBox(log_box, '运行记录', width=80, textwrap=tk.NONE)
        self.log_text_box.grid(row=0, column=0)
        widget_handler = WidgetLogger(self.log_text_box)
        debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if logger.level == logging.DEBUG:
            widget_handler.setFormatter(debug_formatter)
        else:
            widget_handler.setFormatter(info_formatter)
        logger.addHandler(widget_handler)


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
