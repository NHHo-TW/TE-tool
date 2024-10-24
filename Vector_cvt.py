# -*- coding: utf-8 -*-
"""
Ver 1.0.1
程式整合簡化 （FORMAT + ASSIGN 的部分）

Ver 1.0.0
Beta, 支援 tstl2 檔案
自動比對最接近的 pin name
目前僅支援比對 DPIN → LCDPIN → DPIN(closest)
"""

from collections import defaultdict
import sys
import os
import re
import Levenshtein

from logging_config import setup_logger

def tstl2_vector(file_source_path, file_target_path, DPINLIST, LCDPINLIST):
    path_list = file_source_path.replace('\\','/').split('/')
    file_name = path_list[-1][0:-6] # .tstl2
    file_name = re.sub(r'\W', '_', file_name)
    target_file = file_target_path + '/' + file_name + '.acs'
    fout = open(target_file, "w+")
    LINE = 1 ; new_rule = 0 ; rpt_cnt = 0
    TN = "T1" ; pattern = ""
    StartFlag = 0 ; HeaderFlag = 0 ; format_flag = 0
    with open(file_source_path, 'r', encoding = 'utf-8') as f: #大檔案儲存
        for line in f:
            line = line.strip() # replace space and \n at top&end
            if (line[:2] == '//' or line == ''): continue
            if ('FORMAT' in line) or ('ASSIGN' in line)：
                channel_list = ""
                if 'FORMAT' in line: format_flag = 1
                if 'ASSIGN' in line: format_flag = 2
                if format_flag == 1: tmpstr = re.sub(r'\\', ' ', line)
                if format_flag == 2: tmpstr = re.sub(r'ASSIGN', ' ', line).strip()
                while ';' not in line:
                    line = f.readline()
                    line = line.strip()
