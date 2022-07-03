from scrapers import Baidu

if __name__ == "__main__":

    config = dict()
    config['scraper_api_key'] = '1f8bda8aecca20d44570369e28babdf4'
    # 1f8bda8aecca20d44570369e28babdf4  # unknow
    # a16f3d5ee4d665788e236247f9745570  # google 400 used
    # 75eb0cefb0bebddf6eb481b60353d525  # github 600 used
    # 2d7b42ec7382806b9d502668992bfc59  # foxmail 5000 free

    Baidu(config).run()
