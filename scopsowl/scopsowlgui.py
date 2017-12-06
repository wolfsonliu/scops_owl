# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 10:08:34 2017

@author: lib
"""
# ------------------
# Library
# ------------------
import os
import sys
import logging
import tkinter as tk

# ------------------
# Function
# ------------------
from scopsowl.fetch import fetch_doc

logger = logging.getLogger(os.path.basename(__file__).replace('.py', '')).addHandler(logging.StreamHandler())

# ------------------
# Class
# ------------------


class AppFetchDoc(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.inputinfo = dict()
        self._create_textboxs()
        self._create_yearinput()
        self._create_outputfileentry()
        self._create_runbutton()


    def _create_textboxs(self):
        # 建立所有的文本输入框
        # affiliation id text
        # label
        self.affiliation_id_textbox = self._textbox(
            '单位ID（Affiliation ID）输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=0
        )
        self.author_id_textbox = self._textbox(
            '作者ID（Author ID）输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=1
        )
        self.api_key_textbox = self._textbox(
            'API KEY 输入框',
            width=40, textwrap=tk.NONE,
            row=0, column=2
        )
        
    def _create_yearinput(self):
        # 建立年份筛选输入框
        self.yeardirection = tk.StringVar()
        yearregion = tk.Frame(self)
        yearregion.grid(row=1, column=0)
        Lab = tk.Label(yearregion, text='年份')
        Lab.grid(row=0, column=0)
        self.year = tk.Entry(yearregion)
        self.year.grid(row=0, column=1, columnspan=2)
        R1 = tk.Radiobutton(yearregion, text='之前', variable=self.yeardirection, value='<')
        R1.grid(row=1, column=0)
        R2 = tk.Radiobutton(yearregion, text='当年', variable=self.yeardirection, value='=')
        R2.grid(row=1, column=1)
        R3 = tk.Radiobutton(yearregion, text='之后', variable=self.yeardirection, value='>')
        R3.grid(row=1, column=2)
        
        
    def _create_outputfileentry(self):
        # 建立输出文件名输入框
        self.fileentry = dict()
        self.outputfileframe = tk.Frame(self)
        self.outputfileframe.grid(row=1, column=1)
        Lab = tk.Label(self.outputfileframe, text='工作目录')
        Lab.grid(row=0, column=0)
        wkentry = tk.StringVar()
        wkentry.set('')
        self.fileentry['wkdir'] = tk.Entry(self.outputfileframe, textvariable=wkentry)
        self.fileentry['wkdir'].grid(row=0, column=1)
        Lab1 = tk.Label(self.outputfileframe, text='作者ID-文献ID文件')
        Lab1.grid(row=1, column=0)
        Lab2 = tk.Label(self.outputfileframe, text='文献ID-单位')
        Lab2.grid(row=2, column=0)
        Lab3 = tk.Label(self.outputfileframe, text='文献基本信息')
        Lab3.grid(row=3, column=0)
        entry1 = tk.StringVar()
        entry1.set('author_doc.csv')
        self.fileentry['author_doc'] = tk.Entry(self.outputfileframe, textvariable=entry1)
        self.fileentry['author_doc'].grid(row=1, column=1)
        entry2 = tk.StringVar()
        entry2.set('doc_affiliation.csv')
        self.fileentry['doc_affiliation'] = tk.Entry(self.outputfileframe, textvariable=entry2)
        self.fileentry['doc_affiliation'].grid(row=2, column=1)
        entry3 = tk.StringVar()
        entry3.set('document.csv')
        self.fileentry['doc'] = tk.Entry(self.outputfileframe, textvariable=entry3)
        self.fileentry['doc'].grid(row=3, column=1)

    def _create_runbutton(self):
        # 建立运行按钮
        self.runbuttonframe = tk.Frame(self)
        self.runbuttonframe.grid(row=1, column=2)
        self.runbutton = tk.Button(self.runbuttonframe, text='运行', command=self._run)
        self.runbutton.pack(expand=True, anchor=tk.CENTER)
        

    def _textbox(self, label, width, textwrap, row, column):
        # make the text box with x and y scrollbar
        frame = tk.Frame(self)
        frame.grid(row=row, column=column)
        thelabel = tk.Label(frame, text=label)
        thelabel.grid(row=0, column=0)
        thetext = tk.Text(
            frame,
            borderwidth=3,
            width=width,
            relief=tk.SUNKEN,
            wrap=textwrap
        )
        thetext.grid(row=1, column=0)
        thescrollx = tk.Scrollbar(
            frame,
            command=thetext.xview,
            orient=tk.HORIZONTAL
        )
        thescrollx.grid(
            row=2, column=0, sticky=tk.W + tk.E + tk.N + tk.S
        )
        thetext.configure(xscrollcommand=thescrollx.set)
        thescrolly = tk.Scrollbar(
            frame,
            command=thetext.yview,
            orient=tk.VERTICAL
        )
        thescrolly.grid(
            row=1, column=1, sticky=tk.W + tk.E + tk.N + tk.S
        )
        thetext.configure(yscrollcommand=thescrolly.set)
        return thetext
    
    def _run(self):
        # 保存输入信息
        self.inputinfo['api_key'] = self.api_key_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.inputinfo['affiliation_id'] = self.affiliation_id_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.inputinfo['author_id'] = self.author_id_textbox.get(1.0, tk.END).rstrip().split('\n')
        self.inputinfo['year'] = self.year.get()
        self.inputinfo['yeardirection'] = self.yeardirection.get().rstrip()
        self.inputinfo['filepath_wkdir'] = self.fileentry['wkdir'].get()
        self.inputinfo['filepath_author_doc'] = self.fileentry['author_doc'].get()
        self.inputinfo['filepath_doc_affiliation'] = self.fileentry['doc_affiliation'].get()
        self.inputinfo['filepath_doc'] = self.fileentry['doc'].get()
        
        from time import sleep
        message = tk.StringVar()
        
        one = tk.Toplevel()
        tmp = tk.Message(one, textvariable=message)
        tmp.pack()
        samplefunc()
        message.set(sys.stdout.readlines())
        tmp.update()
        
        # 下载文献信息
#        fetched = fetch_doc(
#            self.inputinfo['affiliation_id'],
#            self.inputinfo['author_id'],
#            self.inputinfo['year'],
#            self.inputinfo['yeardirection'],
#            self.inputinfo['api_key']
#        )
#        fetched['author_doc'].to_csv(
#            os.path.join(self.inputinfo['filepath_wkdir'], self.inputinfo['filepath_author_doc']),
#            index=False
#        )
#        fetched['document'].to_csv(
#            os.path.join(self.inputinfo['filepath_wkdir'], self.inputinfo['filepath_doc']),
#            index=False
#        )
#        fetched['doc_affiliation'].to_csv(
#            os.path.join(self.inputinfo['filepath_wkdir'], self.inputinfo['filepath_doc_affiliation']),
#            index=False
#        )


logger = logging.getLogger('one')
logger.addHandler(logging.StreamHandler())
def samplefunc():
    for x in range(10):
        sleep(1)
        logger.info('Hi, there! ' + '{0}'.format(x))

# ------------------
# EOF
# ------------------