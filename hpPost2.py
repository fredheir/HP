import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['hp']

from hpfunctions import stripWhite
from commentStats import *
import commentStats

for target in db.metadatadb.find({'typos':{'$exists':False}}):
	target['text'] = target.pop('body')
	target['text']=' '.join([i for i in target['text']])

	nWords,typos,caps,nPunct,words,nNames,pos= getBaseStats(target)
	try:
		errorRate=typos/float(nWords)
	except: errorRate =None
	print errorRate
	cleanString=' '.join([i.lower() for i in words if len(i)>2])
	db.metadatadb.update({'_id':target['_id']},{'$set':{
	                                            'cleanString':cleanString,
	                                            'errorRate':errorRate,
	                                            "nWords": nWords,
	                                            "typos": typos,
	                                            "caps": caps,
	                                            "nPunct": nPunct,
	                                            'namedEntities':pos,
	                                            "nNames": nNames
	                                            }})