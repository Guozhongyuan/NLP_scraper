import requests
import csv
import json
import time
import random

headers = {
    'Cookie': '_T_WM=53629218447; XSRF-TOKEN=db4d17; WEIBOCN_FROM=1110006030; MLOGIN=0; M_WEIBOCN_PARAMS=fid%3D100103type%253D1%2526q%253D%2525E4%2525B8%252581%2525E7%25259C%25259F%26uicode%3D10000011',
    'Referer': 'https://m.weibo.cn/detail/4312409864846621',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
    'X-Requested-With': 'XMLHttpRequest'
}

# MicroBlog #stock# url
hostUrl = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D60%26q%3D%23%E8%82%A1%E7%A5%A8%23%26t%3D0&page_type=searchall"

def spider(page_num, hostUrl):

    if page_num:
        main_url = hostUrl + '&page=' + str(page_num)

    try:
        r = requests.get(url=main_url, headers=headers)
        r.raise_for_status()
    except Exception as e:
        print("微博爬取失败", e)
        return 0

    result_json = json.loads(r.content.decode('utf-8'))
    info_list = []
    for card in result_json['data']['cards']:
        info_dict_sub = {}
        if card.get("mblog"):
            info_dict_sub['attitudes_count'] = card['mblog']['attitudes_count']  # attitudes_count
            info_dict_sub['comments_count'] = card['mblog']['comments_count']  # comments_count
            info_dict_sub['reposts_count'] = card['mblog']['reposts_count']  # reposts_count

            time.sleep(random.randint(4, 6))
            info_commands_id = card['mblog']['id']
            info_commands_url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(info_commands_id, info_commands_id)
            try:
                r = requests.get(url=info_commands_url, headers=headers)
                r.raise_for_status()
            except Exception as e:
                print("评论爬取失败", e)
                return 0
            commands_json = json.loads(r.content.decode('utf-8'))
            commands_text = []
            if commands_json.get('data', 0):
                if commands_json['data'].get('data', 0):
                    commands_text = [commands_card['text'] for commands_card in commands_json['data']['data']]  # comments content
            info_dict_sub['commands_text'] = commands_text

            if page_num == 1:
                info_dict_sub['created_time'] = card['mblog']['created_at']  # created time
            elif '2021' not in card['mblog']['created_at']:
                info_dict_sub['created_time'] = card['mblog']['created_at']
            else:
                print("2022年微博爬取完毕")
                break

            # info_dict_sub['weibo_position'] = card['mblog']['weibo_position']  # Original or not

            if card['mblog'].get('raw_text'):
                info_dict_sub['raw_text'] = card['mblog']['raw_text']  # content
            else:
                info_dict_sub['raw_text'] = card['mblog']['text']

            # if card['mblog']['source'] == '':
            #     info_list_sub.append(None)
            # else:
            #     info_list_sub.append(card['mblog']['source'])

            time.sleep(random.randint(4, 6))

            info_list.append(info_dict_sub)
        else:
            continue

    return info_list


res = []
    
for i in range(1, 5+1):
    information = spider(i,hostUrl)
    res.append(information)
    print("page %s finished" % i)

