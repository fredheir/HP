
# coding: utf-8

# In[18]:

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
targetDb='rt'
db = client['rus']
db[targetDb].create_index([("_id", pymongo.DESCENDING)])
# In[176]:

def checkField(field,target):
    return db[targetDb].find({field:target}).count()==0

def nextDay(d):
    dt=datetime.strptime(d, "%Y-%m-%d")
    return dateUp(dt).strftime("%Y-%m-%d")



# In[241]:

day=nextDay("2006-06-11")
def getDayLinks(day):
    cats=['news','uk','usa','op-edge','business']
    links=[]
    for i in cats:
        target='http://rt.com/'+i+'/'+day
        d=getUrl(target)
        myparser = etree.HTMLParser(encoding="utf-8")
        tree= etree.HTML(d, parser=myparser)
        links+=tree.xpath('//div[@class="content-wp"]//a[@class="header"]/@href')
        if len(links)==0:return links
        print str(len(links))+' targets found'
    return links



# In[247]:

# In[ ]:



#                 nextDay("2014-06-11")
# testPages=['http://rt.com/op-edge/165276-iraq-violence-usa-britain/',
#            'http://rt.com/news/169168-facebook-court-data-request/',
#            'http://rt.com/news/169156-us-denmark-turkey-rasmussen/',
#            'http://rt.com/usa/smartphone-application-community-three-762/',
#            'http://rt.com/usa/dozens-nyc-child-ring/',
#            'http://rt.com/usa/us-and-egypt-afraid-of-disruption-to-obama-visit/'
#            ]
# for url in testPages:
#     entry=getRtPage(url)
#     print entry['imageCaption']
                
# In[218]:

def getRtPage(url):
    d=getUrl(url)
    if 'You have typed the web address incorrectly' in d:
        return
    _ids=(url.split('/')[-2].split('-'))
    _id=None
    for i in _ids:
            try:
                _id=int(i)
            except:pass
    if _id is None:
        _id=int(d.split('var doc_id = ')[1].split(';')[0])
    if not checkField('_id',_id):
        return

    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')
    textImage= tree.xpath('//meta[@property="og:image"]')[0].get('content')
    try:
        author=tree.xpath('//div[@class="b-op_edge_authors"]/a/@href')[0].split('/')
        authorImage= tree.xpath('//div[@class="b-op_edge_authors"]/a/img/@src')[0]
        author=author[len(author)-2]
    except:
        author=authorImage=None
    date=stripWhite(tree.xpath('//span[@class="time"]')[0].text.split('Published time: ')[1])
    category=tree.xpath('//li[@class="active"]/a')[0].text
    tags=tree.xpath('//div[@class="b-tags_trends"]/div/a/text()')
    coms=rtComs(_id)
    imageCaption=None
    try:
        imageCaption=stripWhite(tree.xpath('//p[@class="article_img_footer"]/text()')[0])
    except:pass
    entry={
    'title':title,
    'image':textImage,
    'author':author,
    'authorImage':authorImage,
    'date':date,
    'category':category,
    '_id':_id,
    'tags':tags,
    'comments':coms,
    'body':tree.xpath('//div[@class="cont-wp"]/p/text()'),
    'imageCaption':imageCaption
    }
    return([entry])


# In[149]:

def rtComs(_id):
    import json
    coms=[]
    totP=2
    n=0
    while totP>n:
        comments=getUrl("http://rt.com/news/get-comments/?sort=newest&page="+str(n+1)+"&doc_id="+str(_id))
        c=json.loads(comments)
        try:
            totP=int(c['Body']['pager'].split('totalPages = ')[1].split(';')[0])
        except:totP=1
        coms+=c['Body']['comments']
        n+=1
    return coms



results=[]
day=nextDay("2006-07-01")
while True:
    targets=getDayLinks(day)
    for url in targets:
        url='http://rt.com/'+url
        out=(getRtPage(url))
        results+=out
    day=nextDay(day)
    print '\n\nNEW DAY!: '+str(day)
    if len (results)>0:
        print results
        archive(db,targetDb,results)
        results=[]

