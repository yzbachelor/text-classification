#-*- coding: utf-8 -*-
import os
import jieba
import pandas as pd
import logging
FILE=os.getcwd()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'log.txt'),
                    filemode='w')


#achieve list of files
def getFilelist(argv):
    path=argv
    filelist=[]
    files=os.listdir(path)
    for f in files:
        if(f[0]=='.'):
            pass
        else:
            filelist.append(f)
    return filelist,path



#splitWordQ   全模式
def splitWordQ(argv,path,spath):
    sFilePath=spath
    if not os.path.exists(sFilePath):
        os.mkdir(sFilePath)
    filename=argv
    f=open(path+filename,'r+')
    file_list=f.read()
    f.close()
    stopwords = {}.fromkeys([ line.rstrip() for line in open('stopword.txt') ])
    seg_list=jieba.cut(file_list,cut_all=True)
    
    result=[]
    for seg in seg_list:
        seg=''.join(seg.split())
        if(seg!='' and seg!="/n"and seg!="/n/n" and seg not in stopwords):
            result.append(seg)
            
    f=open(sFilePath+"/"+filename,'w+')
    f.write(' '.join(result).encode('utf-8'))
    f.close()

#splitWord   精确模式
def splitWord(argv,path,spath):
    sFilePath=spath
    if not os.path.exists(sFilePath):
        os.mkdir(sFilePath)
    filename=argv
    f=open(path+filename,'r+')
    file_list=f.read()
    f.close()
    stopwords = {}.fromkeys([ line.rstrip() for line in open('stopword.txt') ])
    seg_list=jieba.cut(file_list,cut_all=False)
    
    result=[]
    for seg in seg_list:
        seg=''.join(seg.split())
        if(seg!='' and seg!="/n"and seg!="/n/n" and seg not in stopwords):
            result.append(seg)
            
    f=open(sFilePath+"/"+filename,'w+')
    f.write(' '.join(result).encode('utf-8'))
    f.close()

def SplitW():
    (allfile,path) = getFilelist("./train_article/")
    logging.debug('train_article reloaded')
    for ff in allfile:
        if not os.path.isfile('./train_segfile1/'+ff):        
            print "Using jieba on train_article "+ff
            splitWordQ(ff, path,'./train_segfile1')
            splitWord(ff, path,'./train_segfile2')
    logging.debug('train_article words split!')
    (allfile,path) = getFilelist("./test_article/")
    logging.debug('test_article reloaded')
    for ff in allfile:
        if not os.path.isfile('./test_segfile1/'+ff):        
            print "Using jieba on test_article "+ff
            splitWordQ(ff, path,'./test_segfile1')
            splitWord(ff, path,'./test_segfile2')
    logging.debug('test_article words split!')

