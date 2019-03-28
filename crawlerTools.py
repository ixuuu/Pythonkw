# -*- coding:utf-8 -*-

# 1 selenium set headers
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
dacp = dict(DesiredCapabilities.PHANTOMJS)

headers = {'Host': 'bj.meituan.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
path_phantomjs = r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe'
path_chrome = r'D:\chromedriver.exe'

for key, value in enumerate(headers):
    capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
    webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value

driver = webdriver.PhantomJS(path_phantomjs)
driver.set_window_size(1120, 550)
driver.get('http://bj.meituan.com/meishi/sales/pn1/')
# time.sleep(10)
# with open('resp1.html', 'w', encoding='utf-8') as f:
#         f.write(driver.page_source)
driver.quit()
