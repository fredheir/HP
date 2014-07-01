
# coding: utf-8

# In[ ]:

from hpfunctions import dateUp
from datetime import datetime
import lxml
from lxml import html,etree
import time
import urllib3
import sys
from hpfunctions import stripWhite, getUrl
from datetime import datetime
import re
import json


# In[ ]:

url='http://lifenews.ru/news/135725'
results=[]
n=15
while True:
    n+=1
    url='http://lifenews.ru/news/'+str(n)
    print url
    temp=getLifePage(url)
    if not temp is None:
        results.append(temp)
        print temp['views']
        print temp['nComments']


# In[ ]:

def getLifePage(url):
    d=getUrl(url)
    if '404 ' in d:
        print 'no page '+url
        return
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    tags= tree.xpath('//ul[@class="tags"]/li/a/text()')
    try:
        img= tree.xpath('//meta[@property="og:image"]')[0].get('content')
    except:img=None
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')
    text=tree.xpath('//div[@class="note"]/p/text()')
    text='\n'.join([i for i in text[1:]])
    date=tree.xpath('//time')[0].get('datetime')
    _id=url.split('/')[len(url.split('/'))-1]
    try:
        comments=getUrl('http://lifenews.ru/comments/post/'+str(_id))
        c=json.loads(comments)
    except:
        c=None
    entry={
    'title':title,
    'tags':tags,
    'img':img,
    'date':date,
    'url':url,
    'text':text,
    'comments':c,
    'views':tree.xpath('//div[@class="views"]/text()'),
'nComments':tree.xpath('//span[@class="counter"]/text()'),
    '_id':_id
    }
    return entry


# In[ ]:

len(results)
results[650]['date']


# In[ ]:



