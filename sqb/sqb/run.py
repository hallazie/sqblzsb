#coding:utf-8

# from spiders.apply_spider import ApplySpider
# from spiders.bidding_spider import BiddingSpider
# from spiders.won_spider import WonSpider

# from scrapy import signals
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerProcess
# from scrapy.settings import Settings

from scrapy import cmdline

import save2db

# RUNNING_CRAWLERS = []

# def run():

def run():
	try:
		cmdline.execute('scrapy crawl bidding'.split())
		cmdline.execute('scrapy crawl won'.split())
		cmdline.execute('scrapy crawl apply'.split())
	finally:
		save2db.save2db()

if __name__ == '__main__':
	run()