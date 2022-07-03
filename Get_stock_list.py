import pickle
import pandas as pd
from multiprocessing.pool import Pool
from utils.baidu_utils import get_baidu_pedia, get_baidu_pedia_two_step
import copy


class Baidu():
    def __init__(self, config):
        self.stock_list = config['stock_list']
        self.scraper_api_key = config['scraper_api_key']

    def scrape(self, stock):
        query = stock['ticker_name']
        summary = ""
        try:
            url, summary, content = get_baidu_pedia(query, self.scraper_api_key)
        # company_chinese_name, url, summary, content = get_baidu_pedia_two_step(query, self.scraper_api_key)
        except Exception as err:
            print(err)
        # print(query)
        if len(summary):
            stock['baike_summary'] = summary
            stock['baike_content'] = content
            stock['baike_url'] = url
            print(query, summary)
        else:
            print(query, 'NONE')
        return copy.deepcopy(stock)

    def run(self):
        stocks = self.stock_list
        pool = Pool(processes=4)
        res = pool.map(self.scrape, stocks)
        return res


if __name__ == '__main__':

    with open("./files/eastmoney_stocks_list.pkl","rb") as f:
        stocks = pickle.load(f)

    config = {
        'scraper_api_key': '2d7b42ec7382806b9d502668992bfc59',
        'stock_list': stocks,
    }

    baidu_pedia_scraper = Baidu(config)
    res = baidu_pedia_scraper.run()

    with open("./files/eastmoney_stocks_list_0451_1232.pkl", "wb") as f:
        pickle.dump(res, f)