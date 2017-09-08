#coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb as msql
import chardet
import os
import codecs
import logging

dat_path = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-2])+'/sqb/json_files/bid_item_list.dat'

def save2db():
    if not os.path.exists(dat_path):
        logging.error('the dat file with crawled info is not exist')
        return 0
    try:
        conn = msql.connect(
            host = '116.62.137.20',
            port = 3306,
            user = 'root',
            passwd = 'longning',
            db = 'ztb',
            # host = '127.0.0.1',
            # port = 3306,
            # user = 'root',
            # passwd = 'rage',
            # charset = 'utf8',
            local_infile = 1
        )
        cur = conn.cursor()
        logging.info('connection established successfully')
        cur.execute('load data local infile "'+dat_path+'" into table message (title,area,industry,type,peopleInfo,projectName,price,name,time,text)')
        logging.info('dat file loaded into db successfully')
        conn.commit()
        cur.close()
    except Exception as e:
        logging.error(e)
    finally:
        if os.path.exists(dat_path):
            os.remove(dat_path)
        try:
            conn.close()
        except Exception as e:
            logging.error(e)



if __name__ == '__main__':
    conn = msql.connect(
        host = '120.77.249.40',
        port = 3306,
        user = 'root',
        passwd = 'longning',
        db = 'ztb',
        local_infile = 1
    )    
    cur = conn.cursor()
    cur.execute('select count(title) from message')
    print cur.fetchone()
    cur.execute('load data local infile "'+dat_path+'" into table message (title,area,industry,type,peopleInfo,projectName,price,name,time,text)')
    cur.execute('select count(title) from message')
    print cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    # dat_path = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-2])+'/sqb/json_files/bid_item_list.dat'
    # print 'load data local infile "'+dat_path+'" into table message (title,area,industry,type,peopleInfo,projectName,price,name,time,text)'
