# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 10:08:34 2017

@author: lib
"""
# ------------------
# Import Library
# ------------------
import os
# import sys
import logging
import tkinter as tk


# ------------------
# Import Functions and Classes
# ------------------
from scopsowl.fetch import fetch_doc
# from scopsowl.fetch import fetch_document_info


# ------------------
# Errors and logs
# ------------------

logger = logging.getLogger('scops_owl.scopsowlgui')

# ------------------
# Function
# ------------------


# ------------------
# Class
# ------------------
class TextBox(tk.Frame):
    def __init__(self, master, label, width, textwrap, row, column):
        super().__init__(master)
        # make the text box with x and y scrollbar
        self.grid(row=row, column=column)
        self.label = tk.Label(self, text=label)
        self.label.grid(row=0, column=0)
        self.text = tk.Text(
            self,
            borderwidth=3,
            width=width,
            relief=tk.SUNKEN,
            wrap=textwrap
        )
        self.text.grid(row=1, column=0)
        self.scroll_x = tk.Scrollbar(
            self,
            command=self.text.xview,
            orient=tk.HORIZONTAL
        )
        self.scroll_x.grid(
            row=2, column=0, sticky=tk.W + tk.E + tk.N + tk.S
        )
        self.text.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_y = tk.Scrollbar(
            self,
            command=self.text.yview,
            orient=tk.VERTICAL
        )
        self.scroll_y.grid(
            row=1, column=1, sticky=tk.W + tk.E + tk.N + tk.S
        )
        self.text.configure(yscrollcommand=self.scroll_y.set)

    def get(self, index1, index2):
        return self.text.get(index1, index2)

# ------------------


class AppFetchAffilAuthorDoc(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.input_info = dict()
        self._create_text_boxs()
        self._create_year_input()
        self._create_output_file_entry()
        self._create_run_button()

    def _create_text_boxs(self):
        # 建立所有的文本输入框
        # affiliation id text
        # label
        self.affiliation_id_textbox = TextBox(
            self,
            '单位ID（Affiliation ID）输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=0
        )
        self.author_id_textbox = TextBox(
            self,
            '作者ID（Author ID）输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=1
        )
        self.api_key_textbox = TextBox(
            self,
            'API KEY 输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=2
        )
        
    def _create_year_input(self):
        # 建立年份筛选输入框
        self.year_direction = tk.StringVar()
        year_region = tk.Frame(self)
        year_region.grid(row=1, column=0)
        lab = tk.Label(year_region, text='年份')
        lab.grid(row=0, column=0)
        self.year = tk.Entry(year_region)
        self.year.grid(row=0, column=1, columnspan=2)
        r1 = tk.Radiobutton(year_region, text='之前', variable=self.year_direction, value='<')
        r1.grid(row=1, column=0)
        r2 = tk.Radiobutton(year_region, text='当年', variable=self.year_direction, value='=')
        r2.grid(row=1, column=1)
        r3 = tk.Radiobutton(year_region, text='之后', variable=self.year_direction, value='>')
        r3.grid(row=1, column=2)
        
    def _create_output_file_entry(self):
        # 建立输出文件名输入框
        self.file_entry = dict()
        self.output_file_frame = tk.Frame(self)
        self.output_file_frame.grid(row=1, column=1)
        lab = tk.Label(self.output_file_frame, text='工作目录')
        lab.grid(row=0, column=0)
        wk_entry = tk.StringVar()
        wk_entry.set('')
        self.file_entry['wkdir'] = tk.Entry(self.output_file_frame, textvariable=wk_entry)
        self.file_entry['wkdir'].grid(row=0, column=1)
        lab1 = tk.Label(self.output_file_frame, text='作者ID-文献ID文件')
        lab1.grid(row=1, column=0)
        lab2 = tk.Label(self.output_file_frame, text='文献ID-单位')
        lab2.grid(row=2, column=0)
        lab3 = tk.Label(self.output_file_frame, text='文献基本信息')
        lab3.grid(row=3, column=0)
        entry1 = tk.StringVar()
        entry1.set('author_doc.csv')
        self.file_entry['author_doc'] = tk.Entry(self.output_file_frame, textvariable=entry1)
        self.file_entry['author_doc'].grid(row=1, column=1)
        entry2 = tk.StringVar()
        entry2.set('doc_affiliation.csv')
        self.file_entry['doc_affiliation'] = tk.Entry(self.output_file_frame, textvariable=entry2)
        self.file_entry['doc_affiliation'].grid(row=2, column=1)
        entry3 = tk.StringVar()
        entry3.set('document.csv')
        self.file_entry['doc'] = tk.Entry(self.output_file_frame, textvariable=entry3)
        self.file_entry['doc'].grid(row=3, column=1)

    def _create_run_button(self):
        # 建立运行按钮
        self.run_button_frame = tk.Frame(self)
        self.run_button_frame.grid(row=1, column=2)
        self.run_button = tk.Button(self.run_button_frame, text='运行', command=self._run)
        self.run_button.pack(expand=True, anchor=tk.CENTER)

    def _run(self):
        # 保存输入信息
        self.input_info['api_key'] = self.api_key_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.input_info['affiliation_id'] = self.affiliation_id_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.input_info['author_id'] = self.author_id_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.input_info['year'] = self.year.get()
        self.input_info['yeardirection'] = self.year_direction.get().rstrip()
        self.input_info['filepath_wkdir'] = self.file_entry['wkdir'].get()
        self.input_info['filepath_author_doc'] = self.file_entry['author_doc'].get()
        self.input_info['filepath_doc_affiliation'] = self.file_entry['doc_affiliation'].get()
        self.input_info['filepath_doc'] = self.file_entry['doc'].get()
        # 下载文献信息
        fetched = fetch_doc(
            self.input_info['affiliation_id'],
            self.input_info['author_id'],
            self.input_info['year'],
            self.input_info['yeardirection'],
            self.input_info['api_key']
        )
        fetched['author_doc'].to_csv(
            os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_author_doc']),
            index=False
        )
        fetched['document'].to_csv(
            os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_doc']),
            index=False
        )
        fetched['doc_affiliation'].to_csv(
            os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_doc_affiliation']),
            index=False
        )

# ------------------


class AppFetchDocInfo(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)


# ------------------
# EOF
# ------------------
