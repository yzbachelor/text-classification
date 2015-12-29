# -*- coding: cp936 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
#encoding=utf-8
import MySQLdb
import os
import re
import logging
FILE=os.getcwd()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'log.txt'),
                    filemode='w')


def readTrain():
    '''
    从数据库读取训练数据，训练数据说明文档train.csv，训练文本数据存放在train_article
    '''
    try:
        conn=MySQLdb.connect(host='120.24.89.65',user='ggt',passwd='ggt123',\
                             db='offline',port=4000,charset='utf8')
        cur=conn.cursor()
        cur.execute("select aid,from_type,status,tid_1,tid_2,tid_3,tid_4\
                    from article where status=1 or status=2")
        rows=cur.fetchall()
        readme=[]
        for row in rows:
            readme.append(str(row[0])+','+str(row[1])+','+str(row[2])+','+\
                          str(row[3])+','+str(row[4])+','+str(row[5])+','+str(row[6]))
        f=open('train.csv','w')
        f.write('\n'.join(readme))
        f.close()
        logging.debug('train.csv is stablished')
        path='./train_article/'
        if not os.path.exists(path):
            os.mkdir(path)
        ff=[]
        for row in rows:
            filename=str(row[0])+'.txt'
            if not os.path.isfile(path+filename):
                ff.append(str(row[0]))
        if len(ff)==0:
            logging.info("no new articles added")
        else:
            for i in range(len(ff)/1000+1):
                if (i+1)*1000>len(ff):
                    ff1=ff[i*1000:]
                else:
                    ff1=ff[i*1000:(i+1)*1000]
                ff1=','.join(ff1)
                cur.execute("select aid,content from article where aid in (%s)"%ff1)
                rows=cur.fetchall()
                for row in rows:
                    filename=str(row[0])+'.txt'
                    f=open(path+filename,'w')
                    f.write(re.sub(r'<(S*?)[^>]*>.*?|<.*? /> ','',str(row[1])))
                    f.close()
        logging.debug('train_articles are loaded')
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))


def readTest():
    '''
    从数据库读取测试数据，训练数据说明文档test.csv，训练文本数据存放在test_article
    '''
    try:
        conn=MySQLdb.connect(host='120.24.89.65',user='ggt',passwd='ggt123',\
                             db='offline',port=4000,charset='utf8')
        cur=conn.cursor()
        cur.execute("select aid,from_type,status,tid_1,tid_2,tid_3,tid_4\
                    from article where status=0")
        rows=cur.fetchall()
        readme=[]
        for row in rows:
            readme.append(str(row[0])+','+str(row[1])+','+str(row[2])+','+\
                          str(row[3])+','+str(row[4])+','+str(row[5])+','+str(row[6]))
        f=open('test.csv','w')
        f.write('\n'.join(readme))
        f.close()
        logging.debug('test.csv is stablished')
        path='./test_article/'
        if not os.path.exists(path):
            os.mkdir(path)
        ff=[]
        for row in rows:
            filename=str(row[0])+'.txt'
            if not os.path.isfile(path+filename):
                ff.append(str(row[0]))
        if len(ff)==0:
            logging.info("no new articles added")
        else:
            for i in range(len(ff)/1000+1):
                if (i+1)*1000>len(ff):
                    ff1=ff[i*1000:]
                else:
                    ff1=ff[i*1000:(i+1)*1000]
                ff1=','.join(ff1)
                cur.execute("select aid,content from article where aid in (%s)"%ff1)
                rows=cur.fetchall()
                for row in rows:
                    filename=str(row[0])+'.txt'
                    f=open(path+filename,'w')
                    f.write(re.sub(r'<(S*?)[^>]*>.*?|<.*? /> ','',str(row[1])))
                    f.close()
        logging.debug('test_articles are loaded')
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))

def updataSql():
    try:
        conn=MySQLdb.connect(host='120.24.89.65',user='ggt',passwd='ggt123',db='offline',port=4000,charset='utf8')
        cur=conn.cursor()
        f=open('result.txt','r')
        dd=f.read().split()
        f.close()
        X=[]
        for d in dd:
            X.append(d.split(','))
        ss=[]
        for x in X:
            if x[1]=='1.0':
                ss.append(x[0])
        ss=','.join(ss)
        cur.execute('update article set status="3" where aid in(%s)'%ss)
        cur.close()
        conn.commit()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
