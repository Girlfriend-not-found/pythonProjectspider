import requests
import time
from selenium import webdriver
from pharse import main


txt_Uname = ''
txt_Upass = ''

driver = webdriver.Chrome()
driver.get('http://10.100.0.121:8020/UI/login.html')

nodes = driver.find_element_by_id('imgVerify')
nodes.screenshot('test.png')

pharse_text = main()

driver.find_element_by_id('txt_Uname').send_keys(txt_Uname)
driver.find_element_by_id('txt_Upass').send_keys(txt_Upass)
driver.find_element_by_id('txt_Code').send_keys(pharse_text)

driver.find_element_by_class_name('login_btn').click()
time.sleep(1)
cookie = dict()
for i in driver.get_cookies():
    cookie[i["name"]] = i["value"]
print(cookie)




