# -*- coding: utf-8 -*-
"""
Ver 1.0.1
程式整合簡化 (FORMAT + ASSIGN 的部分）

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
                    if format_flag == 1: line = re.sub(r'\\', ' ', line)
                    tmpstr = tmpstr + line
                tmpstr = re.sub(r'\;', ' ', tmpstr)
                if format_flag == 1: tmparr = tmpstr.split(' ')
                if format_flag == 2: tmparr = tmpstr split(',')
                ch_list_name = tmparr
                if format_flag == 1:
                    del tmparr[0]
                    tmparr[:] = [value for i, value in enumerate(tmparr) if value != '']
                for key in tmparr:
                    if (format_flag == 2) and (key.strip() == ''):
                        continue
                    if key in DPINLIST:
                        channel_list = channel_list + str(DPINLIST[key][0]) + ","
                    elif key in LCDPINLIST:
                        channel_list = channel_list + str(LCDPINLIST[key][0]) + ","
                    else:
                        closest_key = min(DPINLIST.key(), key = lambda k: Levenshtein.distance(k, key))
                        channel_list = channel_list + str(DPINLIST[closest_key][0]) + ","
                        logger.warning(f"There is no {key} in Socket.tdl, closest key is {closest_key}, check it pls")
                    channel_list = channel_list.rstrip(',')
                    format_flag = 0

                if 'EABLE' in line:
                    tmparr = line.split(' ')
                    TN = '/' + re.sub(r"[S;]", "", tmparr[1]) + ' ! '
                    StartFlag = 1
                    if HeaderFlag == 0: header(file_name, fout, channel_list, ch_list_name); HeaderFlag = HeaderFlag + 1
                    continue
                if 'ENDTEST' in line:
                    StartFlag = 0
                    OutStr = "{:<10}{:<15}{}{}{:>10} \n" .format("SP:", "NOP", TN, pattern, 'SP Label')
                    fout.write(OutStr)
                    fout.write("END\n")
                if StartFlag == 1:
                    pattern = line
                    if re.search(r'\bREPEAT\b', pattern):
                        rpt_cnt = int(re.sub(r'\D', '', pattern.strip().split(' ')[1]))
                        continue
                    elif re.search(r'\bENDREPT\b', pattern):
                        rpt_cnt = 0
                        continue
                    try:
                        numcheck = re.search(r'/\*\s*(.*?)\s*\*/', pattern).group(1)
                    except:
                        logger.error(f"There is new rule in {file_name}, contact author pls")
                    if LINE == 1: OutStr = "{:<10}{:<15}{}{}{:<5}{:<10} \n" .format("ST:", "NOP", TN, pattern, " ", str(LINE))
                    elif rpt_cnt: OutStr = "{:<10}{:<15}{}{}{:<5}{:<10} \n" .format(" "  , "IDXI " + str(rpt_cnt), TN, pattern, " ", str(LINE) + " Repeat " + str(rpt_cnt + 1))
                    else        : OutStr = "{:<10}{:<15}{}{}{:<5}{:<10} \n" .format(" "  , "NOP", TN, pattern, " ", str(LINE))
                    if int(numcheck) != LINE:
                        new_rule += 1 #should add warning log
                        logger.debug(f"{pattern}")
                    LINE += 1
                    if rpt_cnt: LINE = LINE + rpt_cnt
                    fout.write(OutStr)
    fout.close()
    if new_rule:
        logger.warning(f"There is new rule in {file_name}, contact author pls")

def vector_trans(file_source_path, DPINLIST, LCDPINLIST, file_target_path = "target"):
    now_path = os.path.dirname(file_source_path).replace('\\', '/')
    folder = now_path + '/' + file_target_path
    if not os.path.exists(folder):
        os.makedirs(folder)
    if file_source_path.endswith('.tstl2'):
        tstl2_vector(file_source_path, folder, DPINLIST, LCDPINLIST)
    else:
        logger.error(f"There is no convert rule for {file_source_path} now, contact author pls")

def header(file_name, fout, channel_list, ch_list_name):
    file_name = file_name.upper()
    file_name = re.sub(r'_', '.', file_name)
    fout.write("LPAT    " + file_name + "\n") 
    fout.write("MODE    QUARTER\n")
    fout.write("RDX 10\n")
    fout.write("CHANNEL LCDEXPAND   " + channel_list + "\n")
    fout.write("CFPF\n")
    fout.write("LOC 0\n")
    fout.write(';---------------------------------------------------------------------------------------\n')
    max_length = len(max(ch_list_name, key = len))
    tmparr = [""] * max_length
    for i in range(max_length):
        for j in range(0, len(ch_list_name)):
            if i < len(ch_list_name[j]):
                tmparr[i] = tmparr[i] + ch_list_name[j][i]
            else:
                tmparr[i] = tmparr[i] + " "
        fout.write("\;{:<29} {}\n" .format(" ", tmparr[i]))
    fout.write(';---------------------------------------------------------------------------------------\n')

def socket_input(file_source_path = Socket.tdl):
    file_source_path = file_source_path.replace('\\', '/')
    DPINLIST = defaultdict(list)
    LCDPINLIST = defaultdict(list)
    try:
        with open(file_source_path, 'r', encoding = 'utf-8') as f: #大檔案儲存
            for line in f:
                match = re.search(r'(\w+)\s*\.define\s*(.*?)\)', line)
                if match:
                    dpin    = match.group(1)
                    channel = match.group(2)
                    channel = channel.split(",")
                    channel = [re.sub(r'\D', '', item) for item in channel]
                if re.search(r'\bDPIN\b', line):
                    if dpin in DPINLIST:
                        logger.warning(f"There is duplicate DPIN {dpin} in DPIN define")
                        # should add warning log
                    else:
                        DPINLIST[dpin] = channel
                if re.search(r'\bLCDPIN\b', line):
                    if dpin in LCDPINLIST:
                        logger.warning(f"There is duplicate LCDPIN {dpin} in LCDPIN define")
                        # should add warning log
                    else:
                        LCDPINLIST[dpin] = channel
            f.close()
    except:
        logger.error(f"There is no Socket.tdl, now path:{file_source_path}")
    return DPINLIST, LCDPINLIST

#################### main program ####################
if __name__ == '__main__':
    logger = setup_logger(name = "CvtModule", log_file = "app.log", level = "DEBUG")

    #script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(os.path.realpath(sys.arvg[0])) # 修正打包後的路徑問題
    source_dir = script_dir + '/pattern/'
    target_dir = script_dir + '/pattern/target/'

    DPINLIST, LCDPINLIST = socket_input(script_dir + '/Socket.tdl')

    all_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 把完整的檔案路徑加入 list
            if not (file.endswith('.tdl') or file.endswith('.asc')):
                all_files.append(os.path.join(root, file))
    for file_path in all_files:
        logger.info(f"Processing file:{file_path}")
        print(f"Processing file:{file_path}")
        vector_trans(file_path, DPINLIST, LCDPINLIST)