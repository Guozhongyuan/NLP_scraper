from bs4 import BeautifulSoup
import numpy as np
import multiprocessing
import copy
from tqdm import tqdm
import requests
import pickle
import json


def get_url(time_0='2022-03-22', time_1='2022-03-23', pages=100):
    url_list = []
    for page in range(1, pages+1):
        url = f"https://reportapi.eastmoney.com/report/jg?cb=datatable6176985&pageSize=100&beginTime={time_0}&endTime={time_1}&pageNo={page}"
        url_list.append(url)
    return url_list

def get_report(url_list):
    query_list = []
    for i in tqdm(range(len(url_list))):
        url = url_list[i]
        res = requests.get(url)
        res_text = res.text
        res_text = res_text[17:-1]
        res_js = json.loads(res_text)
        if len(res_js['data'])==0:
            break
        query_list.extend(res_js['data'])
        # time.sleep(random.uniform(1,2))
    return query_list


def get_content(text_link):

    html = requests.get(text_link).content
    soup = BeautifulSoup(html, "lxml")

    # different classname
    # class_name = {
    #     '个股研报': 'stockzw_content',
    #     '行业研报': 'zw-content',
    #     '宏观研究': 'ctx-content',
    #     '盈利预测': '',
    #     '新股研报': 'stockzw_content',
    #     '策略报告': 'ctx-content',
    #     '券商晨报': 'zw-content',
    # }

    res = {
        'stockzw_content': soup.find('div', class_='stockzw_content'),
        'ctx-content': soup.find('div', class_='ctx-content'),
        'zw-content': soup.find('div', class_='zw-content'),
    }
    
    for key in res.keys():
        if res[key] != None:
            content = [i.text for i in res[key].find_all('p')]
            content = ''.join(content)
            content = content.replace('\u3000\u3000', '')
            content = content.replace('\u3000\u3000', '')
            content = content.replace('\r', '')
            content = content.replace(' ', '')
            return key, content

    return None, None


def process(query):
    try:
        encodeUrl = query['encodeUrl']
        content_url = f'https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={encodeUrl}'
        key, content = get_content(content_url)
        query['content_url'] = content_url
        query['key'] = key
        query['content'] = content
        return copy.deepcopy(query)
    except Exception:
        return []



if __name__ == '__main__':

    url_list = get_url(time_0='2020-04-15', time_1='2022-04-15', pages=2000)

    query_list = get_report(url_list)

    pool = multiprocessing.Pool(processes=16)

    pbar = tqdm(total=len(query_list))

    res_list = []

    def update(res):
        if res != []:
            res_list.append(res)
        pbar.update()

    for query in query_list:
        pool.apply_async(process, args=(query,), callback=update)

    pool.close()
    pool.join()

    with open('./files/eastmoney_hgyb.pkl', 'wb') as f:
        pickle.dump(res_list, f)