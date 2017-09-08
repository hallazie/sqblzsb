#coding:utf-8

import json
import codecs

def get_json():
	jpath = '/home/hallazie/codes/Pz/sqb/sqb/json_files/bid_item_list.json'
	file = open(jpath, 'r')

	while True:
		try:
			curr_j = json.loads(file.readline())
			print curr_j['title']
			print curr_j['price']
			print curr_j['name']
			print '========================='
			# f = codecs.open('/home/hallazie/codes/Pz/sqb/stuff/new_pages/'+curr_j['title'], 'w', encoding='utf-8')
			# f.write(curr_j['text'])
			# f.close()
		except Exception as e:
			print e
			break
	file.close()

if __name__ == '__main__':
	get_json()