from bs4 import BeautifulSoup
import json
import multiprocessing
import copy
from tqdm import tqdm
import requests
import pickle


def get_url(time_0='2022-03-22', time_1='2022-03-23', pages=100):
    # 新股研报
    url_list = []
    for page in range(1, pages+1):
        url = f"https://reportapi.eastmoney.com/report/newStockList?cb=datatable9276010&pageSize=50&beginTime={time_0}&endTime={time_1}&pageNo={page}&fields=&qType=4&p={page}&pageNum={page}&pageNumber={page}"
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
    return query_list


def get_content(text_link):

    html = requests.get(text_link).content
    soup = BeautifulSoup(html, "lxml")

    res = soup.find('div', class_='newsContent')
    
    if res != None:
        content = [i.text for i in res.find_all('p')]
        content = ''.join(content)
        content = content.replace('\u3000\u3000', '')
        content = content.replace('\u3000\u3000', '')
        content = content.replace('\r', '')
        content = content.replace('\n', '')
        content = content.replace(' ', '')
        return content

    return None


def process(query):
    try:
        infoCode = query['infoCode']
        content_url = f'https://data.eastmoney.com/report/info/{infoCode}.html'
        content = get_content(content_url)
        query['content_url'] = content_url
        query['content'] = content
        if content != None:
            return copy.deepcopy(query)
        else:
            return None
    except Exception:
        return None



if __name__ == '__main__':

    url_list = get_url(time_0='2020-04-15', time_1='2022-04-15', pages=5000)

    query_list = get_report(url_list)

    pool = multiprocessing.Pool(processes=16)

    pbar = tqdm(total=len(query_list))

    res_list = []

    def update(res):
        if res != None:
            res_list.append(res)
        pbar.update()

    for query in query_list:
        pool.apply_async(process, args=(query,), callback=update)

    pool.close()
    pool.join()

    with open('./files/eastmoney_xgyb.pkl', 'wb') as f:
        pickle.dump(res_list, f)