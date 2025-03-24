# -*- coding: utf-8 -*-
"""
ver 1.0
feature: trans datalog to shmoo

"""
from collections import defaultdic
import sys
import os
import re
import json
from logging_config import setup_logger
from NDLogLib import ND4Cap

class ShmooJSON:
    def __init__(self, file_path = "shmoo_set.json"):
        self.file_path = file_path
        self.data = self._load_json()

    def _load_json(self):
        """ 讀取 JSON 文件內容 """
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"File not found:{self.file_path}")
            return {}
        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            return {}
    def get_info(self, func_name):
        """ 查對應名稱的 shmoo 設定 """
        if self.data[0].get(func_name, {}):
            return self.data[0].get(func_name, {})
        else:
            logger.info(f"Setting not found:{func_name}")

    def json_gen(self, source_file):
        start_flag = False
        shmoo_cnt = 0
        json_dict = defaultdict(dict)
        header_arr = x_arr = y_arr = []
        with open(source_file, 'r', encoding='utf-8') as f: #大檔案儲存
            for line in f:
                line = line.strip() #replace space and \n at top&end
                if "SHMOO START" in line:
                    start_flag = True
                    shmoo_cnt += 1
                elif "SHMOO END" in line:
                    start_flag = False
                    func_name = 'Name' + str(shmoo_cnt)
                    json_dict[func_name]["header"] = header_arr
                    json_dict[func_name]["x"] = x_arr
                    json_dict[func_name]["y"] = y_arr
                if start_flag:
                    matches = re.findall(r'\s*(Start)\s*(Stop)\s*(Step)\s*(Org)\s*(Unit)\s*(Swp)\s*(Param)\s*(Comment)\s*', line)
                    #header_arr = re.search(r'\s*Stop\s*', line)
                    if matches:
                        header_arr = [item for match in matches for item in match]
                        line = f.readline().strip()
                        x_arr = [x for x in line.split(' ') if x != '']
                        if len(x_arr) < 9:
                            x_arr.append("")
                        line = f.readline().strip()
                        y_arr = [x for x in line.split(' ') if x != '']
                        if len(y_arr) < 9:
                            y_arr.append("")
        fout = open(self.file_path, "w+")
        fout.write("[\n")
        fout.write("    {\n")
        formatted_str = additional_str = tmp_str = ""
        for index, key in enumerate(json_dict):
            formatted_str = "{:8}\"{}\": {}".format(' ', key, "{\n")
            fout.write(formatted_str)
            formatted_str = "{:12}{}: {}".format(' ', "\"header\"", "[\n")
            fout.write(formatted_str)
            formatted_str = "{:16}{}{}".format(' ', "\"\"", ",\n")
            fout.write(formatted_str)
            for i in range(7):
                formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["header"][i], ",\n") ; fout.write(formatted_str)
            formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["header"][i+1], "\n") ; fout.write(formatted_str)
            formatted_str = "{:12}{}{}".format(' ', '', "],\n") ; fout.write(formatted_str)
            formatted_str = "{:12}{}: {}".format(' ', "\"shmoo_x\"", "[\n"); fout.write(formatted_str)
            for i in range(1, 8):
                formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["x"][i], ",\n") ; fout.write(formatted_str)
            formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["x"][i+1], "\n") ; fout.write(formatted_str)
            formatted_str = "{:12}{}{}".format(' ', '', "],\n") ; fout.write(formatted_str)
            formatted_str = "{:12}{}: {}".format(' ', "\"shmoo_y\"", "[\n"); fout.write(formatted_str)
            for i in range(1, 8):
                formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["y"][i], ",\n") ; fout.write(formatted_str)
            formatted_str = "{:16}\"{}\"{}".format(' ', json_dict[key]["y"][i+1], "\n") ; fout.write(formatted_str)
            formatted_str = "{:12}{}{}".format(' ', '', "]\n") ; fout.write(formatted_str)
            if index < len(json_dict) - 1:
                formatted_str = "{:8}{}{}".format(' ', '', "},\n") ; fout.write(formatted_str)
                tmp_str = "{:8}\"{}\": {}\n{:12}\"{}\"\n{:8}{}\n".format(' ', "shmoo" + str(index), "[", ' ', "other info", ' ', "],")
            else:
                formatted_str = "{:8}{}{}".format(' ', '', "}\n") ; fout.write(formatted_str)
                tmp_str = "{:8}\"{}\": {}\n{:12}\"{}\"\n{:8}{}\n".format(' ', "shmoo" + str(index), "[", ' ', "other info", ' ', "]")
            additional_str += tmp_str
        formatted_str = "{:4}{}{}".format(' ', '', "},\n") ; fout.write(formatted_str)
        additional_str = "    {\n" + additional_str + "    }\n" ; fout.write(additional_str)
        fout.write("]\n")

###################### main ######################
if __name__=='__main__':
    logger = setup_logger(name = "DTS", log_file = "app.log", level = "DEBUG")
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    #source_dir = script_dir + '/data/'
    #target_dir = script_dir + '/data/shmoo/'
    source_dir = os.path.join(script_dir, 'data')
    target_dir = os.path.join(script_dir, 'data', 'shmoo')

    
    all_files = []
    all_file_name = os.listdir(source_dir)
    all_file_name[:] = [file for file in all_file_name if file.endswith('.log')]
    cover_enable = True
    
    setting = ShmooJSON("shmoo_set.json") # 指定 shmoo 設定文件
    setting.json_gen("Test2.log")
    #a = setting.get_info("shm_isp_kvco_selr")["header"][1]
    
    '''
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 把完整的檔案路徑加入 list
            all_files.append(os.path.join(root,file))
    for file_path in all_files:
        logger.info(f"Processing file:{file_path}")
    '''
    for file in all_file_name:
        logger.info(f"Processing file:{file}")
        file_name = file[:-4]
        source_name = file_name + '.log'
        target_name = file_name + '_shmoo.log'
        yyds = ND4Cap(logger, cover_enable, source_dir, target_dir, source_name, target_name)
        yyds.shmoo_log_format(setting)
