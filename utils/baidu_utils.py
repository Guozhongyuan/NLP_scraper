import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import time
import re


def request_by_api(url, api_key, NUM_RETRIES=3):
    '''
        input: url
        output: response
    '''
    params = {'api_key': api_key, 'url': url}
    response = ''
    for _ in range(NUM_RETRIES):
        try:
            response = requests.get(url='http://api.scraperapi.com/', params=urlencode(params))
            if response.status_code in [200, 404]:
                # escape for loop if the API returns a successful response
                break
        except requests.exceptions.ConnectionError as err:
            print('scraperapi: ', err)
            response = ''
    return response


def get_baidu_pedia(query, api_key, NUM_RETRIES=3):
    '''
        function: BaiduPedia accurate query
        input: queryStr ( Only the query included in BaiduPedia entries can be queried )
        output: BaiduPedia content
    '''
    url = f'https://baike.baidu.com/item/{query}'
    
    response = request_by_api(url, api_key, NUM_RETRIES)
    if response != '':
        baidu_pedia = BeautifulSoup(response.content, 'html')
        para = baidu_pedia.find_all('div', class_="para")
        if len(para):
            text = []
            for i in para:  # 段落内容
                info = i.get_text()
                text.append(info)
            summary = text[0].replace("\n", "").replace("\xa0", "")
            content = ''.join(text[1:])
            content = content.replace("\n", "").replace("\xa0", "")
        else:
            summary = ""
            content = ""
        return url, summary, content

    return "", "", ""


def get_baidu_pedia_two_step(query, api_key, NUM_RETRIES=3):
    '''
        function: Baidu fuzzy query, first search in Baidu, then get the chinese name of company, and then search in BaiduPedia
        input: queryStr
        output: BaiduPedia content
    '''
    url = f'https://www.baidu.com/baidu?tn=monline_7_dg&ie=utf-8&wd={query}+公司+百科'
    response = request_by_api(url, api_key, NUM_RETRIES)
    if response != '':
        html_doc = response.text
        page = BeautifulSoup(html_doc, 'html')
        div = page.findAll(name='span', attrs={'class': 'c-tools new-pmd'})

        for element in div:
            time.sleep(0.5)
            info = element.attrs['data-tools']
            company_chinese_name = re.findall(r"title:'.*',url", info)[0]
            if '百度百科' in company_chinese_name:
                company_chinese_name = company_chinese_name[7:-12]
                url, summary, content = get_baidu_pedia(company_chinese_name, api_key, NUM_RETRIES)
                return company_chinese_name, url, summary, content

    return "", "", "", ""