# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item
from scrapy.item import Field

class PipItem(scrapy.Item):
	url = Field()
	title = Field()
	item_type = Field()
	area = Field()
	industry = Field()
	html = Field()

class BiddingItem(scrapy.Item):
	title = Field() 		# name of the bidding 
	area = Field()			# area of the bidding, eg. Hebei
	industry = Field()		# industry of the bidding, eg. Construction
	item_type = Field()		# 0,1,2 : for bidding, won and apply
	peopleInfo = Field()	# USELESS 
	projectName = Field()	# name of first party (USELESS)
	price = Field()			# price of the biddng
	name = Field()			# id-style name
	time = Field()			# time of showing of the bidding
	text = Field()			# details (main part)

# TESTING:
if __name__ == '__main__':
	pass