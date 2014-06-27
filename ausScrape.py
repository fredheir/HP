import lxml
from lxml import html
import time
import urllib3
import sys
from hpfunctions import stripWhite, getUrl
from commentStats import *
import commentStats
import sys
from datetime import date, timedelta, datetime
import pymongo
from pymongo import MongoClient

def getStats(target):
	nWords,typos,caps,nPunct,words,nNames,pos= getBaseStats(target)
	try:
		errorRate=typos/float(nWords)
	except: errorRate =None
	print errorRate
	cleanString=' '.join([i.lower() for i in words if len(i)>2])
	return {
												'cleanString':cleanString,
												'errorRate':errorRate,
												"nWords": nWords,
												"typos": typos,
												"caps": caps,
												"nPunct": nPunct,
												'namedEntities':pos,
												"nNames": nNames
												}

client = MongoClient()
db = client['aus']
db.aus.create_index([("_id", pymongo.DESCENDING)])


def archive(metaData):
	print ("entering scraped")
	if len (metaData)>0:
		try: 
			db.aus.insert(metaData,continue_on_error=True)
		except pymongo.errors.DuplicateKeyError:pass


#USE: sourcedate


def getText(textUrl):
	string=getUrl(textUrl)
	string=getUrl(textUrl)
	tree = html.fromstring(string)
	a=tree.xpath("//div/p/span/text()")
	d=''.join(['\n'+line[2:len(line)] for line in a])
	d= re.sub('-\n','',d)
	return d

def getTextUrl(link):
		a=link.split("article/")[1]
		a=a.split("?")[0]
		return 'http://trove.nla.gov.au/ndp/del/text/'+str(a),a


def addTwenty(target,targetDate):
	pageN=int(target*20)
	if db.aus.find({'sourcePage':pageN}).count()>0:
		return
	url = "http://trove.nla.gov.au/newspaper/result?q=conspiracy&s="+str(pageN)+'&sortby=dateAsc&dateFrom='+targetDate
	print url
	dat=getUrl(url)
	tree = html.fromstring(dat)
	
	links=[]
	for link in tree.xpath('//a/@href'):
		try:
			if "ndp/del/" in str(link): 
				links.append(link)
		except:pass

	results=[]
	searchDate=""
	for n in range(1,21):
			target=tree.xpath("//ol/li["+str(n)+"]/dl/dd/div")
			relScore=float(target[len(target)-1].text_content().split('score: ')[1].split(')')[0])
			dateString=tree.xpath("//ol/li["+str(n)+"]/dl/dd/strong")[0].text_content()
			sourceFull=tree.xpath("//ol/li["+str(n)+"]/dl/dd/em")[0].text_content()
			source=sourceFull.split(' (')[0]
			target=tree.xpath("//div/ol/li[@class='article ']["+str(n)+"]/dl/dt/a")
			title=stripWhite(target[len(target)-1].text_content())
			textUrl,_id=getTextUrl(links[n])
			targetText=getText(textUrl)
			t={'text':targetText}
			df=datetime.strptime(dateString,"%A %d %B %Y")
			searchDate= str(df).split(' ')[0]
			ts=int(re.sub('-','',searchDate))
			
			stats=getStats(t)
			stats['title']=title
			stats['dateString']=dateString
			stats['relevanceScore']=relScore
			stats['sourceFull']=sourceFull
			stats['source']=source
			stats['textUrl']=textUrl
			stats['rawText']=targetText
			stats['_id']=_id
			stats['sourcePage']=pageN
			stats['ts']=ts
			stats['searchDate']=searchDate
			print str(stats['_id'])+': '+dateString+' ' +' '+title+ ' nWords: '+str(stats['nWords'])
			results.append(stats)
	archive(results)
	results=[]
	return(searchDate)

		
def main(argv=None):#take input file
	print 'welcome to the aussie scraper! starts on page 0 by default'		
	if argv is None: argv =sys.argv
	if argv[1:]:
		target=int(argv[1])
	else:target=1


	targetDate=""
	while True:
		print 'starting page '+str(target)
		if target>50:
			print 'resetting'
			print searchDate
			targetDate=searchDate
			target=0
		temp=addTwenty(target,targetDate)
		if len(temp)>3:
			searchDate=temp
		target+=1
	

if __name__ == "__main__":
	sys.exit(main())
	