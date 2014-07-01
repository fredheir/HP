
# coding: utf-8

# In[1]:

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


# In[464]:

def getEntry(url):
    d=getUrl(url)
    if "We've been notified about this issue and we'll take a look at it shortly." in d:
        return
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    tags= tree.xpath('//div[@class="tags"]/a/text()')
    img= tree.xpath('//meta[@property="og:image"]')[0].get('content')
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')
    text=tree.xpath('//span[@class="_ga1_on_ contextualizable"]/text()')
    text=('\n'.join([stripWhite(i) for i in text[1:]]))
    date=tree.xpath('//div[@class="topic"]/div[@class="date"]/text()')[0]
    _id=url.split('-echo/')[0].split('/')[-1]
    progSeries=tree.xpath('//div[@class="descr"]/h1/a/text()')
    author=stripWhite(' '.join(tree.xpath('//dl[@class="autorBlock"][1]//div[@class="autor"]/a/text()')))
    entry={
        'title':title,
        'tags':tags,
        'authImg':img,
        'date':date,
        'url':url,
        'text':text,
        'comments':c,
        'views':int(tree.xpath('//span[@class="icInfo icView"]/text()')[0]),
        'nComments':int(tree.xpath('//div[@class="block1"]/dl//a[@class="icInfo icComment"]/text()')[0]),
        'nLikes':int(tree.xpath('//a[@class="icInfo icLike"]/b/text()')[0]),
        '_id':_id,
        'progSeries':progSeries,
        'author':author
    }
    return entry


# In[465]:

def getBase(url):
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    dat= tree.xpath('//ul[@class="comments"]')[0]
    return dat


# In[466]:

def getCom(base,parentCom,parentUser):
    results=[]
    for com in base.xpath('li'):
        date= com.xpath('div/div[@class="descr"]/div/text()')
        date=' '.join(stripWhite(i) for i in date)
        entry={
            'comId' : com.get('id').split('cmnt-')[1],
            'userId':com.xpath('div/@ data-author')[0],
            'deleted':True,
            'parentCom':parentCom,
            'parentUser':parentUser
        }
        text=com.xpath('div/div[@class="descr"]/text()')[1:]
        text='\n'.join(stripWhite(i) for i in text)
        try:
            entry['userName']= com.xpath('div/div[@class="autor user"]/a/@href')[0].split('/')[-2]
            entry['date']=date
            entry['text']= text#stripWhite(com.xpath('div/div[@class="descr"]/text()')[1])
            entry['rating']= int(com.xpath('div/ul/li/a/b/text()')[0])
            entry['deleted']=False
            entry['avatar']='http://www.echo.msk.ru'+com.xpath('div/div/a/img/@src')[0].split('?')[0]
        except:pass

        results.append(entry)
        if len(com.xpath('ul/li'))>0:
            target=com.xpath('ul')[0]
            results+=getCom(target,entry['comId'],entry['userId'])
    return(results)
        #date=' '.join(i for i in date)


# In[467]:

def getOne(url):
    entry=getEntry(url)
    if entry is None:
        return
    cont=1
    n=0
    coms=[]
    while cont==1:
        comUrl='http://www.echo.msk.ru/elements/'+str(entry['_id'])+'/comments_page/'+str(n)+'.html'
        print comUrl
        base=getBase(comUrl)
        com=getCom(base,0,0)
        print len(com)
        if len(com)==0:
            cont=0
        else:
            n+=1
        coms+=com
    entry['comments']=coms
    print 'number of comments found: '+str(len(coms))
    return entry


# In[473]:

def getTargets(url):
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    targets=tree.xpath('//dl[@class="topBlock"]//div[@class="descr"]/a/@href')
    if len (targets)==0:
        targets=tree.xpath('//div[@class="centerright"]//div[@class="text1"]/a/@href') 
    targets=[i for i in targets if 'polls' not in i and 'inopress' not in i]
    return targets


# In[474]:

results=[]
root='http://wayback.archive.org/web/20100106044345/http://echo.msk.ru/'
url=root
targets=getTargets(url)
for i in targets:
    url=root+i
    url='http'+url.split('http')[-1]
    print url
    temp=getOne(url)
    if not temp is None:
        temp['type']='blog'
        if 'blog' not in url:
            temp['type']='radio'
        results.append(temp)
        print len (results)
        print temp['type']


# In[472]:

targets


# In[459]:

'tse'+t.split('tse')[-1]


# In[ ]:



