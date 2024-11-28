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

    #################### collect data ####################
    def collect_data(self):
        multi_site         = defaultdict(list) # {DUT: [all_info]}
        self.die           = defaultdict(list) # {sample: [all_info]}
        self.die_xy        = defaultdict(list) # {coordinate: [all_info]}
        self.res           = defaultdict(list) # {"sample_item" : "result"}
        all_info           = []                # 0: datetime / 1: wafer / 2: sample / 3: DUT / 4: X / 5: Y / 6: BIN
        self.test_item_dic = defaultdict(list) # {Test Name: Test ID}
        self.dpin          = defaultdict(list) # {"sample_item" : "DPIN"}
        self.h_limit       = defaultdict(list) # {"sample_item" : "H Limit"}
        self.l_limit       = defaultdict(list) # {"sample_item" : "L Limit"}
        self.unit          = defaultdict(list) # {"sample_item" : "Unit"}
        dut_assign         = 1                 # result dut
        pre_dut_assign     = 1
        dut_context_flag   = 0
        cat_context_flag   = False
        test_item_flag     = False
        test_item_idx      = 0                 # FT has space line between result
        pj_context_flag    = False             # pjudge
        vj_context_flag    = False             # vjudge
        meas_context_flag  = False             # IM/VM

        with open(self.log_file, 'r', encoding = 'utf-8') as f: # 大檔案儲存
            for line in f:
                line = line.strip() # replace space and \n at top & end

                # datetime
                if 'ADVANTEST DataLog' in line:
                    all_info = [line.replace(' ADVANTEST DataLog: ', '').replace('*', '')]
                    multi_site        = {}
                    pj_context_flag   = False
                    vj_context_flag   = False
                    meas_context_flag = False
                    test_item_flag    = False
                    test_item_idx     = 0
                    continue
                elif 'Viewpoint DataLog' in line:
                    all_info = [line.replace(' Viewpoint DataLog: ', '').replace('*', '')]
                    multi_site        = {}
                    pj_context_flag   = False
                    vj_context_flag   = False
                    meas_context_flag = False
                    test_item_flag    = False
                    test_item_idx     = 0
                    continue

                # wafer / sample
                if 'Wafer Name' in line:
                    temp = [x for x in line.split(' ') if x != '']
                    all_info += [temp[3], int(temp[-1])]
                    continue

                # dut
                if ('DUT' in line) and ('X' in line) and ('Y' in line):
                    dut_context_flag   = True
                    continue
                elif (dut_context_flag):
                    temp = [x for x in line.split(' ') if x != '']
                    if (temp): # DUT X Y
                        dut_assign = int(temp[0]) # get dut no.
                        multi_site[dut_assign] = all_info + temp

                        coor_x = temp[1]
                        coor_y = temp[2]
                        coor_xy = 'X' + str(coor_x) + 'Y' + str(coor_y)
                        #self.die_xy[coor_xy] = all_info + temp
                        if self.die_xy[coor_xy] == []:
                            self.die_xy[coor_xy] = all_info + temp
                        
                        all_info[2] = all_info[2] - 1 # next: sample - 1
                    else: # space line
                        dut_context_flag = False
                    continue

                # bin
                if ('DUT :' in line) and (not cat_context_flag):
                    cat_context_flag = True
                    temp = [x for x in line.split(' ') if x != '']
                    dut_assign = int(temp[-1]) # get dut no.
                elif ('Category' in line) and cat_context_flag:
                    temp = [x for x in line.split(' ') if x != '']
                    try:
                        BIN = int(temp[-1]) - 1 # bin - 1
                    except:
                        BIN = 0
                    if dut_assign in multi_site.key(): # always max cat
                        sample_info = multi_site[dut_assign]
                        #self.die[sample_info[2]] = sample_info + [BIN]

                        coor_x = sample_info[4]
                        coor_y = sample_info[5]
                        coor_xy = 'X' + str(coor_x) + 'Y' + str(coor_y)
                        #if (len(self.die[self.die_xy[coor_xy][2]]) != 7) and (len(self.die[self.die_xy[coor_xy][2]]) != 0):
                        if len(self.die[self.die_xy[coor_xy][2]]) != 0 and self.cover_enable == True:
                            self.die[self.die_xy[coor_xy][2]][6] = BIN
                        else:
                            self.die[sample_info[2]] = sample_info + [BIN]

                    continue
                elif (line == '') and cat_context_flag:
                    cat_context_flag = False
                    continue

                # judge result
                if line[0:10] == '**********': # 加速判定
                    test_item_idx = 0
                    test_id = line.split('[')[1].split(']')[0] # 抓測試項編號
                    test_id = int(test_id[5:]) # "Test 1234" -> 1234
                    item = line.split('"')[1]
                    # if item not in self.test_item_dic.keys(): self.test_item_dic.update(dict(zip(str(item), test_id)))
                    temp_arr1 = [test_id,]
                    temp_arr2 = [item,]
                    if ('] IM' in line) or ('] VM' in line):
                        #self.test_item_dic.update(dict(zip(temp_arr1, temp_arr2)))
                        pass
                    else:
                        self.test_item_dic.update(dict(zip(temp_arr1, temp_arr2)))
                    if (1):
                    #if (item in self.test_items.keys()):
                        # 測項數據起始
                        if ('] FT FAIL' in line) or ('] FT PASS' in line): # pjudge
                            pj_context_flag = True
                            vj_context_flag = False
                            meas_context_flag = False
                            test_item_flag = True
                            # for single site
                            sample_info = multi_site[dut_assign]
                            if self.cover_enable == False:
                                label = str(sample_info[2]) + '_' + str(test_id) # sample_item
                            elif self.cover_enable == True:
                                label = ""
                                coor_xy = 'X' + str(sample_info[4]) + 'Y' + str(sample_info[5])
                                temp_arr = self.die_xy[coor_xy]
                                label = str(temp_arr[2]) + '_' + str(test_id)
                            if ('PASS' in line)  : self.res[label] = 0 # pat pass
                            elif ('FAIL' in line): self.res[label] = 1 # pat fail
                            temp_arr1 = [test_id,]
                            temp_arr2 = [0,]
                            temp_arr3 = ['',]
                            self.dpin.update(dict(zip(temp_arr1, temp_arr3)))
                            self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            temp_arr2 = ['',]
                            self.unit.update(dict(zip(temp_arr1, temp_arr2)))
                        elif ('] VM ' in line) or ('] IM ' in line): # VM/IM
                            # V04
                            pj_context_flag = False
                            vj_context_flag = False
                            meas_context_flag = True
                            test_item_flag = True
                            pass
                        else: # vjudge
                            pj_context_flag = False
                            vj_context_flag = True
                            meas_context_flag = False
                            test_item_flag = True
                    else: # 測項跳過
                        pj_context_flag = False
                        vj_context_flag = False
                        meas_context_flag = False
                        test_item_flag = False
                elif (pj_context_flag) and (line[0:6] == 'DUT   '):
                    test_item_idx = 1 # pjudge start
                    temp = [x for x in line.split(' ') if x != '']
                    dut_assign = int(temp[-1]) # get dut no.
                elif (vj_context_flag) and (line[0:6] == 'TestID'):
                    test_item_idx = 1 # vjudge start
                elif (meas_context_flag) and (line[0:6] == 'TestID'):
                    test_item_idx = 1 # IM/VM start
                elif (not test_item_flag) or (test_item_idx == 0):
                    continue
                elif (line == ''):
                    pre_dut_assign = 1
                    test_item_idx = 0
                    continue
                elif (pj_context_flag): # pjudge
                    sample_info = multi_site[dut_assign]
                    if self.cover_enable == False:
                        label = str(sample_info[2]) + '_' + str(test_id) # sample_item
                    elif self.cover_enable == True:
                        label = ""
                        coor_xy = 'X' + str(sample_info[4]) + 'Y' + str(sample_info[5])
                        temp_arr = self.die_xy[coor_xy]
                        label = str(temp_arr[2]) + '_' + str(test_id)
                    temp = [x for x in line.split(' ') if x != '']
                    if (temp[0] == 'PASS'):
                        self.res[label] = 0 # pat pass
                        test_item_idx += 1
                    elif (temp):
                        self.res[label] = 1 # pat fail
                        test_item_idx += 1
                elif (vj_context_flag): # vjudge
                    temp = [x for x in line.split(' ') if x != '']
                    dut_assign = int(temp[-1]) # get dut no.
                    sample_info = multi_site[dut_assign]

                    temp_arr1 = [test_id,]
                    temp_arr2 = ['',]
                    self.dpin.update(dict(zip(temp_arr1, temp_arr2)))

                    if self.cover_enable == False:
                        label = str(sample_info[2]) + '_' + str(test_id) # sample_item
                    elif self.cover_enable == True:
                        label = ""
                        coor_xy = 'X' + str(sample_info[4]) + 'Y' + str(sample_info[5])
                        temp_arr = self.die_xy[coor_xy]
                        label = str(temp_arr[2]) + '_' + str(test_id)
                    temp = [x for x in line.split(' ') if x != '']
                    if ('FAIL' in temp[1]) or ('OVERFLOW' in temp[1]) or ('ERROR' in temp[1]):
                        #if 'OVERFLOW' or 'ERROR' in temp[1]: temp[2] = '9999'
                        self.res[label] = self.unit_transfer(temp[2])[0]
                        temp_arr1 = [test_id,]
                        temp_arr2 = [self.unit_transfer(temp[3])[0],]
                        self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[4])[0],]
                        self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[2])[1],]
                        self.unit.update(dict(zip(temp_arr1, temp_arr2)))
                    else: # PASS
                        self.res[label] = self.unit_transfer(temp[1])[0]
                        temp_arr1 = [test_id,]
                        if re.findall('\d+', temp[2]):
                            temp_arr2 = [self.unit_transfer(temp[2])[0],]
                            self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            temp_arr2 = [self.unit_transfer(temp[3])[0],]
                            self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        else: # spec: None
                            temp_arr2 = [temp[2],]
                            self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            temp_arr2 = [temp[3],]
                            self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[1])[1],]
                        self.unit.update(dict(zip(temp_arr1, temp_arr2)))
                    test_item_idx += 1
                elif (meas_context_flag): # IM/VM
                    temp = [x for x in line.split(' ') if x != '']
                    dut_assign = int(temp[-1]) # get dut no.
                    sample_info = multi_site[dut_assign]
                    if dut_assign != pre_dut_assign:
                        test_item_idx = 1
                        pre_dut_assign = dut_assign
                    pin_name = str(temp[-2])

                    test_id_ex = str(test_id) + '_' + str(test_item_idx)
                    temp_arr1 = [test_id_ex,]
                    temp_arr2 = [item,]
                    temp_arr3 = [pin_name,]
                    #if dut_assign == 1:
                    self.test_item_dic.update(dict(zip(temp_arr1, temp_arr2)))
                    self.dpin.update(dict(zip(temp_arr1, temp_arr3)))
                    if self.cover_enable == False:
                        label = str(sample_info[2]) + '_' + str(test_id_ex) # sample_item
                    elif self.cover_enable == True:
                        label = ""
                        coor_xy = 'X' + str(sample_info[4]) + 'Y' + str(sample_info[5])
                        temp_arr = self.die_xy[coor_xy]
                        label = str(temp_arr[2]) + '_' + str(test_id_ex)
                    if ('FAIL' in temp[1]) or ('OVERFLOW' in temp[1]) or ('ERROR' in temp[1]):
                        #if 'OVERFLOW' or 'ERROR' in temp[1]: temp[2] = '9999'
                        self.res[label] = self.unit_transfer(temp[2])[0]
                        temp_arr1 = [test_id_ex,]
                        temp_arr2 = [self.unit_transfer(temp[3])[0],]
                        self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[4])[0],]
                        self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[2])[1],]
                        self.unit.update(dict(zip(temp_arr1, temp_arr2)))
                    else: # PASS
                        self.res[label] = self.unit_transfer(temp[1])[0]
                        temp_arr1 = [test_id_ex,]
                        if re.findall('\d+', temp[2]):
                            temp_arr2 = [self.unit_transfer(temp[2])[0],]
                            self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            temp_arr2 = [self.unit_transfer(temp[3])[0],]
                            self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        else: # spec: None
                            temp_arr2 = [temp[2],]
                            self.h_limit.update(dict(zip(temp_arr1, temp_arr2)))
                            temp_arr2 = [temp[3],]
                            self.l_limit.update(dict(zip(temp_arr1, temp_arr2)))
                        temp_arr2 = [self.unit_transfer(temp[1])[1],]
                        self.unit.update(dict(zip(temp_arr1, temp_arr2)))
                    test_item_idx += 1

    """ group database and write csv """
    def write_csv(self):
        field = ['', 'TestTime', 'Wafer', 'Sample', 'DUT', 'X', 'Y', 'BIN']
        #samples = sorted(die.key()) # DUT chaos
        samples = self.die.keys()
        k_items = self.test_item_dic.keys()
        v_items = self.test_item_dic.value()
        with open(self.csv_file, 'w', newline = '') as csv_file: # CSV write
            field_names = ['', '', '', '', '', '', '', 'Test ID'] + [item for item in k_items]
            writer = csv.DictWriter(csv_file, field_names = field_names)
            writer.writeheader()
            field_names = ['', '', '', '', '', '', '', 'Test Name'] + [item for item in v_items]
            csv.writer(csv_file).writerow(field_names)
            #field_names = ['', '', '', '', '', '', '', 'DPIN']
            #csv.writer(csv_file).writerow(field_names)
            self.setting_arr_fill(csv_file, 'DPIN', self.dpin)
            self.setting_arr_fill(csv_file, 'Hlimit', self.h_limit)
            self.setting_arr_fill(csv_file, 'Llimit', self.l_limit)
            self.setting_arr_fill(csv_file, 'Unit', self.unit)
            field_names = field + [item for item in k_items]
            csv.writer(csv_file).writerow(field)
            writer = csv.DictWriter(csv_file, field_names = field_names)
            #writer.writeheader()
            shift_i = 0
            for i, sample in enumerate(samples):
                r = {}
                if int(self.die[sample][4]) < 0: # X < 0, fake data (XY - 99999)
                    shift_i += 1
                    continue
                for k_items, v_items in self.test_item_dic.items():
                    key = str(sample) + '_' + str(k_items) # recover key name
                    if key in self.res.keys():
                        name = field + [k_items]
                        value = [i - shift_i] + self.die[sample] + [self.res[key]]
                        r.update(dict(zip(name, value)))
                        self.res.pop(key) # delet row data, accelerate
                    elif sample in self.die.keys():
                        name = field
                        value = fieldvalue = [i - shift_i] + self.die[sample]
                        r.update(dict(zip(name, value))) # not delete, reused
                writer.writerow(r)
            csv_file.close()

    def setting_arr_fill(self, csv_file, title, target_dict):
        field = ['', '', '', '', '', '', '', title]
        r = {}
        for k_items, v_items in self.test_item_dic.items():
            #name = field + [v_item]
            name = field + [k_items]
            value = field + [target_dict[k_items]]
            r.update(dict(zip(name, value)))

        #field_names = field + [item for item in self.test_item_dic.values()]
        field_names = field + [item for item in self.test_item_dic.keys()]
        writer = csv.DictWriter(csv_file, field_names = field_names)
        writer.writerow(r)

""" main """
if __name__ == '__main__':
    start = time() # 計時
    file_time = 0
    file_last_time = start

    dir_path = os.path.dirname(os.path.realpath(__file__))
    in_dir_path = dir_path + "/IN/"
    out_dir_path = dir_path + "/OUT/"
    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)
    all_file_name = os.listdir(in_dir_path)

    cover_enable = True

    for file in all_file_name:
        #initial_par("all")
        file_name = file[:-4]
        #file_source = open(in_dir_path + file, 'r', encoding = 'UTF-8') # to avoid "encoding = cp950" issue
        #file_target = open(out_dir_path + file_name + '.csv', 'w')
        source_name = file_name + '.log'
        target_name = file_name + '.csv'

        yyds = ND4Cap(cover_enable, in_dir_path, out_dir_path, source_name, target_name)
        yyds.collect_data()
        yyds.write_csv()

        file_time_title = 'file_time:' + str(file)
        file_time = time()
        time_counter = format(file_time - file_last_time)
        file_last_time = file_time
        print('file_time {}: {:.2f} s'.format(file_time_title, float(time_counter)))
        Test = yyds.TEST
        print (TEST)
    end = time()
    time_counter = format(end - start)
    print('END {}: {:.2f} s'.format(__name, float(time_counter)))
    # input("Please press the Enter key to proceed") #systemp pause code
