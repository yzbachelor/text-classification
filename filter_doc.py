#-*- coding: utf-8 -*-
from sklearn import svm
from sklearn import metrics
from sklearn import cross_validation 
from sklearn.externals import joblib
import pandas as pd
import os
import numpy as np
import random
from mySql import readTrain,readTest,updataSql
from split_word import SplitW
from gensim import corpora, models, similarities
from collections import defaultdict
import logging
FILE=os.getcwd()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'log.txt'),
                    filemode='w')


def MyDict():
    '''
    利用训练数据和gensim，生成字典dict
    '''
    path='./train_segfile2/'
    rdarray=pd.read_csv("train.csv", header=None)
    documents=[]
    for i in range(0,rdarray.shape[0]):
        fname=path+str(rdarray[0][i])+'.txt'
        f=open(fname,'r+')
        context=f.read().decode('utf-8')
        f.close()
        documents.append(context)
    texts=[[word for word in document.split()]for document in documents]
    dictionary = corpora.Dictionary(texts)
    dictionary.save('wordDict1.dict')


    
class MyCorpus(object):
    '''
    利用训练文档和字典，生成corpus
    '''
    def __iter__(self):
        path='./train_segfile2/'
        rdarray=pd.read_csv("train.csv", header=None)
        dictionary=corpora.Dictionary.load('wordDict1.dict')
        for i in range(0,rdarray.shape[0]):
            fname=path+str(rdarray[0][i])+'.txt'
            f=open(fname,'r+')
            context=f.read().decode('utf-8')
            f.close()
            if len(context)>800:
                yield dictionary.doc2bow(context.split())


class MyCorpus1(object):
    '''
    利用测试文档和字典，生成corpus
    '''
    def __iter__(self):
        path='./test_segfile2/'
        rdarray=pd.read_csv("test.csv", header=None)
        dictionary=corpora.Dictionary.load('wordDict1.dict')
        for i in range(0,rdarray.shape[0]):
            fname=path+str(rdarray[0][i])+'.txt'
            f=open(fname,'r+')
            context=f.read().decode('utf-8')
            f.close()
            yield dictionary.doc2bow(context.split())

def sampling(X,Y):
    '''
    欠采样
    '''
    sample_x=[]
    sample_y=[]
    Y_label=[0 for i in range(len(Y))]
    count=0
    for i in range(len(Y)):
        if Y[i]==1:
            sample_x.append(X[i])
            sample_y.append(Y[i])
            count+=1
            Y_label[i]=1
    #print count
    num=0
    while num<count*3:
        index=random.randint(0,len(Y)-1)
        if Y[index]!=1 and Y_label[index]==0:
            sample_x.append(X[index])
            sample_y.append(Y[index])
            Y_label[index]=1
            num+=1
    return sample_x,sample_y


def train(argv):
    path=argv
    rdarray=pd.read_csv("train.csv", header=None)
    y=[]
    for i in range(0,rdarray.shape[0]):
        fname=path+str(rdarray[0][i])+'.txt'
        f=open(fname,'r+')
        context=f.read().decode('utf-8')
        f.close()
        if len(context)>800:
            if rdarray[2][i]==1:
                y.append(1)
            else:
                y.append(2)
    dictionary=corpora.Dictionary.load('wordDict1.dict')
    corpus_train=corpora.MmCorpus('wordDict1.mm')
    tfidf = models.TfidfModel(corpus_train)
    lsi=models.LsiModel.load('model1.lsi')
    corpus_memory_friendly = MyCorpus()
    corpus_tfidf = tfidf[corpus_memory_friendly]
    corpus_lsi = lsi[corpus_tfidf]
    X=[[s[1] for s in w]for w in corpus_lsi]
    X=pd.DataFrame(X)
    X=X.fillna(value=0)
    X=np.array(X)
    Y=y
    np.savetxt("Xdata.txt",X)
    np.savetxt("Ydata.txt",Y)
    logging.debug("train_data X,Y are ready!")
    '''
    #svm classweight
    X=np.loadtxt("Xdata.txt")
    Y=np.loadtxt("Ydata.txt")
    '''
    X_train,Y_train=sampling(X,Y)
    logging.debug('sampling is completed')
    np.savetxt("X1data.txt",X_train)
    np.savetxt("Y1data.txt",Y_train)
    classWeight=[]
    for i in range(len(Y_train)):
        if Y_train[i]==1:
            classWeight.append(1)
        else:
            classWeight.append(1)
    #svm设置和训练以及保存
    clf=svm.SVC(kernel='linear')
    clf.fit(X_train,Y_train,classWeight)
    joblib.dump(clf,"train_model.m")
    logging.debug('train_model is already trained')


def split_doc(argv):
    #dictionary+tfidf+lsi+svm_model load
    dictionary=corpora.Dictionary.load('wordDict1.dict')
    corpus_train=corpora.MmCorpus('wordDict1.mm')
    tfidf = models.TfidfModel(corpus_train)
    lsi=models.LsiModel.load('model1.lsi')
    clf=joblib.load('train_model.m')
    #读取未标识文本 转化成数组
    path=argv
    rdarray=pd.read_csv("test.csv", header=None)
    corpus_memory_friendly = MyCorpus1()
    corpus_tfidf = tfidf[corpus_memory_friendly]
    corpus_lsi = lsi[corpus_tfidf]
    X=[[s[1] for s in w]for w in corpus_lsi]
    X=pd.DataFrame(X)
    X=X.fillna(value=0)
    X_test=np.array(X)
    #svm模型预测和结果保存
    Y_predict=clf.predict(X_test)
    result=[]
    path1='./trueFile/'
    if not os.path.exists(path1):
        os.mkdir(path1)
    path2='./test_article/'
    for i in range(len(Y_predict)):
        filename=str(rdarray[0][i])+'.txt'
        f1=open(path2+filename,'r')
        context=f1.read()
        f1.close()
        if(len(context)<800):
            Y_predict[i]=0
        if Y_predict[i]==1:
            f1=open(path1+filename,'w')
            f1.write(context)
            f1.close()
	    result.append(str(rdarray[0][i])+','+str(Y_predict[i]))
    f=open('result.txt','w')
    f.write('\n'.join(result))
    f.close()
    logging.debug('result comes out!')
        
def main():
    readTrain()
    readTest()
    SplitW()
    train('./train_segfile2/')
    split_doc('./test_segfile2/')
    updataSql()
    
  
if __name__=='__main__':
    main()
