import lxml
from lxml import html
import time
import urllib3
import sys

def getUrl(url):
	http = urllib3.PoolManager()
	rx = http.request('GET', url).data
	return(rx)

def getBaseLinks(searchTerm,n):
    url = "http://chroniclingamerica.loc.gov/search/pages/results/list/?date1=1836&rows=100&searchType=basic&state=&date2=1922&proxtext="+searchTerm+"&y=0&x=0&dateFilterType=yearRange&page="+str(n)+"&sort=date"
    dat=getUrl(url)
    parsed=html.fromstring(dat)
    links=[]
    for link in parsed.xpath('//a/@href'):
        if "lccn/sn" in link: 
            links.append(link)
    newLinks=[]
    for link in links:
        a=link.split("#")[0]
        a=a.split(";")[0]
        a="http://chroniclingamerica.loc.gov/"+a+"ocr"
        newLinks.append(a)
    return(newLinks)

import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['cd']
db.cd.create_index([("_id", pymongo.DESCENDING)])


def archive(db,metaData):
    print ("entering scraped")
    if len (metaData)>0:
        try: 
            db.cd.insert(metaData,continue_on_error=True)
        except pymongo.errors.DuplicateKeyError:pass


def downloadOne(searchTerm,url):
    dat= getUrl (url)
    tree = html.fromstring(dat)
    string= tree.xpath("//div/h1/text()")[1]

    title=string.split(".")[0]
    place=string.split("(")[1].split(")")[0]
    date=string.split(",")[-3:][0:2]
    date=date[0]+date[1]
    print date
    body=tree.xpath("//div/p/text()")

    dict={"date": date,
          "url":url,
          "publication":title,
          "site":"chroniclingamerica",
          "text":body,
          "searchTerm":searchTerm,
          "titleHeader":string
          }
    return(dict)

def executeScript(target):
    target=int(target)
    toArchive=[]
    counter=0
    searchTerm="conspiracy"
    while True:
            print ("getting new target links")
            newLinks=getBaseLinks(searchTerm,target)
            for i in newLinks:
                counter+=1
                cont=0
                while cont==0:
                    try:
                        toArchive.append(downloadOne(searchTerm,i))
                        cont=1
                    except:
                        time.sleep(15)
                if counter%10==0:
                    counter=0
                    archive(db,toArchive)
                    toArchive=[]
            target+=1


def main(argv=None):#take input file
    print 'welcome to the cmd version of the conspiracy in america scraper. lets get cracking. Enter target page, or start at 1'
    if argv is None:
        argv =sys.argv
        
    if argv[1:]:
        target=argv[1]
    else:target=1

    print executeScript(target)
    

if __name__ == "__main__":
    sys.exit(main())
