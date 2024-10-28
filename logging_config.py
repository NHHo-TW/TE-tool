# -*- coding: utf-8 -*-
"""
Ver 1.0.0
Debug 用模組
"""

import logging

def setup_logger(name = None, level = logging.DEBUG, log_file = None):
    # 設定基本配置
    logging.basicConfig(
        level = level,
        format = '%(asctime)s - %(name)s - %(Levelname)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        filename = log_file,
        filemode = 'w'
    )

    if not log_file:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(Levelname)s - %(message)s'))
        logger.addHandler(console)
    
    return logger

def auto_set_logger():
    logger = setup_logger(name = "MyLogger", logfile = "app.log")
