# coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time



profile = webdriver.FirefoxProfile("C:\\Users\\pc\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\twshyplx.default")
profile.set_preference('browser.download.dir', 'D:\\code\\download')
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

driver = webdriver.Firefox(firefox_profile=profile)

###login
#driver.get("https://sellercentral.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fsellercentral.amazon.com%2Fgp%2Fhomepage.html&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=sc_na_amazon_v2&_encoding=UTF8&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&language=en_US&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=sc_na_amazon&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&ssoResponse=eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.q7oujB5A_nuoHWifjt8iWjJrpuKBJ5TbbdDSv0ak6722eZ7zZKZTOQ.J0h1F1VI_DnAMYpp.cR909kD5QN5QHKC3t05XEUWimg5U0izpc1P2cZkdulmo7-AcfRuofUO8UCMtfeUNiXAFrdZw4Q8y0VIhAPO9QKV1jXmq1theWSwQFPFpA5C00lKT0P-TP1c8_fQVyDoQuGxgT5Yf6CiPZsMBtHNRw9matsALK23cZ0OPwmql4WhoIVKjqfxfjgl1UR4uK0ZZ67fCMC0vTWxMqbHO3rHsPfwTIFAIsQoKhYDapMlKpTuv00jIytGTnHn7KyZQUS3P6ZkeV89N5etkc5ClRO2ykxkOopX5Y3lpQA.s7p0LDaPEFzl2sf6KZRIVg")
#driver.find_element_by_id("signInSubmit").click();
#driver.find_element_by_xpath('//*[@id="sc-top-nav-root"]/li[7]/ul/li[4]/a').click()
#driver.get("https://sellercentral.amazon.com/gp/homepage.html")
#FvmallCA20170224


driver.get("https://sellercentral.amazon.com/gp/site-metrics/report.html#&reportID=eD0RCS")
time.sleep(5)
driver.find_element_by_id("report_DetailSalesTrafficBySKU").click()
time.sleep(5)
driver.find_element_by_xpath("//div[@id='export']/span").click()
driver.find_element_by_id("downloadCSV").click()
