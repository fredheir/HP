#hp add body and tags
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
client=MongoClient()
db=client['hp']

for i in db.metadatadb.find({'body': {'$size': 0}}):
    url=i['url']
    rx=getUrl(url)
    tree = html.fromstring(rx)
    body=tree.xpath("//*[@class='entry_body_text']/p")
    if len(body) ==0:
        body= tree.xpath("//*[@class='articleBody']/p")
    if len(body) ==0:
        body= tree.xpath("//*[@id='mainentrycontent']/p")
    if len(body) ==0:
        body= tree.xpath("//*[@class='content']/p")
    if len(body) ==0:
        body= tree.xpath("//*[@class='news_main_info']/p")
    if len(body) ==0:
    	body=tree.xpath("//div[contains(@class,'entry_body_text')]/p")
    bod=[]
    for line in body:
        bod.append(line.text_content())
    if len(bod)==0: 
        print 'body not found: '+str(url)
    db.metadatadb.update({'url':url},{'$set':{'body':bod}})
    try:
	    tags= tree.xpath("//div[contains(@class,'follow_tags')]/span")[0].text_content().split(",")
	    t=[]
	    for i in tags:
	        t+=[i.replace(u'\xa0', u'').lstrip()]
	    t=stripWhiteList(t)
    except: t=tree.xpath("//div[contains(@class,'follow_tags')]/a/text()")
    if len(t)==0:
        t= tree.xpath("//span[@class='group']/span/a/text()")
        print t
        db.metadatadb.update({'url':url},{'$set' : {'tags':t}})
