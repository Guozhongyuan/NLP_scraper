# 1. convert from many txt files to one csv file

import os
from tqdm import tqdm
import csv

txts_path = "./save_stocks"

txt_paths = []
for root, dirs, files in os.walk(txts_path):
    for file in files:
        txt_paths.append(root + "/" + file)

path = txt_paths[0]
with open(path, "r", encoding='utf-8') as f:
    data = f.readlines()
    one = {}
    one['time'] = data[14].replace('\n', '')
    one['ticker_id'] = data[1].replace('\n', '')
    one['ticker_name'] = data[2].replace('\n', '')
    one['ticker_class'] = data[13].replace('\n', '')
    one['ticker_grade'] = [data[5].replace('\n', ''), data[6].replace('\n', '')]
    one['text_title'] = data[4].replace('\n', '')
    one['text_content'] = "".join(data[15:]).replace('\n', '').replace(' ', '').replace('\u3000\u3000', '')

temp = one['text_content']
# print(temp)
print(temp[0])