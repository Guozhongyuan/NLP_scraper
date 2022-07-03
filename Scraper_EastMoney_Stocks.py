#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 22:59:25 2018
@author: lilong
https://github.com/TATlong/Research-report-Classification-system
"""

import os
import time
import time
import traceback
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ReportReptile:

    def __init__(self):
        self.filedir = "save"
        os.makedirs(self.filedir, exist_ok=True)
        self.phantomjs_path = "./phantomjs-2.1.1-windows/bin/phantomjs.exe"
        self.url = "https://data.eastmoney.com/report/stock.jshtml"   # origin url
        self.driverInit()

    def driverInit(self):
        """brower driver init"""
        self.driver = webdriver.PhantomJS(executable_path=self.phantomjs_path)
        # get init page
        self.driver.get(self.url)

    def get_page_num(self, num):
        """simulate mouse to click the next page"""

        # （1）locate to page choose position："stock_table_pager"
        element_page = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, "stock_table_pager")))

        # （2）get button "ipt"
        tr_options = element_page.find_element_by_class_name("ipt")

        # （3）fill in page num, and then click
        tr_options.clear()  # clear current page num
        tr_options.send_keys('{}'.format(str(num)))
        element_page.find_element_by_class_name("btn").click()

        # （4）must wait for fixed time
        time.sleep(10)

    def download_report(self, text_link, re_sum_info):

        text_tmp = "\n".join([str(s) for s in re_sum_info])

        # get content
        orihtml = requests.get(text_link).content
        soup = BeautifulSoup(orihtml, "lxml")

        # judge whether black page
        if soup.find('div', class_='stockzw_content') == None:
            return None

        page_con = []
        for a in soup.find('div', class_='stockzw_content').find_all('p'):
            page_con.append(str(a.text))

        file_path = os.path.join(self.filedir, '{}.txt'.format(str(re_sum_info[-1]) + "_" + str(re_sum_info[0])))
        with open(file_path, "w+", encoding="utf-8") as f:
            f.write(text_tmp+"\n".join(page_con))

    def clickUPData(self):

        print("simulate click to sort by date ...")
        element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "stock_table")))

        # first click
        data_options = element.find_elements_by_tag_name("thead")[0]
        data_options_1 = data_options.find_elements_by_xpath('//*[@id="stock_table"]/table/thead/tr/th[6]/a')[0]
        print(f"find：{data_options_1.text}")
        data_options_1.click()
        time.sleep(10)

        # second click
        data_options = element.find_elements_by_tag_name("thead")[0]
        data_options_2 = data_options.find_elements_by_xpath('//*[@id="stock_table"]/table/thead/tr/th[6]/a')[0]
        data_options_2.click()
        time.sleep(10)

    def getPageTest(self):
        element_table = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "stock_table")))
        tr_options = element_table.find_elements_by_tag_name("tr")
        for tr_option in tr_options:
            td_options = tr_option.find_elements_by_tag_name("td")
            re_sum_info = []
            for td_option in td_options:
                re_sum_info.append(td_option.text)
            print("page:", re_sum_info)

    def get_report_page(self, page_start, page_end):

        print("chrome webdriver start ...")
        for i in range(page_start, page_end + 1):
            try:
                print(f"----------- get page: {i}---------")

                self.get_page_num(i)
                element_table = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, "stock_table")))

                # get all "tr"
                tr_options = element_table.find_elements_by_tag_name("tr")

                # loop 'td'
                for tr_option in tr_options:
                    # get：idx、title、writer、writer's company、article num in a month、date
                    td_options = tr_option.find_elements_by_tag_name("td")  # locate at "td"
                    re_sum_info = []
                    for td_option in td_options:
                        re_sum_info.append(td_option.text)
                    print("page:", re_sum_info)

                    # get content
                    for i in range(len(td_options)):
                        if i == 4:  # td_options[4].find_elements_by_xpath(".//*[@href]")[0].get_attribute('href')
                            url_element = td_options[i]
                            if not url_element:
                                continue
                            # print('report title:', td_options[i].text)
                            link = url_element.find_elements_by_xpath(".//*[@href]")[0]
                            text_link = link.get_attribute('href')
                            self.download_report(text_link, re_sum_info)
                            break

            except Exception as e:
                info = traceback.format_exc()
                print(info)

        # close plantomjs driver
        self.driver.quit()

    def get_report_date(self, start_date, end_date):
        """ scrape by article date """

        # format time
        start_date = time.strptime(start_date, "%Y-%m-%d")
        end_date = time.strptime(end_date, "%Y-%m-%d")

        # sort, then scrape from ealiest time
        self.clickUPData()

        # # test use
        # self.getPageTest()

        # init page each time
        pageNum_init = 1
        FLAG = True
        while FLAG:
            self.get_page_num(pageNum_init)
            print(f"page: {pageNum_init}")
            try:
                element_table = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "stock_table")))
                tr_options = element_table.find_elements_by_tag_name("tr")

                # loop 'td'
                for tr_option in tr_options:
                    # get：idx、title、writer、writer's company、article num in a month、date
                    td_options = tr_option.find_elements_by_tag_name("td")  # locate at "td"
                    re_sum_info = []
                    for td_option in td_options:
                        re_sum_info.append(td_option.text)
                    print("page:", re_sum_info)
                    if not re_sum_info:
                        continue

                    # judge date
                    time_tmp = time.strptime(re_sum_info[-1], "%Y-%m-%d")
                    if time_tmp < start_date:
                        continue
                    elif time_tmp > end_date:
                        FLAG = False
                        break
                    else:
                        # get content
                        for i in range(len(td_options)):
                            if i == 1:
                                url_element = td_options[i]
                                if not url_element:
                                    continue
                                # print('report title:', td_options[i].text)
                                link = url_element.find_elements_by_xpath(".//*[@href]")[0]  # get the link
                                text_link = link.get_attribute('href')
                                self.download_report(text_link, re_sum_info)
                                break

            except Exception as e:
                info = traceback.format_exc()
                print(info)
                pageNum_init += 1
            pageNum_init += 1

        self.driver.quit()


def main():
    report_obj = ReportReptile()

    # （1）page
    report_obj.get_report_page(1, 100)

    # （2）date
    # report_obj.get_report_date('2022-02-10', '2022-02-12')


if __name__ == '__main__':
    main()

