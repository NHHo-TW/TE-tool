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

        with open(source_file, 'r', encoding='utf-8') as f:
            header_arr, x_arr, y_arr = [], [], []

            for line in f:
                line = line.strip()

                if "SHMOO START" in line:
                    start_flag = True
                    shmoo_cnt += 1
                    header_arr, x_arr, y_arr = [], [], []  # Reset arrays

                elif "SHMOO END" in line:
                    start_flag = False
                    func_name = f"Name{shmoo_cnt}"
                    json_dict[func_name] = {
                        "header": header_arr,
                        "x": x_arr,
                        "y": y_arr
                    }

                elif start_flag:
                    match = re.match(r'^\s*(Start|Stop|Step|Org|Unit|Swp|Param|Comment)\s*', line)
                    if match:
                        header_arr = line.split()
                        next_line = f.readline().strip()
                        x_arr = next_line.split() if next_line else []
                        next_line = f.readline().strip()
                        y_arr = next_line.split() if next_line else []

        # Writing JSON output
        output_data = []
        for key, value in json_dict.items():
            output_data.append({
                key: {
                    "header": value["header"],
                    "shmoo_x": value["x"],
                    "shmoo_y": value["y"]
                }
            })
    
        output_data.append({"shmoo_meta": ["other info"]})

        with open(self.file_path, "w", encoding="utf-8") as fout:
            json.dump(output_data, fout, indent=4)

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
