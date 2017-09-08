#coding:utf-8
import json
import codecs
import os
import logging

root_path = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-2])

def get_bidding():
	json_dir = root_path + '/sqb/json_files/'
	jfile = json.load(codecs.open(json_dir+'bidding.json', 'r', encoding='utf-8'))
	return jfile

def get_won():
	json_dir = root_path + '/sqb/json_files/'
	jfile = json.load(codecs.open(json_dir+'bidded.json', 'r', encoding='utf-8'))
	return jfile

def get_apply():
	json_dir = root_path + '/sqb/json_files/'
	jfile = json.load(codecs.open(json_dir+'apply.json', 'r', encoding='utf-8'))
	return jfile

if __name__ == '__main__':
	try:
		f = open(root_path+'/sqb/json_files/bid_item_list.json', 'r')
		i = 0
		while True:
			i+=1
			l = f.readline()
			if l == '':
				break
			print i
	except Exception as e:
		logging.error(e)
	finally:
		try:
			f.close()
		except Exception as e:
			logging.error(e)