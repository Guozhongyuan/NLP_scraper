import pandas as pd
from utils.baidu_utils import get_baidu_pedia_two_step
from jieba import analyse
import zhconv
import csv
from multiprocessing.pool import Pool


class Baidu():
    def __init__(self, config):
        self.stock_list = pd.read_csv('full_stock_list.csv')
        self.scraper_api_key = config['scraper_api_key']

    def scrape(self, stock):

        query = stock['Company Common Name']
        print(query)

        company_chinese_name, url, summary, text = get_baidu_pedia_two_step(query, self.scraper_api_key, NUM_RETRIES=3)

        if len(summary):

            company_name = zhconv.convert(company_chinese_name, 'zh-tw')
            summary = zhconv.convert(summary, 'zh-tw')
            keywords = analyse.tfidf(summary + text)
            keywords = [zhconv.convert(i, 'zh-tw') for i in keywords]

            save_list = [   stock['ICB Subsector code'],
                            stock['Ticker'],
                            company_name,
                            summary,
                            keywords]
            print(save_list)
            print(query, 'end')
            return save_list

        print(query, 'NONE')
        return []


    def run(self):
        stocks = self.stock_list
        a = stocks['ICB Subsector code']
        b = stocks['Ticker']
        c = stocks['Company Common Name']
        pool_dict_list = []
        for i in range(0, a.size): # a.size
            temp = {'ICB Subsector code': a[i],
                    'Ticker': b[i],
                    'Company Common Name': c[i]}
            pool_dict_list.append(temp)

        pool = Pool(processes=1)
        res = pool.map(self.scrape, pool_dict_list)
        
        with open("save.csv","a+", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for i in res:
                if i != []:
                    writer.writerow(i)
                    print(i)
