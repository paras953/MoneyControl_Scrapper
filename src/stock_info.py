from selenium import webdriver
import os
from bs4 import BeautifulSoup as bs4
import string
import pandas as pd
import re
import traceback


options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument("--incognito")


class StockScraper():
	def __init__(self):
		#useful variables
		self.technicals_link_daily=None
		self.technicals_link_weekly=None
		self.technicals_link_monthly=None

		self.company_details={}
		self.overview_details={}
		self.essentials={}
		self.technicals={'daily':{},'weekly':{},'monthly':{}}
		self.user_sentiment={}
		self.final_dict={}
		self.base_scraper=None
		self.broker_research={}
		self.price_scraper=None
		self.price_data={}

	def get_base_data(self,base_url):
		#1st method to call

		print('Get base data called')
		try:
			driver = webdriver.Chrome(options=options)
			driver.get(base_url)
			soup=bs4(driver.page_source.encode('utf-8'),'lxml')
			self.base_scraper=soup
			driver.quit() #Exiting now will use only when needed

			table=soup.findAll('div',{'class':'bx_mceti'})

			for items in table:
				link=items.findAll('a')
				#print(link)
				if len(link)>0:
					self.technicals_link_daily=link[0]['href']
					break

			company_tag=soup.findAll('div',{'id':'stockName'})
			

			for cos in company_tag:
				self.company_details['company_name']=cos.findAll('h1')[0].text.strip()
				self.company_details['sector']=cos.findAll('a')[0].text.strip()		

			
			print('Overview details now')
			overview_table_list=soup.findAll('div',{'class':'oview_table'})


			#First one is of not much use
			ov_table1=overview_table_list[1]
			ov_table2=overview_table_list[2]
			ov_table3=overview_table_list[3]

			self.overview_details['mkt_cap']=ov_table1.findAll('td',{'class':'nsemktcap bsemktcap'})[0].text
			self.overview_details['nse_beta']=ov_table1.findAll('span',{'class':'nsebeta'})[0].text
			self.overview_details['bse_beta']=ov_table1.findAll('span',{'class':'bsebeta'})[0].text

			self.overview_details['face_value']=ov_table2.findAll('td',{'class':'nsefv bsefv'})[0].text
			self.overview_details['eps']=ov_table2.findAll('td',{'class':'nseceps bseceps'})[0].text
			self.overview_details['pe']=ov_table2.findAll('td',{'class':'nsepe bsepe'})[0].text
			self.overview_details['sector_pe']=ov_table2.findAll('td',{'class':'nsesc_ttm bsesc_ttm'})[0].text
			self.overview_details['book_value_per_share']=ov_table2.findAll('td',{'class':'nsebv bsebv'})[0].text

			self.overview_details['pb_ratio']=ov_table3.findAll('td',{'class':'nsepb bsepb'})[0].text
			self.overview_details['pc_ratio']=ov_table3.findAll('td',{'class':'nsep_c bsep_c'})[0].text
			self.overview_details['dividend_yield']=ov_table3.findAll('td',{'class':'nsedy bsedy'})[0].text

			
			self.essentials['mc_essentials']=soup.findAll('div',{'id':'mcessential_div'})[0].findAll('div')[0].findAll('div')[1].findAll('div')[0].text
			
			#self.essentials['mc_essentials']=soup.findAll('div',{'class':'bx_mceti mc_essenclick'})[0].findAll('div',{"class":'esbx esbx3'})[0].text
			
			try:
				self.essentials['company_financial_score']=soup.findAll('div',{'class':'fpioi'})[0].findAll('div')[-1].text
			except Exception as e:
				self.essentials['company_financial_score']='NA'
			try:
				self.essentials['company_financials_comment']=soup.findAll('div',{'class':'fpioi'})[0].findAll('p')[0].text
			except Exception as e:
				self.essentials['company_financials_comment']='NA'
			try:
				self.essentials['mc_insight']=soup.findAll('div',{'id':'mc_insight'})[0].findAll('div')[1].findAll('p')[0].findAll('strong')[0].text
			except Exception as e:
				print('No insight found')
				self.essentials['mc_insight']='NA'

			company_rev=soup.findAll('table',{'class':'frevdat'})[0]
			row_list=company_rev.findAll('tr')
			
			self.essentials['rev_growth']=row_list[0].findAll('td')[1].text
			self.essentials['net_profit']=row_list[1].findAll('td')[1].text
			self.essentials['operating_profit']=row_list[2].findAll('td')[1].text



			print('Done with base data')
			return 0
		except Exception as e:
			print(e)
			traceback.print_exc()
			print('getting base data failed')
			return 1


	def get_technical_data(self):
		print('get_technical_data')
		try:
			if self.technicals_link_daily==None:
				print('No technical link found')
				return 1

			driver = webdriver.Chrome(options=options)
			driver.get(self.technicals_link_daily)
			soup_daily=bs4(driver.page_source.encode('utf-8'),'lxml')
			self.price_scraper=soup_daily #for bese/nse price
			driver.quit() #Exiting now will use only when needed


			self.technicals_link_weekly=self.technicals_link_daily.replace('daily','weekly')
			self.technicals_link_monthly=self.technicals_link_daily.replace('daily','monthly')

			driver = webdriver.Chrome(options=options)
			driver.get(self.technicals_link_weekly)
			soup_weekly=bs4(driver.page_source.encode('utf-8'),'lxml')
			driver.quit() #Exiting now will use only when needed

			driver = webdriver.Chrome(options=options)
			driver.get(self.technicals_link_monthly)
			soup_monthly=bs4(driver.page_source.encode('utf-8'),'lxml')
			driver.quit() #Exiting now will use only when needed

			#method calls for getting technicl data
			self.scrape_technical(time_range='daily',scraper_obj=soup_daily)
			self.scrape_technical(time_range='weekly',scraper_obj=soup_weekly)
			self.scrape_technical(time_range='monthly',scraper_obj=soup_monthly)
			return 0
		except Exception as e:
			print(e)
			traceback.print_exc()
			print('Error while hitting technicals site')
			return 1

	def scrape_technical(self,time_range,scraper_obj):
		#time_range can be one of daily/weekly/monthly
		try:
			tech_ids={'daily':'techan_daily','weekly':'techan_weekly','monthly':'techan_monthly'}
			possible_ids={'bulishbar verybearish':'Very Bearish','bulishbar bearish':'Bearish','bulishbar neutral':'Neutral','bulishbar bullish':'Bullish','bulishbar verybullish':'Very Bullish'}

			technical_items=scraper_obj.findAll('div',{'id':tech_ids[time_range]})

			for items in technical_items:
				for ids in possible_ids.keys():
					rating=items.findAll('div',{'class':ids})
					if len(rating)>0:
						self.technicals[time_range]['rating']=possible_ids[ids]
						break




			return 0
		except Exception as e:
			print(e)
			traceback.print_exc()
			print('Scrape technical failed {}'.format(time_range))
			return 1

	def get_price_data(self):
		try:

			print('get_price_data called')
			soup=self.price_scraper
			self.price_data['bse_price']=soup.findAll('div',{'class':'bsedata_bx'})[0].findAll('div',{'class':'pcnsb div_live_price_wrap'})[0].findAll('span')[0].text
			self.price_data['nse_price']=soup.findAll('div',{'class':'nsedata_bx'})[0].findAll('div',{'class':'pcnsb div_live_price_wrap'})[0].findAll('span')[0].text
			self.price_data['bse_vol']=soup.findAll('div',{'class':'bsedata_bx'})[0].findAll('span',{'class':'txt13_pc volume_data'})[0].text
			self.price_data['nse_vol']=soup.findAll('div',{'class':'nsedata_bx'})[0].findAll('span',{'class':'txt13_pc volume_data'})[0].text
			return 0

		except Exception as e:
			print(e)
			print('get_price_data failed')
			traceback.print_exc()
			return 1




	def get_user_sentiment(self):
		print('get_user_sentiment')
		try:
			soup=self.base_scraper
			chart_fl=soup.findAll('div',{'class':'chart_fl'})
			sentiment=None
			
			for items in chart_fl:
				sentiment=soup.findAll('ul',{'class':'buy_sellper'})
				if len(sentiment)>0:
					break

			if len(sentiment)>0:
				list_class=sentiment[0].findAll('li')
				for items in list_class:
					self.user_sentiment[items.text.split(' ')[-1]]=items.text.split(' ')[0]
				return 0
			else:
				print('No sentiment found')
				return 1
		except Exception as e:
			print(e)
			print('get_user_sentiment failed')
			traceback.print_exc()
			return 1

	def get_broker_research(self):
		print('get_broker_research')
		try:
			
			keys1=['broker1','broker2','broker3','broker4','broker5','broker6','broker7']
			keys2=['name','date','recommendation']
			final_key_list=[]
			for item1 in keys1:
				for item2 in keys2:
					final_key_list.append(item1+'_'+item2)

			soup=self.base_scraper
			div_broker=soup.findAll('div',{'id':'broker_research'})[0].findAll('div',{'class':'brrs_stock'})[0].findAll('div',{'class':'clearfix'})
			
			if len(div_broker)==1 and div_broker[0].text=='No Data For Broker Research.':
				for keys in final_key_list:
					self.broker_research[keys]='NA'
				return 0
			if len(div_broker)>0:
				div_broker_final=div_broker[0].findAll('div',{'class':'brrs_bx grey_bx'})
				for index,items in enumerate(div_broker_final):
					brkr_index=str(index+1)
					key_name='broker'+brkr_index+'_name'
					key_date='broker'+brkr_index+'_date'
					key_rec='broker'+brkr_index+'_recommendation'
					
					self.broker_research[key_name]=items.findAll('div',{'class':'brstk_name'})[0].findAll('h3')[0].text
					self.broker_research[key_date]=items.findAll('div',{'class':'br_date'})[0].text
					self.broker_research[key_rec]=items.findAll('button')[0].text
				return 0
			return 1
		except Exception as e:
			print('SOme error in broker research')
			traceback.print_exc()
			return 1


		except Exception as e:
			print(e)
			traceback.print_exc()
			return 1

	
	def update_data(self,data_dict,dict_type,time_range=None):

		if len(data_dict.keys())>0 and dict_type!='technicals':
			for keys in data_dict.keys():
				self.final_dict[keys]=data_dict[keys]
			return 0
		elif len(data_dict[time_range].keys())>0 and dict_type=='technicals':

			for keys in data_dict[time_range].keys():
				self.final_dict[keys+'_'+time_range]=data_dict[time_range][keys]
			return 0
		else:
			print('No data to update')
			return 1			


	def aggregate_data(self,url):
		final_dict={}
		print('Aggregate data called')
		result_base_data=self.get_base_data(base_url=url)
		if result_base_data==0:
			self.update_data(self.company_details,dict_type='company_details')
			self.update_data(self.overview_details,dict_type='overview_details')
			self.update_data(self.essentials,dict_type='essentials')

		result_technicals=self.get_technical_data()

		if result_technicals==0:
			self.update_data(self.technicals,dict_type='technicals',time_range='daily')
			self.update_data(self.technicals,dict_type='technicals',time_range='weekly')
			self.update_data(self.technicals,dict_type='technicals',time_range='monthly')

		result_user_sentiment=self.get_user_sentiment()

		if result_user_sentiment==0:
			self.update_data(self.user_sentiment,dict_type='user_sentiment')

		result_broker=self.get_broker_research()

		result_price_data=self.get_price_data()
		if result_price_data==0:
			self.update_data(self.price_data,dict_type='price_data')

		if result_broker==0:
			self.update_data(self.broker_research,dict_type='broker_research')

		print('Done scraping everything')
		return self.final_dict