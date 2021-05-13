from selenium import webdriver
import os
from bs4 import BeautifulSoup as bs4
import string
import pandas as pd
import re
import traceback
import string

options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument("--incognito")
url='https://www.moneycontrol.com/india/stockpricequote/'
endpoints=list(string.ascii_uppercase)
endpoints.append('others')
final_url_list=[url+letters for letters in endpoints]

log_list=[]
for index,url in enumerate(final_url_list):
	print(endpoints[index])

	driver = webdriver.Chrome(options=options)
	driver.get(url)
	soup=bs4(driver.page_source.encode('utf-8'),'lxml')
	
	driver.quit()
	table=soup.findAll('table',{'class':'pcq_tbl MT10'})
	if len(table)==0:
		print('Failed for {}'.format(endpoints[index]))
		continue
	row_list=table[0].findAll('tr')
	
	if len(row_list)==0:
		print('No rows for {}'.format(endpoints[index]))

	for rows in row_list:
		td=rows.findAll('td')
		if len(td)==0:
			continue
		for items in td:
			log_dict={}
			log_dict['name']=items.findAll('a')[0].text 
			log_dict['link']=items.findAll('a')[0]['href']
			log_list.append(log_dict)

	print('Done for {}'.format(url))



print('DF starts now')
df=pd.DataFrame(log_list)
df.to_csv('moneycontrol_stock_list.csv',index=False)
