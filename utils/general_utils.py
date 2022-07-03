import pymongo
import json
from collections import Counter
import re
import yaml
import logging
import psycopg2


def update_universe(config, currency=['USD']):
    """
    update the big_universe and sector_dict.json in the

    Args:
        config (dict): the configuration from config.yamlError
        currency (list, optional): list of currency, the range of stocks we want to scrape. Defaults to ['USD'].
    """
    logging.warning("updating the stock list and sector dict...")
    stock_db_collection = connect_to_mongodb(
            config['mongodb']['database'], config['stock_universe'], config['mongodb']['host'], config['mongodb']['ssl_ca_cert_path'])
    update_StockDB(stock_db_collection, config)
    update_sector_dict(stock_db_collection, currency)
    logging.warning("update completed")


def update_StockDB(stock_db_collection, config):
    """
    update the big_universe if any new stocks come to the stock_universe.

    Args:
        stock_db_collection (obj): the big_universe mongodb collection_name
        config (dict): the configuration for postgres, mongodb etc.
    """
    conn = psycopg2.connect(
        host=config['postgres']['host'],
        database=config['postgres']['database'],
        user=config['postgres']['user'],
        password=config['postgres']['password'])
    try:
        cur = conn.cursor()
        cur.execute('''
                    SELECT ticker, ticker_symbol, ticker_name, icb_code, currency_code
                    FROM public.universe
                    WHERE is_active = true AND icb_code != 'NA'
                    ''')
    except Exception:
        logging.error('failed to connect to the postgres database.')
        return
    
    res = cur.fetchall()
    for i in range(len(res)):
        if stock_db_collection.find_one({'_id':res[i][0]}):
            continue
        try:
            stock_db_collection.insert_one({
                '_id': res[i][0],
                'ticker_symbol': res[i][1],
                'ticker_name': res[i][2],
                'icb_code': res[i][3],
                'currency_code': res[i][4]
            })
        except Exception as e:
            logging.error(e.args)
    

# from mongodb NLP.StockDB get the newest stock list
def update_sector_dict(stock_db_collection, currency):
    """update resource/stocks/sector_dict.json

    Args:
        stock_db_collection (obj): The mongodb collection object that stock universe link to.
        currency (list, optional): The list of stocks we want for scraping..
    """
    filter = {
        'currency_code': {
            '$in': currency
        },
        'icb_code': {
            '$ne': None
        }
    }
    project = {
        'ticker_symbol': 1,
        'icb_code': 1
    }

    cursor = stock_db_collection.find(filter=filter, projection=project)
    sector_dict = {}
    for record in cursor:
        sector_dict[record['ticker_symbol']] = record['icb_code']
    with open('resource/stocks/sector_dict.json', 'w') as f:
        json.dump(sector_dict, f)

# read config.yaml and transform to a dict
def get_config():
    """
    get the settings from resource/config.yaml

    Returns:
        dict: the configuration dictionary
    """
    with open('config.yaml', 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            logging.error(exc)
    return config

def connect_to_mongodb(dbname, collection_name, host, ca_certs_path):
    """
    build connection to mongodb

    Args:
        dbname (str): the database name of mongodb
        collection_name (str): the collection name inside the database
        ca_certs_path (str): the file is under resource/could/

    Returns:
        obj: a mongo client object
    """
    myclient = pymongo.MongoClient(host=host, ssl=True, tlsCAFile=ca_certs_path)
    mydb = myclient[dbname]
    myCollection = mydb[collection_name]
    return myCollection


def get_stock_list():
    """
    get 556 stocks' symbols (AMZN)
    """
    return list(get_sector_dict().keys())

def get_sector_dict():
    """
    get each symbol's corresponding sector (AMZN -> 10101010)
    """
    with open('resource/stocks/sector_dict.json') as json_file:
        sector_dict = json.load(json_file)
    return sector_dict


def get_sector(ticker_list, sector_dict, threshold=0.666):
    """
    get one sector for majority tickers

    Args:
        ticker_list (list): the candidate tickers
        sector_dict (dict): ticker --> sector count
        threshold (float, optional): the threhold for how many stocks should be in the same sector. Defaults to 0.666.

    Returns:
        str: the sector code, none if no majority
    """
    sector_list = []
    for ticker in ticker_list:
        if ticker in sector_dict:
            sector_list.append(sector_dict[ticker])
    if len(sector_list) != 0:
        most_common = Counter(sector_list).most_common(1)
        if most_common[0][1] / len(sector_list) > threshold:
            sector = most_common[0][0]
            return sector
    return None


def get_sector_loose(ticker_list, sector_dict, trim=0, threshold=0.5):
    """
    this function will get 2,4,6,8 digits sector, the recursive function
    will only terminate when at least half of stocks are in the same sector

    Args:
        ticker_list (list): the candidate tickers
        sector_dict (dict): ticker --> sector count
        trim (int, optional): the digits we remove from the. Defaults to 0.
        threshold (float, optional): the threhold for how many stocks should be in the same sector. DefDefaults to 0.5.

    Returns:
        str: the sector code, none if no majority
    """
    # no common sector even expand to 2 digit industry code
    if trim == 8:
        return None

    sector_list = []
    div = 10**trim
    for ticker in ticker_list:
        if ticker in sector_dict:
            sector_list.append(int(sector_dict[ticker]) // div)

    # check if there is no ticker mentioned in the universe
    if len(sector_list) == 0:
        return None

    # get the common sector
    most_common = Counter(sector_list).most_common(1)
    if most_common[0][1] / len(sector_list) > threshold:
        sector = most_common[0][0]
        return sector
    else:
        return get_sector_loose(ticker_list, sector_dict, trim=trim+2)


def process_text(text):
    """
    use regex to remove stocks, links and make sure the text is long enough

    Args:
        text (str): the input text

    Returns:
        str: text without links and ticker symbols
    """
    ignore = False

    # using regex to filter out $AMZN or http, https links
    text = re.sub(r"\$[a-zA-Z]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"https?:\/\/[^ \n]*", "", text, flags=re.IGNORECASE)
    length = len(text.split())

    # remove all the tweets that only contain 5 or fewer words
    if length <= 5:
        ignore = True
    return text, ignore