# coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import t3





options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir="+r"C:/Users/pc/AppData/Local/Google/Chrome/tmp/User Data")
prefs = {'profile.default_content_settings.popups':0, 'download.default_directory': 'D:\\code\\download\\BusinessReport'}
options.add_experimental_option('prefs', prefs)


executable_path = r"C:\Users\pc\Desktop\chromedriver_win32\chromedriver.exe"


driver = webdriver.Chrome(executable_path,chrome_options=options)


driver.get("http://47.88.53.247:8081/web-crm/")
#driver.find_element_by_link_text("consoleAppender.2017-12-11.log").click()

ky=driver.find_elements_by_css_selector(css_selector="#ky")
print(len(ky))


