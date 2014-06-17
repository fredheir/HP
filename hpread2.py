#hp reading

from datetime import date, timedelta, datetime
from hpfunctions import *


import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['hp-database']
counter=0
writer=open("hpOut.txt","a")
for i in db.metadatadb.find({'timestamp':{'$exists': True},'nComments':{'$exists': True},'timestamp':{'$regex':'^201406'}}):
	counter+=1
	out=i["timestamp"]
	#out=formatDate(t)
	comCount=int(i["nComments"])
	category=i["category"]
	title=i["title"]
	try:
		tags=i["tags"]
	except:tags=["missing"]
	author=i["author"]
	t=""

	for tag in tags:
		t+=tag+","
	t=t.replace(u"\xe9",u"e")
	t=t.replace(u"\n"," ")
	t=t.replace(u"\t"," ")
	t=t.replace(u'"',"")
	title=title.replace(u'"',"")
	title=title.replace(u"\t"," ")
	title=title.replace(u";"," ")
	t=t.replace(u";"," ")
	if comCount>0:
		writer.write(
			str(i["_id"])+"\t"+
			str(out.encode("utf-8"))+"\t"+
			str(category.encode("utf-8"))+"\t"+
			str(title.encode("utf-8"))+"\t"+
			str(author.encode("utf-8"))+"\t"+
			str(t.encode("utf-8"))+"\t"+
			str(comCount)+
			"\n")
	if counter %100==0:print counter

writer.close()
