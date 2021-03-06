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
from dateutil.relativedelta import relativedelta
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
targetDb='aus2'
db[targetDb].create_index([("_id", pymongo.DESCENDING)])


def archive(metaData):
    print ("entering scraped")
    if len (metaData)>0:
        try: 
            db.aus2.insert(metaData,continue_on_error=True)
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
    url = "http://trove.nla.gov.au/newspaper/result?q=conspiracy&s="+str(pageN)+'&sortby=dateAsc&dateFrom='+targetDate
    print url
    dat=getUrl(url)
    links=[]
    tree = html.fromstring(dat)
    for link in tree.xpath('//a/@href'):
        try:
            if "ndp/del/" in str(link): 
                links.append(link)
        except:pass
    textUrl,_id=getTextUrl(links[-1])
    refId=int(_id)
    print _id
    if not db[targetDb].find({'_id':refId}).count()==0:
        links=[]
        print 'found '+str(len(tree.xpath('//a/@href')))+' but all in database. Moving on.'

    #results=[]
    searchDate=""
    if len (links)>0:
        for n in range(1,21):
            try:
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
                stats['_id']=int(_id)
                stats['sourcePage']=pageN
                stats['ts']=ts
                stats['searchYear']=int(searchDate.split('-')[0])
                print str(stats['_id'])+': '+dateString+' ' +' '+title+ ' nWords: '+str(stats['nWords'])
                #results.append(stats)
                db.aus2.insert(stats)
            except:pass
    #archive(results)
    #results=[]
    print refId
    try:
        return(ts)
    except:
        return(db[targetDb].find({'_id':refId})[0]['ts'])

		
def main(argv=None):#take input file
	print 'welcome to the aussie scraper! starts on page 0 by default'		
	if argv is None: argv =sys.argv
	if argv[1:]:
		targetDate=(argv[1])
	else:
	    	targetDate= '1804-01-01'

	if db[targetDb].find({'_id' : 0}).count()==0:
	    entry={
	        '_id':0,
	        'seen':[]
	    }
	    db[targetDb].insert(entry)

	target=0
	while True:
	    tester=targetDate[:7]
	    seen=db[targetDb].find({'_id' : 0})[0]['seen']
	    if tester not in seen:
	        print 'starting page '+str(target)
	        if target>90:
	            print 'resetting'
	            searchDate=temp
	            print searchDate
	            targetDate=searchDate
	            target=0
	        temp=addTwenty(target,targetDate)
	        temp=str(temp)
	        temp=temp[0:4]+'-'+temp[4:6]+'-'+temp[7:]
	        print temp
	        if temp[:7] != tester:
	            print 'Inserting date. found new date : ' +temp[:7]
	            db[targetDb].update({'_id' : 0}, { '$push':{'seen': tester}})

	        target+=1
	    else:
	        formattedDate=datetime.strptime(targetDate,"%Y-%m-%d")
	        targetDate = formattedDate+ relativedelta(months=1)
	        targetDate=str(targetDate).split()[0]
	        target=1
	        print targetDate

	

if __name__ == "__main__":
	sys.exit(main())
	