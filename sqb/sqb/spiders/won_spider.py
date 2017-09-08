#coding:utf-8

import scrapy
import sys
import re
import logging
import time
sys.path.append("..")

from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from sqb.items import PipItem
from sqb.urls import get_won
from bs4 import BeautifulSoup as soup

class WonSpider(CrawlSpider):
	name = 'won'
	url_dict_list = get_won()
	html_head = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>'
	html_tail = '</body></html>'
	logging.basicConfig(level = logging.INFO)

	def start_requests(self):
		'''
			TODO: generate request of the list-site and send to the 
			callback parse_list() to get all the actual pages with 
			won info.
		'''
		for url_dict in self.url_dict_list:
			try:
				url = url_dict['url']
				name = url_dict['name']
				province = url_dict['province']
				city = url_dict['city']
				server_type = url_dict['type']
				if url != '' and name != '':
					logging.info('now crawling at site: '+name)
					yield Request(url = url, meta = {'list_url':url, 'province':province,
						'city':city, 'server_type':server_type}, callback = self.parse_list)
			except Exception as e:
				logging.error(e)


	def parse_list(self, response):
		'''
			TODO: parse the current list-cite and get all the urls
			in the node of form <a href="..." title="..."> which 
			indicates that this is a won info page, since it has
			a title.
		'''
		html = response.body
		logging.info('now crawling page: '+response.url)

		for a in soup(str(html), 'lxml').find_all('a'):
			try:
				url = a.attrs['href']
				title = a.attrs['title']
			except Exception as e:
				continue
			
			if url[0] != '/':
				actual_url = url
			else:
				actual_url = '/'.join(response.meta['list_url'].split('/')[0:3])+url

			province = response.meta['province']
			city = response.meta['city']
			server_type = response.meta['server_type']
			yield Request(url = actual_url, meta = {'title':title, 'province':province, 
				'city':city, 'industry':server_type}, callback = self.parse_info)

	def parse_info(self, response):

		item = PipItem()
		item['url'] = response.url
		item['title'] = response.meta['title']
		item['item_type'] = 1
		item['area'] = response.meta['province']
		item['industry'] = response.meta['industry']
		item['html'] = response.body
		yield item
