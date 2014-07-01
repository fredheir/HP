
# coding: utf-8

# In[244]:

import lxml
from lxml import html, etree
import time
import urllib3
import sys
from hpfunctions import stripWhite, getUrl,archive

import pymongo
from pymongo import MongoClient
client = MongoClient()
targetDb='inosmi'
db = client['rus']
db[targetDb].create_index([("_id", pymongo.DESCENDING)])



def getMonth(t):
    t=str(t)
    a=int(t[0:4])
    b=int(t[-2:])
    if b==12:
        b=1
        a+=1
    else:
        b+=1
    if b<10:
        b='0'+str(b)
    return str(a)+str(b)

def getPage(mn,verbose=0):
    print mn
    cont=1
    results=[]
    pn=1
    while cont==1:
        url='http://inosmi.ru/archive/'+str(mn)+'/index_'+str(pn)+'.html'
        d=getUrl(url)
        myparser = etree.HTMLParser(encoding="utf-8")
        tree= etree.HTML(d, parser=myparser)
        targets=[]
        targets=tree.xpath("//div[@class='lenta']/ul[@class='r_main']/li/a/@href")
        targets+= tree.xpath("//div[@class='lenta']/ul[@class='r_main']/li/div/div/h3/a/@href")
        if len(targets)==0:
            cont=0
            print 'all done here! moving on'
        else:
            print 'New targets found!: '+str(len(targets))+' links to go '+url
            pn+=1
        for target in targets:
            if not '/overview/' in target:
                new=getEntry('http://inosmi.ru'+target,verbose)
                #print new['title']
                results.append(new)
        archive(db,targetDb,results)




# In[541]:

def getEntry(url,verbose=0):
    import re
    dat=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(dat, parser=myparser)
    title= tree.xpath("//h1[@class='inline']/text()")[0]
    try:
        author= tree.xpath("//div[@class='source_authors']/text()")[0]
    except:author=''
    try:
        origUrl=tree.xpath("//div[@class='original']/p/a/@href")[0]
    except:
        origUrl=None
        if verbose==1:print 'link to original not found: '+url
    try:
        origDate=tree.xpath("//div[@class='original']/p[2]/text()")[0].split(': ')[1]
    except:origDate=None
    date=tree.xpath("//p[@class='date2']/span/text()")[0]
    country=publication=None
    try:
        publication = tree.xpath("//div[@class='article_issue_title inline']/a/text()")[0]
        country =  tree.xpath("//div[@class='article_issue_title inline']/a/text()")[1]
    except:
        if ':' in title:
            temp=title.split(':')
            title=temp[1]
            pub=temp[0]
            if verbose==1:print 'alternative source info found: '+temp[0]
            try:
                publication=pub.split(u'"')[1]
                if '(' in temp:
                    country=pub.split('(')[1].split(')')[0]
            except:publication=pub

        else: 
            if verbose==1: print'NO SOURCE INFO FOUND'

    try:
        nComments= int(tree.xpath("//div[@class='leftclear']/div[@class='comment orang']/span/text()")[0])
    except:nComments=0
    try:
        imgUrl=tree.xpath("//div[@class='img-wrap']/img/@src")[0]
    except:imgUrl=None
    text= tree.xpath("//div[@class='leftclear']/p/text()")
    translator=None
    for para in text:
        if u'Перевод: ' in para:
            translator=para.split(u'Перевод: ')[1]
    text='\n'.join(text)
    com=tree.xpath("//ul[@class='tree']/li")
    comments=getAllComments(com)
    entry={
    'title':title,
    'author':author,
    'origUrl':origUrl,
    'origDate':origDate,
    'publication':publication,
    'date':date,
    'country':country,
    'nComments':nComments,
    'imgUrl':imgUrl,
    'text':text,
    'comments':comments,
    'url':url,
    '_id':int(url.split('/')[len(url.split('/'))-1].split('.')[0]),
    'category':url.split('/')[3],
    'translator':translator,
    'source':inosmi
    }
    return(entry)


# In[318]:

def getSubComments(url,parent):
    dat=getUrl(url)
    from lxml import etree
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(dat, parser=myparser)
    commentChild=tree.xpath("/html/body/ul/li")
    out=getSubComment(commentChild,'test')
    return out

def getSubComment(commentChild,parent):
    out=[]
    for comment in commentChild:
        comDate= comment.find('span[@class="date"]').text
        comBod= comment.find('div[@class="body"]').text
        user= comment.find('div[@class="header"]/span').text
        userId,comId=comment.find('div[@class="header"]/span').get('id').split('_')[1:3]
        title= comment.find('div[@class="header"]/strong').text
        parent=parent
        out.append({
                    'comDate':comDate,
                    'comBod':comBod,
                    'user':user,
                    'userId':userId,
                    'title':title,
                    'parent':parent
                    })
        if comment.find('ul') is not None:
            out+= (getSubComment(comment.find('ul'),userId))
    return out



# In[316]:

def getAllComments(comments):
    results=[]
    for comment in comments:
        try:
            comDate= comment.find('span[@class="date"]').text
            comBod= comment.find('div[@class="body"]').text
            user= comment.find('div[@class="header"]/span').text
            userId,comId=comment.find('div[@class="header"]/span').get('id').split('_')[1:3]
            title= comment.find('div[@class="header"]/strong').text
            parent='root'
            results.append({
                        'comDate':comDate,
                        'comBod':comBod,
                        'user':user,
                        'userId':userId,
                        'title':title,
                        'parent':parent
                        })
            results+=getSubComments('http://inosmi.ru'+comment.find('div[@class="foot"]/span/a').get('rel'),userId)
        except:pass
    return results






# In[ ]:

keep=[]
d=200601
while True:
    keep+=(getPage(d,verbose=1))
    d=getMonth(d)

