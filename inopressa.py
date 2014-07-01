
# coding: utf-8

# In[2]:

from hpfunctions import dateUp
from datetime import datetime
import lxml
from lxml import html,etree
import time
import urllib3
import sys
from hpfunctions import stripWhite, getUrl, archive
from datetime import datetime
import re


import pymongo
from pymongo import MongoClient
client = MongoClient()
targetDb='rus'
db = client[targetDb]
db[targetDb].create_index([("_id", pymongo.DESCENDING)])




def getRubric(rubric):
    results=[]
    n=0
    cont=1
    while cont==1:
        targets=getTargets(rubric,n)
        if len(targets)<10:cont=0
        print 'page n '+str(n)
        n+=1
        for i in targets:
            url='http://www.inopressa.ru/'+i
            print url
            entry=getOne(url)
            entry['category']=rubric
            results.append(entry)
        print str(len(results))+' in results'
        archive(db,targetDb,results)
        results=[]
    
def getTargets(rubric,page):
    url='http://www.inopressa.ru/rubrics/'+rubric+'?page='+str(page)
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d)
    targets=tree.xpath('//div[@class="topic"]/h2/a/@href')
    return(targets)




# In[108]:

# In[96]:

def getOne(url):
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d)
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')

    author,source=tree.xpath('//h3/a/text()')[0].split(' | ')
    if not u'обзор' in author:
        origUrl=tree.xpath('//div[@class="source"]/a/@href')
    else:
        origUrl=tree.xpath('//div[@class="body"]//a/@href')
    
    date=url.split('article/')[1].split('/')[0]
    date=datetime.strptime(date, "%d%b%Y")
    text=tree.xpath('//div[@class="body"]/p/text()')
    text = ''.join([i for i in text])
    text=re.sub('\r','\n',text)
    entry={
    'title':title,
    'author':author,
    'origUrl':origUrl,
    'date':date,
    'url':url,
    'text':text
    }
    return entry

# In[106]:

rubrics=['russia','sport','culture','incident','peace',
         'economics','war','different','science',
         'extremal','neareast','law','analytics']


for i in rubrics:
    print i
    getRubric(i)


