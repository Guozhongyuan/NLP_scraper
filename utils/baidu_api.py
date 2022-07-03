from aip import AipNlp
import json


class BaiduNLU():

    """[Baidu_nlu_api, more information here: https://cloud.baidu.com/doc/NLP/s/tk6z52b9z]
    """
    def __init__(self, config):
        """
        Args:
            config ([dict]): 
                config['APP_ID']
                config['API_KEY']
                config['SECRET_KEY']
        """
        self.client = AipNlp(config['APP_ID'], config['API_KEY'], config['SECRET_KEY'])
   

    def print_dic(self, dic):
        """[print and line feed]
        Args:
            dic ([dict]): return of baidu_api  
        """
        print(json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))


    def get_sentiment(self, content):
        """
        Args:
            content ([str])
        Returns:
            [dict]:
                "item": 
                    "Sentigent": 2, indicates the classification result of emotional polarity, [0, 1, 2]
                    "Confidence": 0.40, indicates the confidence of classification
                    "Positive_prob": 0.73, indicates the probability of belonging to the positive category
                    "Negative_prob": 0.27, indicates the probability of belonging to the negative category
        """
        dic = self.client.sentimentClassify(content)
        return dic


    def get_keyword(self, title, content):
        """
        Args:
            title ([str]): [title of news]
            content ([str]): [content of news]
        Returns:
            [dict]:
                "items":
                    "tag": Focus string
                    "score": Weight (value range 0 ~ 1)
        """
        dic = self.client.keyword(title, content)
        return dic


    def get_topic(self, title, content):
        """
        Args:
            title ([str]): [title of news]
            content ([str]): [content of news]
        Returns:
            [dict]:
                "item":
                    + "lv1_tag_list": array of objects Primary classification results
                    + "lv2_tag_list": array of objects Secondary classification results
                        ++ "score": float Corresponding score of category label, range 0-1
                        ++ "tag": string Category label
        """
        dic = self.client.topic(title, content)
        return dic


    def get_summary(self, title, content, maxSummaryLen=100):
        """
        Args:
            title ([str]): [title of news]
            content ([str]): [content of news]
            maxSummaryLen (int, optional): [max length of return str, 200-400 is better.]
        Returns:
            [dict]:
                "summary":
        """
        options = {}
        options["title"] = title
        dic = self.client.newsSummary(content, maxSummaryLen, options)
        return dic

