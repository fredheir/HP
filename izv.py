# coding: utf-8

from hpfunctions import dateUp, dateDown
from datetime import datetime
import lxml
from lxml import html,etree
import time
import urllib3
import sys
from hpfunctions import stripWhite, getUrl, archive
from datetime import datetime
import re
import locale


import pymongo
from pymongo import MongoClient
client = MongoClient()
targetDb='izv'
db = client['rus']
db[targetDb].create_index([("_id", pymongo.DESCENDING)])


sections={       
   15:'politics',   19:'society',   16:'economics' , 17:'world',  23:'moscow',
   28:'army',   24:'science',   25:'gadgets and telekom',   18:'culture',
   21:'sport',   22:'unclassified',   26:'N',   27:'spetsproekty',
   28:'army', 30:'property', 31:'vkusno!',32:'health',33:'metallurgiia',
   35:'transport',36:'energy',37:'it',38:'finance',39:'tekhnoparki',40:'education',
   41:'tourism',42:'abiturient',43:"malen'kaia_Strana",44:'ecology',45:'railroads',
   46:'investment_and_construction',47:'Russia-regions',48:'gifts',50:'investment',51:'integration',
   52:'avto',53:'mfgs',54:'innovation',55:'unnamed_(oil)',56:'maks_2013',57:'panorama_taivania',
   62:'knauf',64:'grazhdanskaia_aviatsiia',66:'avto(2)',69:'property(2)',76:'oil_and_gas',
   77:'formula_liderstva'
   }

types={
    0:'news',1:'statei',2:"interv'iu",3:'reportazhei',4:'mnenii',5:'infografika',7:'interaktivy'
}


conv={}
for (n, month) in enumerate(u'января, февраля, марта, апрелья, мая, июня, июля, августа, сентября, октября, ноября, декабря'.split(', '), 1):
    conv[month]=n
def izvDate(date,year):
    day,month,ts=date.split()
    month=conv[month[:-1]]
    date=day+'-'+str(month)+'-'+year+' '+ts
    return date



def getIzvComs(_id,year):
    _id=560985
    import json
    #nPages=1
    n=0
    coms=[]
    cont=0
    while cont==0:
        url="http://izvestia.ru/comments?module_id=164&element_id="+str(_id)+"&action=AjaxShowComments&p="+str(n+1)
        comments=getUrl(url)
        c=json.loads(comments)
        
        d=c['comments']
        myparser = etree.HTMLParser(encoding="utf-8")
        tree= etree.HTML(d, parser=myparser)
        target=tree.xpath('//li')[0].get('cid')
        for com in coms:
            if int(com['comId'])==int(target):
                cont=1
        if cont==0:
            for com in tree.xpath('//li'):
                cid= int(com.get('cid'))
                level=int(com.get('data-level'))
                text= com.xpath('p/text()')[0]
                userName = com.xpath('div/span/text()')[0]
                date= izvDate(com.xpath('div/text()')[0][2:],year)
                #for i in com:
                #    print (i.xpath('//p/text()'))[0]
                entry={
                       'comId':cid,
                       'level':level,
                       'text':text,
                       'userName':userName,
                       'date':date,
                       }
                coms.append(entry)
        n+=1
    return coms

def checkField(field,target):
    return db[targetDb].find({field:target}).count()==0

def getIzvEntry(url):
    _id = int(url.split('/')[-1])
    if not checkField('_id',_id):
        return
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    
    title= tree.xpath('//meta[@property="og:title"]')[0].get('content')
    textImage= tree.xpath('//meta[@property="og:image"]')[0].get('content')
    try:
        author=tree.xpath('//a[@itemprop="author"]/text()')[0]
    except:author=None
    try:
        sub=tree.xpath('//h2[@class="subtitle"]//text()')[0]
    except:sub=''
    text=tree.xpath('//div[@class="text_block"]/p/text()')
    text=sub+'\n'.join([i for i in text if i != sub])
    #date=tree.xpath('//span[@class="info_block"]')[0].get('datetime')
    date=tree.xpath('//span[@class="info_block_date"]/time/@datetime')[0]
    nComs=0
    try:
        nComs=int(tree.xpath('//a[@class="info_link_comments"]/span/text()')[0])
    except:
        coms=[]
        pass
    if nComs>0:
        coms=getIzvComs(_id,date.split('-')[0])
    imageCaption=None
    try:
        imageCaption=stripWhite(tree.xpath('//div[@class="img_block "]/p/text()')[0])
    except:pass
    ad=0
    if len(tree.xpath('//h1/span[@class="adv_sign"]'))>0:
        ad=1
        
    entry={
               'title':title,
               'image':textImage,
               'author':author,
               'date':date,
               '_id':_id,
               'comments':coms,
               'body':text,
               'imageCaption':imageCaption,
               'url':url,
               'ad':ad   
                  }
    return entry



def getTargets(section,t,pn):
    url='http://izvestia.ru/archive/'+str(section)+'?type='+str(t)+'&p='+str(pn)
    print url
    d=getUrl(url)
    myparser = etree.HTMLParser(encoding="utf-8")
    tree= etree.HTML(d, parser=myparser)
    targets=[]
    try:
        targets=tree.xpath('//div[@class="items_list"]//h3/a/@href')
        targets=list(set(targets))
    except:pass
    return targets


#for i in sections
try:
    dummy=db[targetDb].find({'_id':0})[0]
    print dummy['lastPage']
except:dummy={}
if 'lastSection' not in dummy:
    dummy['_id']=0
    dummy['lastSection']=sections.keys()[0]
    dummy['lastType']=types.keys()[0]
    dummy['lastPage']=1
    db[targetDb].insert(dummy)
s1=0
s2=0
results=[]
for section in sections:
    if section==dummy['lastSection']:
        s1=1
    for t in types:
        if t==dummy['lastType']:
            s2=1
            print True
        if s1==1 and s2 ==1:
            print sections[section]+ ' : '+ types[t]
            prev=[]
            cont=True
            pn=1
            if section ==dummy['lastSection'] and t==dummy['lastType']:
                pn=dummy['lastPage']
                print pn
            while cont==True:
                targets=getTargets(section,t,pn)
                if len(targets)==0 or targets[0] in prev:
                    cont=False
                    pass
                else:
                    cc=False
                    for i in targets:
                        if cc==False:
                            print i
                            entry=getIzvEntry('http://izvestia.ru'+i)
                            if entry is None:
                                cc=True
                            else: 
                                entry['section']=sections[section]
                                entry['category']=types[t]
                                results.append(entry)
                    if len (results)>0:
                        print str(len(results)) +' to file away'
                        archive(db,targetDb,results)
                        results=[]
                        db[targetDb].update({'_id' : 0}, { '$set':{
                                'lastSection': section,
                                'lastType':t,
                                'lastPage':pn
                                }})
                prev=targets
                pn+=1
        else: print 'skipping'