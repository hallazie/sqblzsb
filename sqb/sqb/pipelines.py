# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from items import BiddingItem, PipItem
from bs4 import BeautifulSoup as soup
from scrapy.selector import Selector

import chardet
import redis
import codecs
import json
import re
import logging
import time
import os

root_path = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-2])
keys = ['title','area','industry','item_type','peopleInfo','projectName','price','name','time','text']

class SqbPipeline(object):
	def __init__(self):
		self.rds = redis.Redis(host = '127.0.0.1', port = 6379)
		self.filter_units = ['斤','公斤','千克', '克', '毫升', '升', '厘米', '米', '平方厘米', '平方米']

	def process_item(self, pipitem, spider):
		'''
			TODO: parse the bidding info in this page (e.g. title,
			price, area and shit), and get the main body of this 
			page (aka. remove head, all the <div>s with hyperlink 
			and img and shit, and get a html with only the information)
		'''

		dat_file = codecs.open(root_path + '/sqb/json_files/bid_item_list.dat', 'a', encoding='utf-8')

		if self.redis_exist(pipitem['title']):
			logging.info('duplicated item, jump over: '+pipitem['title'])
			return 0

		if spider.name == 'bidding':
			item = self.process_bidding(pipitem)
			try:
				line = '\t'.join([str(item[k]) for k in keys])+'\n'
				dat_file.write(line)
				self.redis_add(pipitem['title'])
				logging.info('item '+item['title']+' saved!!!!!!!')
				# saved = open('/home/hallazie/codes/Pz/sqb/stuff/all_pages/'+str(item['price'])+item['title'].encode('utf-8')+'.html', 'w')
				# saved.write(str(item['text']))
				# saved.close()
				return item
			finally:
				dat_file.close()

		elif spider.name == 'apply':
			item = self.process_apply(pipitem)
			try:
				line = '\t'.join([str(item[k]) for k in keys])+'\n'
				dat_file.write(line)
				self.redis_add(pipitem['title'])
				logging.info('item '+item['title']+' saved!!!!!!!')
				return item
			finally:
				dat_file.close()
			
		elif spider.name == 'won':
			for keyword in ['申报', '征集', '项目']:
				if keyword in pipitem['title']:
					item = self.process_apply(pipitem)
					try:
						line = '\t'.join([str(item[k]) for k in keys])+'\n'
						dat_file.write(line)
						self.redis_add(pipitem['title'])
						logging.info('item '+item['title']+' saved!!!!!!!')
						return item
					finally:
						dat_file.close()
		else:
			dat_file.close()
			logging.warning('currpage of'+pipitem['url']+' is not a valid bidding info page')

	def process_bidding(self, pipitem):
		item = BiddingItem()
		item['title'] = pipitem['title']
		item['area'] = pipitem['area']				# get from json
		item['industry'] = pipitem['industry']		# get from json
		item['item_type'] = 0
		item['peopleInfo'] = None
		item['projectName'] = None					# USELESS
		item['price'] = self.price_curr_page(pipitem['html'])
		item['name'] = self.nameid_curr_page(pipitem['html'])
		item['time'] = self.time_curr_page()
		item['text'] = self.strip_curr_page(pipitem['html'])
		return item

	def process_won(self, pipitem):
		item = BiddingItem()
		item['title'] = pipitem['title']
		item['area'] = pipitem['area']				# get from json
		item['industry'] = pipitem['industry']		# get from json
		item['item_type'] = 1
		item['peopleInfo'] = self.company_curr_page(pipitem['html'])
		item['projectName'] = None					# USELESS
		item['price'] = self.price_curr_page(pipitem['html'])
		item['name'] = self.nameid_curr_page(pipitem['html'])
		item['time'] = self.time_curr_page()
		item['text'] = self.strip_curr_page(pipitem['html'])
		return item

	def process_apply(self, pipitem):
		item = BiddingItem()
		item['title'] = pipitem['title']
		item['area'] = pipitem['area']				# get from json
		item['industry'] = pipitem['industry']		# get from json
		item['item_type'] = 2
		item['peopleInfo'] = None					# USELESS
		item['projectName'] = None					# USELESS
		item['price'] = None
		item['name'] = None
		item['time'] = self.time_curr_page()
		item['text'] = self.strip_curr_page(pipitem['html'])
		return item
		
	# ++++++++++++++++++++++++++++++++++++++++++++++++++++++ UTILS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def company_curr_page(self, body):
		return None

	def keep_curr_page(self, body = 0):
		'''
			use Redis to decide if message is duplicated. if so, throw away. [亿万元]
		'''
		return True

	def time_curr_page(self):
		return time.strftime("%Y-%m-%d#%H:%M:%S", time.localtime(int(time.time())))

	def nameid_curr_page(self, body):
		id_list = []
		for text in Selector(text=body).xpath('//text()').extract():
			try:
				text = self.strip_blanks(text)
				id_list.append(re.findall('招标[序编]号：(.+?)', page)[0])
			except Exception as e:
				continue
		if len(id_list) > 0:
			return id_list[0]
		else:
			return '详见页面'	

	def strip_curr_page(self, body):
		'''
			TODO: strip the current html(bidding info page) and remove
			all the links and images and shit, leave only the text part
			as the main body of this bidding info
		'''
		html = soup(body, 'lxml')
		attr_filter_list = ['href', 'src']			# attrs which are useless
		div_filter_list = ['li', 'a', 'td', 'tr']	# divs which are possibly useless
		node_filter_list = ['script', 'input', 'option', 'select']		# divs which are definitely useless

		for attr in attr_filter_list:
			for curr_div in html.find_all(attrs={attr:re.compile('.+?')}):
				curr_div.replace_with('')

		for div in div_filter_list:
			for curr_div in html.find_all(div):
				if curr_div.text.replace('\t','').replace('\n','').replace(' ', '').replace('&nbsp;', '') == '':
					curr_div.replace_with('')

		for node in node_filter_list:
			for curr_div in html.find_all(node):
				curr_div.replace_with('')

		ret_html = str(html).replace('\t','').replace('\n','')
		return ret_html

	def price_curr_page(self, body):
		'''
			first, stripe the html to a string, and only keep the text part
			which means concat every Selector(text=html).xpath('//text()').extract()
			to a total string.

			TOBEDONE: add fake-price need to be filtered: e.g. 10000000 meters 
		'''
		flag = 0
		page = ''
		for text in Selector(text=body).xpath('//text()').extract():
			page += self.strip_blanks(text)
		page = page.encode('utf-8')
		if '万元' in page:
			flag = 1

		fake_prices = []
		for fake_filter in self.filter_units:
			fake_prices += re.findall('([0-9\.]+?'+fake_filter+')', page)

		# find price in format of '1000万元'
		result_list = re.findall('([0-9\.]+?元|[0-9\.]+?万元)', page)
		for res in result_list:
			print res
		price_list = []
		for result in result_list:
			try:
				num_part = float(result.replace('元','').replace('万',''))
				if '万' in result:
					num_part *= 10000
				if num_part > 5000 and num_part < 9999999999:
					price_list.append(num_part)
			except Exception as e:
				logging.error(e)
				continue
		if len(price_list) > 0:
			try:
				return sorted(price_list, reverse = True)[0]
			except Exception as e:
				logging.error(e)
				return 0

		result_list = []
		# find price in format '1000.00'
		result_list = re.findall('([0-9\.]+\.[0-9][0-9])', page)
		try:	
			price_list = []
			for result in result_list:
				result = float(result)
				if flag == 1:
					result *= 10000
				if result > 5000 and result < 9999999999:
					price_list.append(result)
			if len(price_list) > 0:
				biggest = sorted(price_list, reverse = True)[0]
				if biggest not in fake_prices:
					return biggest
		except Exception as e:
			logging.error(e)
			return 0

		price_list = []
		# find price in the loose format '100000'
		for text in Selector(text=body).xpath('//text()').extract():
			try:
				text = self.strip_blanks(text)
				result = float(text)
				if flag == 1:
					result *= 10000
				if result > 5000 and result < 9999999999:
					price_list.append(result)
			except Exception as e:
				continue
		if len(price_list) > 0:
			biggest = sorted(price_list, reverse = True)[0]
			if biggest not in fake_prices:
				return biggest
		else:
			return 0

	# ------------------------------------------------------------- UTILS -------------------------------------------------------------

	def strip_blanks(self, text):
		return text.replace(' ','').replace('\t','').replace('\n','').replace('&nbps;','') 

	def redis_exist(self, bid_id):
		return self.rds.sismember('junk_id',bid_id)

	def redis_add(self, bid_id):
		self.rds.sadd('junk_id',bid_id)

if __name__ == '__main__':
	a = {'a':0,'b':'BBB','c':True}
	b = [a[k] for k in a]
	print b