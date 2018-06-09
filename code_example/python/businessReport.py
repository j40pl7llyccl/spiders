# coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import time



options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir="+r"C:/Users/pc/AppData/Local/Google/Chrome/tmp/User Data")
prefs = {'profile.default_content_settings.popups':0, 'download.default_directory': 'D:\\code\\download\\BusinessReport'}
options.add_experimental_option('prefs', prefs)
executable_path = r"C:\Users\pc\Desktop\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(executable_path,chrome_options=options)

driver.get("https://sellercentral.amazon.com/gp/homepage.html")
time.sleep(3)

sign=driver.find_elements_by_css_selector(css_selector="#signInSubmit")
if len(sign) >0 :
	driver.find_element_by_id("signInSubmit").click()



driver.get("https://sellercentral.amazon.com/gp/site-metrics/report.html#&reportID=eD0RCS")
time.sleep(5)
driver.find_element_by_id("report_DetailSalesTrafficBySKU").click()
time.sleep(5)

js = "$('#fromDate2').val('12/15/2017');$('toDate2').val('12/15/2017');"
driver.execute_script(js)

driver.find_element_by_id("fromDate2").click()
driver.find_element_by_xpath("//a[@class='ui-state-default ui-state-active']").click()

time.sleep(5)
driver.find_element_by_xpath("//div[@id='export']/span").click()
driver.find_element_by_id("downloadCSV").click()