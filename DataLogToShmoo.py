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
