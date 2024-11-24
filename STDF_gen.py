# -*- coding: utf-8 -*-
"""
V03 - 資料改用 TEST ID 作為對應輸出參考
    - 新增 cover_enable 功能
V04 - 新增 IM/VM 資料輸出
V05 - 修復 value 取值問題
    - 將單位轉換的函式改用字典完成
"""
from collections import defaultdict
import csv
import os
import re
from time import time

class ND4Cap():
    def __init__(self, cover_enable, path_in, path_out, log_file, csv_file):
        self.cover_enable = cover_enable
        self.path_in = path_in
        self.path_out = path_out
        self.log_file = self.path_in + '/' + log_file
        self.csv_file = self.path_out + '/' + csv_file
        self.TEST = 0 # for debug
    #################### unit transfer ####################
    def unit_transfer(self, val_str, prefix = ""):
        # 定義單位倍率字典
        self.unit_multiplier = {
            'G': 1e9, 'M': 1e6, 'K': 1e3, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12
        }
        self.unit_list = {
            'V', 'A', 'Hz', 'R', 'W', 'S'
        }

        try:
            # 處理 ERROR 狀況
            if '***' in val_str:
                return None, prefix
            # 判斷是否為整數
            if val_str.lstrip('.').isdigit():
                val = int(val_str)
                return val, prefix
            # 處理浮點數和單位
            val = None
            unit_str = ""
            for i in range(len(val_str) - 1, -1, -1):
                try:
                    val = float(val_str[:i+1])
                    unit_str = val_str[i+1:].strip()
                    break
                except ValueError:
                    continue
            # 使用單位倍率字典進行轉換
            if unit_str and unit_str[0] in self.unit_multiplier:
                val *= self.unit_multiplier[unit_str[0]]
                unit_str = unit_str[1:]
            # 自定義單位
            if prefix in self.unit_multiplier:
                val /= self.unit_multiplier[unit_str[0]]
                unit_str = prefix + unit_str
            return val, unit_str
        except Exception as e:
            print(f"Error processing val_str = {val_str}: {e}")
            return None, unit_str
