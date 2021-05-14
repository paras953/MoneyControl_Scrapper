from stock_info import StockScraper
import pandas as pd
from datetime import datetime
import os

'''
Sample for one url
url='https://www.moneycontrol.com/india/stockpricequote/power-generationdistribution/adanipower/AP11'
stock_obj=StockScraper()
data_dict=stock_obj.aggregate_data(url)
print(data_dict)

Example of output of single stock

eg 1 :{'company_name': 'Adani Power Ltd.', 'sector': 'Power - Generation & Distribution', 'mkt_cap': '37,585', 'nse_beta': '0.59', 'bse_beta': '0.55', 'face_value': '10', 'eps': '3.29', 'pe': '29.62', 'sector_pe': '18.32', 'book_value_per_share': '34.00', 'pb_ratio': '2.87', 'pc_ratio': '8.41', 'dividend_yield': '--', 'mc_essentials': '50% Pass', 'company_financial_score': '5', 'company_financials_comment': 'indicates Average Financials', 'mc_insight': 'Strong Performer:', 'rev_growth': '10.1%', 'net_profit': '%', 'operating_profit': '17.1%', 'rating_daily': 'Very Bullish', 'rating_weekly': 'Very Bullish', 'rating_monthly': 'Bullish', 'BUY': '87%', 'SELL': '13%', 'HOLD': '0%', 'broker1_name': 'NA', 'broker1_date': 'NA', 'broker1_recommendation': 'NA', 'broker2_name': 'NA', 'broker2_date': 'NA', 'broker2_recommendation': 'NA', 'broker3_name': 'NA', 'broker3_date': 'NA', 'broker3_recommendation': 'NA', 'broker4_name': 'NA', 'broker4_date': 'NA', 'broker4_recommendation': 'NA', 'broker5_name': 'NA', 'broker5_date': 'NA', 'broker5_recommendation': 'NA', 'broker6_name': 'NA', 'broker6_date': 'NA', 'broker6_recommendation': 'NA', 'broker7_name': 'NA', 'broker7_date': 'NA', 'broker7_recommendation': 'NA'}
eg 2: {'company_name': 'Housing Development Finance Corporation Ltd.', 'sector': 'Finance - Housing', 'mkt_cap': '439,928', 'nse_beta': '1.40', 'bse_beta': '1.38', 'face_value': '2', 'eps': '103.88', 'pe': '23.48', 'sector_pe': '25.57', 'book_value_per_share': '756.58', 'pb_ratio': '3.23', 'pc_ratio': '23.04', 'dividend_yield': '0.86', 'mc_essentials': '44% Pass', 'company_financial_score': '2', 'company_financials_comment': 'indicates Weak Financials', 'mc_insight': 'Weak Stock:', 'rev_growth': '8.4%', 'net_profit': '21.4%', 'operating_profit': '14.9%', 'rating_daily': 'Very Bearish', 'rating_weekly': 'Neutral', 'rating_monthly': 'Very Bullish', 'BUY': '57%', 'SELL': '7%', 'HOLD': '36%', 'broker1_name': 'ICICIdirect.com', 'broker1_date': '18 Apr, 2021', 'broker1_recommendation': 'BUY', 'broker2_name': 'HDFC Securities', 'broker2_date': '22 Feb, 2021', 'broker2_recommendation': 'REDUCE', 'broker3_name': 'HDFC Securities', 'broker3_date': '20 Feb, 2021', 'broker3_recommendation': 'BUY', 'broker4_name': 'HDFC Securities', 'broker4_date': '16 Feb, 2021', 'broker4_recommendation': 'BUY', 'broker5_name': 'HDFC Securities', 'broker5_date': '16 Feb, 2021', 'broker5_recommendation': 'BUY', 'broker6_name': 'HDFC Securities', 'broker6_date': '16 Feb, 2021', 'broker6_recommendation': 'BUY'}


'''

PROJECT_ROOT = os.path.abspath(os.path.dirname('src'))
PROJECT_ROOT=PROJECT_ROOT.replace('src','')+'output/'

df=pd.read_csv(PROJECT_ROOT+'moneycontrol_stock_list.csv')

log_list=[]
for index,rows in df.iterrows():
	
	stock_obj=StockScraper()
	print(rows['link'])
	data_dict=stock_obj.aggregate_data(rows['link'])
	log_list.append(data_dict)
	
	'''
	comment below line ...just added to check the output
	'''
	if index>20:
		break

print('Data scraping Done')	


df=pd.DataFrame(log_list)


today=datetime.now() 
date_time = today.strftime("%d/%m/%Y  %H:%M:%S")
date=today.strftime("%d-%m-%Y")
df['date']=date_time
df.fillna('NA',inplace=True)
df.to_csv(PROJECT_ROOT+'Stocks_aggregated_'+date+'.csv')