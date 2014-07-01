
# coding: utf-8

# In[ ]:

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
targetDb='tv1'
db = client['rus']
db[targetDb].create_index([("_id", pymongo.DESCENDING)])
# In[ ]:

def getOneEntry(url):
    d=getUrl(url)
    _id=url.split('/')[-1]
    tree= etree.HTML(d)
    tags= tree.xpath('//meta[@name="keywords"]')[0].get('content')
    vidUrl=img=vidLen=None
    try:
        vidUrl= tree.xpath('//meta[@property="og:video:url"]')[0].get('content')
        img= tree.xpath('//meta[@property="og:image"]')[0].get('content')
        vidLen= int(tree.xpath('//meta[@property="og:video:duration"]')[0].get('content'))
    except:pass
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')

    text=tree.xpath('//div[@class="n_article-txt"]/p/text()')
    text='\n'.join([i for i in text[1:]])
    author=None
    try:
        author=tree.xpath('//div[@class="txt"]/a/text()')[0]
    except:pass
    date=stripWhite(tree.xpath('//h4/span/text()')[0])
    time=stripWhite(tree.xpath('//h4/span/strong/text()')[0])
    print time
    entry={
    'title':title,
    'tags':tags,
    'vidUrl':vidUrl,
    'vidLen':vidLen,
    'imgUrl':img,
    'date':date,
    'url':url,
    'text':text,
    'author':author,
    '_id':_id,
    'time':time
    }
    return entry


def getTargets(section,page):
    url='http://www.1tv.ru/newsarchive_l/'+section+'/page'+str(page)
    print url
    d=getUrl(url)
    tree= etree.HTML(d)
    targets=tree.xpath('//div[@class="n_list-news"]//div[@class="img"]/a/@href')
    return(targets)

def getSection(section):
    results=[]
    n=1
    cont=1
    while cont==1:
        targets=getTargets(section,n)
        if len(targets)<10:cont=0
        print 'page n '+str(n)
        n+=1
        for i in targets:
            url='http://www.1tv.ru/'+i
            if db[targetDb].find({'url':url}).count()==0:
                print url
                entry=getOneEntry(url)
                entry['category']=section
                results.append(entry)
            else: print 'passing'
        print str(len(results))+' in results'
        archive(db,targetDb,results)


# In[ ]:

section=['polit','election','economic','social','world','crime',
         'techno','health','culture','sport','other','odnako','zaprotiv','weather']

for i in section:
    getSection(i)


# In[ ]:



