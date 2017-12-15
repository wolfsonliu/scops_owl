# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 10:08:34 2017

@author: lib
"""
# ------------------
# Import Library
# ------------------
import os
import io
import logging
import tkinter as tk


# ------------------
# Import Functions and Classes
# ------------------
from scopsowl.fetch import fetch_doc
from scopsowl.fetch import fetch_document_info
from scopsowl.guitool import TextBox


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
class AppFetchAffilAuthorDoc(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.input_info = dict()  # store input data
        self._create_text_boxs()
        self._create_year_input()
        self._create_output_file_entry()
        self._create_run_button()

    def _create_text_boxs(self):
        # 建立所有的文本输入框
        # affiliation id text
        # label
        text_frame = tk.Frame(self)
        text_frame.grid(row=0, column=0, columnspan=3)
        self.affiliation_id_textbox = TextBox(text_frame, '单位ID（Affiliation ID）输入框', width=40, textwrap=tk.NONE)
        self.affiliation_id_textbox.grid(row=0, column=0)
        self.author_id_textbox = TextBox(text_frame, '作者ID（Author ID）输入框', width=40, textwrap=tk.NONE)
        self.author_id_textbox.grid(row=0, column=1)
        self.api_key_textbox = TextBox(text_frame, 'API KEY 输入框', width=40, textwrap=tk.NONE)
        self.api_key_textbox.grid(row=0, column=2)
        
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
        self.input_info = dict()  # store input data
        self._create_text_boxs()
        self._create_output_file_entry()
        self._create_run_button()

    def _create_text_boxs(self):
        # 建立所有的文本输入框
        # affiliation id text
        # label
        text_frame = tk.Frame(self)
        text_frame.pack(padx=2, pady=2)
        self.scopus_id_textbox = TextBox(text_frame, '文章 ID（SCOPUS ID）输入框', width=40, textwrap=tk.NONE)
        self.scopus_id_textbox.grid(row=0, column=0)
        self.api_key_textbox = TextBox(text_frame, 'API KEY 输入框', width=40, textwrap=tk.NONE )
        self.api_key_textbox.grid(row=0, column=1)

    def _create_output_file_entry(self):
        # 建立输出文件名输入框
        self.file_entry = dict()
        self.output_file_frame = tk.Frame(self)
        self.output_file_frame.pack(padx=2, pady=2)
        title = tk.Label(self.output_file_frame, text='输出文件信息')
        title.grid(row=0, column=0, columnspan=2)
        lab = tk.Label(self.output_file_frame, text='工作目录')
        lab.grid(row=1, column=0)
        wk_entry = tk.StringVar()
        wk_entry.set('')
        self.file_entry['wkdir'] = tk.Entry(self.output_file_frame, textvariable=wk_entry)
        self.file_entry['wkdir'].grid(row=1, column=1)
        lab1 = tk.Label(self.output_file_frame, text='文献基本信息')
        lab1.grid(row=2, column=0)
        entry1 = tk.StringVar()
        entry1.set('document_coredata.csv')
        self.file_entry['document_coredata'] = tk.Entry(self.output_file_frame, textvariable=entry1)
        self.file_entry['document_coredata'].grid(row=2, column=1)
        lab2 = tk.Label(self.output_file_frame, text='文献作者信息')
        lab2.grid(row=3, column=0)
        entry2 = tk.StringVar()
        entry2.set('document_author.csv')
        self.file_entry['document_author'] = tk.Entry(self.output_file_frame, textvariable=entry2)
        self.file_entry['document_author'].grid(row=3, column=1)
        lab3 = tk.Label(self.output_file_frame, text='文献单位信息')
        lab3.grid(row=4, column=0)
        entry3 = tk.StringVar()
        entry3.set('document_affiliation.csv')
        self.file_entry['document_affiliation'] = tk.Entry(self.output_file_frame, textvariable=entry3)
        self.file_entry['document_affiliation'].grid(row=4, column=1)
        lab4 = tk.Label(self.output_file_frame, text='文献ID-作者ID-单位ID')
        lab4.grid(row=5, column=0)
        entry4 = tk.StringVar()
        entry4.set('document_authorid_affiliationid.csv')
        self.file_entry['document_authorid_affiliationid'] = tk.Entry(self.output_file_frame, textvariable=entry4)
        self.file_entry['document_authorid_affiliationid'].grid(row=5, column=1)
        lab5 = tk.Label(self.output_file_frame, text='文献领域信息')
        lab5.grid(row=6, column=0)
        entry5 = tk.StringVar()
        entry5.set('document_subject_area.csv')
        self.file_entry['document_subject_area'] = tk.Entry(self.output_file_frame, textvariable=entry5)
        self.file_entry['document_subject_area'].grid(row=6, column=1)
        lab6 = tk.Label(self.output_file_frame, text='文献关键词信息')
        lab6.grid(row=7, column=0)
        entry6 = tk.StringVar()
        entry6.set('document_keyword.csv')
        self.file_entry['document_keyword'] = tk.Entry(self.output_file_frame, textvariable=entry6)
        self.file_entry['document_keyword'].grid(row=7, column=1)

    def _create_run_button(self):
        # 建立运行按钮
        self.run_button_frame = tk.Frame(self)
        self.run_button_frame.pack(padx=2, pady=2)
        self.run_button = tk.Button(self.run_button_frame, text='运行', command=self._run)
        self.run_button.pack(side=tk.RIGHT, expand=True, anchor=tk.CENTER)

    def _run(self):
        self.input_info['api_key'] = self.api_key_textbox.get(1.0, tk.END).rstrip().split('\n')  # get api keys
        self.input_info['scopus_id'] = self.scopus_id_textbox.get(1.0, tk.END).rstrip().split('\n')  # get scopus id
        # dirs and file names
        self.input_info['filepath_wkdir'] = self.file_entry['wkdir'].get()
        self.input_info['filepath_document_coredata'] = self.file_entry['document_coredata'].get()
        self.input_info['filepath_document_author'] = self.file_entry['document_author'].get()
        self.input_info['filepath_document_affiliation'] = self.file_entry['document_affiliation'].get()
        self.input_info['filepath_document_authorid_affiliationid'] = self.file_entry[
            'document_authorid_affiliationid'
        ].get()
        self.input_info['filepath_document_subject_area'] = self.file_entry['document_subject_area'].get()
        self.input_info['filepath_document_keyword'] = self.file_entry['document_keyword'].get()
        for i in range(10):
            logger.debug(str(i))
        # # fetch data
        # fetched = fetch_document_info(
        #     self.input_info['scopus_id'],
        #     self.input_info['api_key']
        # )
        # # store data
        # fetched['document'].to_csv(
        #     os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_document_coredata']),
        #     index=False
        # )
        # fetched['author'].to_csv(
        #     os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_document_author']),
        #     index=False
        # )
        # fetched['affiliation'].to_csv(
        #     os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_document_affiliation']),
        #     index=False
        # )
        # fetched['author_affiliation'].to_csv(
        #     os.path.join(
        #         self.input_info['filepath_wkdir'],
        #         self.input_info['filepath_document_authorid_affiliationid']
        #     ),
        #     index=False
        # )
        # fetched['subject_area'].to_csv(
        #     os.path.join(self.input_info['filepath_wkdir'], self.input_info['document_subject_area']),
        #     index=False
        # )
        # fetched['keyword'].to_csv(
        #     os.path.join(self.input_info['filepath_wkdir'], self.input_info['filepath_document_keyword']),
        #     index=False
        # )

# ------------------
# EOF
# ------------------
