
''' Reference
1. [example code](https://console.cloud.tencent.com/api/explorer?Product=nlp&Version=2019-04-08&Action=TextClassification&SignVersion=)
2. [Tecent ID and KEY](https://console.cloud.tencent.com/cam/capi)
3. [Tecent nlu document](https://cloud.tencent.com/document/product/271/35496) limit 20/second
4. [Tecent sdk document](https://cloud.tencent.com/document/sdk/Python)
5. 
'''

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models


class TecentNLU():

    def __init__(self, config):
        cred = credential.Credential(config['SecretId'], config['SecretKey'])
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)
        
    def get_sentiment(self, text, flag=4, mode='2class'):
        resp = None
        try:
            req = models.SentimentAnalysisRequest()
            params = {
                "Text": text,
                "Flag": flag,
                "Mode": mode,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.SentimentAnalysis(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_keywords(self, text, num=30):
        resp = None
        try:
            req = models.KeywordsExtractionRequest()
            params = {
            "Text": text,
            "Num": num,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.KeywordsExtraction(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_topic(self, text, flag=2):
        resp = None
        try:
            req = models.TextClassificationRequest()
            params = {
                "Text": text,
                "Flag": flag,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.TextClassification(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_summary(self, text, length=200):
        resp = None
        try:
            req = models.AutoSummarizationRequest()
            params = {
                "Text": text,
                "Length": length,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.AutoSummarization(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_word_similarity(self, src, target):
        resp = None
        try:
            req = models.WordSimilarityRequest()
            params = {
                "SrcWord": src,
                "TargetWord": target,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.WordSimilarity(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_word_vector(self, text):
        resp = None
        try:
            req = models.WordEmbeddingRequest()
            params = {
                "Text": text,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.WordEmbedding(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_text_similarity(self, src, targets):
        resp = None
        try:
            req = models.TextSimilarityRequest()
            params = {
                "SrcText": src,
                "TargetText": targets,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.TextSimilarity(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp

    def get_text_vector(self, text):
        resp = None
        try:
            req = models.SentenceEmbeddingRequest()
            params = {
                "Text": text,
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.SentenceEmbedding(req)
        except TencentCloudSDKException as err:
            print(err)
        return resp