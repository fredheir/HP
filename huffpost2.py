# -*- coding: utf-8 -*-
#from bs4 import BeautifulSoup

#Valid comparisons:
#Over time and commenting rule changes
#Us v UK

#Possible insight:
#does rulechange broaden debate by welcoming commenters from outside the thematic comfort zone, or does it close off commenting, leaving it to a smaller elite group that feels authorised to comment?
#do comment levels recover after a rule change?
#Are certain subjects more susceptible to spamming / self-censorship, and is this showsn by rule changes?



from hpfunctions import *
from commentStats import *
from datetime import date, timedelta, datetime


import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['hp']

db.metadatadb.create_index([("_id", pymongo.DESCENDING)])
d = datetime.strptime("20130101", "%Y%m%d")

# queue=loadQueue

# #write queue
# writeQueue(file="queue.txt",output=queue)


def archive(db,metaData):
	print ("entering metaData")
	if len (metaData)>0:
		try: 
			db.metadatadb.insert(metaData,continue_on_error=True)
		except pymongo.errors.DuplicateKeyError:pass


def checkAllIn(db,metaData):
	counter=0
	for i in range(len(metaData)):
		if db.metadatadb.find({"_id":metaData[i]["_id"]}).limit(1).count() ==0:
			print "missing meta: "+str(metaData[i]["_id"])
			counter+=1
	print("total number of missing entries: "+str(counter))

def findLastCompleteDay(db):
	minDate=20110101
	for i in db.metadatadb.find():
		try:
			t=int(i["date"])
		except:
			t=huffTime(i["date"])
		if t>minDate:
			minDate=t
	return(str(minDate))

#StartDate = findLastCompleteDay(db)
#d = datetime.strptime(StartDate, "%Y%m%d")
print "starting collection from "+str(d)

#metaData=addOneDay(d)
#tagdb={} #make this a list
todo=[]
metaData=[]
baseUrls=getBaseLinks(d)
while True:
	print("topping up")
	counter=0
	d=d+timedelta(days=1)
	print ("new Day!!: "+str(d))
	m=addOneDay2(d,baseUrls,db)
	todo=m
	print "new files added (should be at least twenty): "+str(len(todo))
	print("Comment downloading about to start. Number of articles downloaded and in queue for comment fetching: "+str(len(metaData)))
	for i in range(len(todo)):
		counter +=1
		_id=todo[i]["_id"]
		print "\nstarting file " +str(_id)
		if counter %10==0:
			print("Number of articles downloaded: "+str(len(metaData)))
			print("number of files before topup: "+str(len(todo)-counter))
		if type(_id) != 'NoneType' and db.metadatadb.find({"_id":_id}).limit(1).count() ==0  and todo[i]["url"] !="none":
			coms=commentSelector(d,_id,todo[i]["url"])
			comStats=getCommentStats(coms)		
			if len (comStats)>0:
				try: 
					db.comStats.insert(comStats,continue_on_error=True)
				except pymongo.errors.DuplicateKeyError:pass
			todo[i]["comments"]=coms
			todo[i]["nComments"]=len(coms)
		else: print "duplicated entry skipped"
		metaData.append(todo[i])

	#d=dateUp(d)
	archive(db,metaData)
	checkAllIn(db,metaData)
	metaData=[]


#Think about schema design: can i search tags? Also 
	#Add 

#Include workers
#merge tags with meta




#TOMORROW:
#Intead of aggregating into cmments, tagdb, done and metadata, save directly to db. Use lookup mechanism to see if article has been scraped. 


#C:\mongodb\bin\mongod.exe --dbpath c:\users\rolf\documents\conspDB\HP --setParameter textSearchEnabled=true
#create Schema
# commentSchema = Schema(_id=ID(stored=True),
#				 user_id=ID(stored=True), 
#				 created_at=ID(stored=True), 
#				 parent_id=ID(stored=True), 
#				 parent_user=ID(stored=True), 
#				 comment_id=ID(stored=True), 
#				 text=KEYWORD(stored=True))

# # Create index dir if it does not exists.
# if not os.path.exists("index3"):
#	 os.mkdir("index3")

# # Initialize index
# index = create_in("index2", schema)
# #index = INDEX.open_dir("index2")

# # Initiate db connection
# db = client['test-database']
# collection = db['test-collection2']
# print db.posts.index_information()

# writer = BufferedWriter(index,period=100,limit=500, writerargs = {"limitmb": 2048})


# for ID in todo:
#	 a,b,c,d,e,f,g=comments[1].values()
#	 counter+=1
#	 writer.add_document(content=unicode(text),nid=unicode(ID))


# #Freq
# from collections import Counter
# holder=[]
# for i in tagdb:
#	 holder+=tagdb[i]
# counts = Counter(holder)
# print(counts)
#Archiving process


# print len(urls)
# d=dateUp(d)


#id=getIds(url)

#To get article urls and ids
