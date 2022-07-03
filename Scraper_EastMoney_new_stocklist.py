import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from tqdm import tqdm


executable_path = "./phantomjs-2.1.1-windows/bin/phantomjs.exe"


def main():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36")
    driver = webdriver.PhantomJS(executable_path=executable_path, desired_capabilities=dcap)

    df = pd.read_csv('./files/stock_list.csv')
    
    all = []
    for i in tqdm(range(len(df))):

        item = df.iloc[i]
        stockCode = str(item['stockCode']).zfill(6)
        info = getWebData(driver, stockCode)
        if info!=None:
            all.append(
                {
                    'stockName':item['stockName'],
                    'stockCode':stockCode,
                    'indvInduCode':item['indvInduCode'],
                    'indvInduName':item['indvInduName'],
                    'info': info,
                }
            )

        # if i >= 20:
        #     break

    pd.DataFrame(all).to_csv('./files/eastmoney_coretheme.csv', index=None)

    driver.close()


def getWebData(driver, stockCode):
    
    insertData = None
    #driver.implicitly_wait(1)

    try:
        #东方财富核心题材

        if stockCode[0:2] == "60" :
            tempCode = "SH" + stockCode
        else:
            tempCode = "SZ" + stockCode
        
        driver.get("http://emweb.securities.eastmoney.com/CoreConception/Index?type=web&code=" + tempCode)

        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "summary")))

        insertData = element.text

    except Exception as e:
        pass
    
    return insertData
    


if __name__=='__main__':
    main()
