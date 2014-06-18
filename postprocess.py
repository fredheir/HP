import pymongo
from pymongo import MongoClient
client=MongoClient()
db=client['hp']

from commentStats import *


comCount=0
entCount=1
for entry in db.metadatadb.find():
    if entCount%10==0:print 'n entries processed: '+str(entCount)
    if comCount%1000==0:print 'n comments processed: '+ str(comCount)
    entCount+=1
    for comment in entry["comments"]:
        comCount+=1
        _id=comment['_id']
        if 'shortPercentage' not in db.comStats.find({'_id':_id})[0]:
            break
        else:
            nWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
            for t in ['LOCATION','PERSON','ORGANIZATION']:
                if t in pos:
                    for i in pos[t]:
                        words+=i.split()
                        db.comStats.update({'_id':_id},{'$set':{t:pos[t]}})
                        
                        if len(words)>0:
                            shortPercentage=content_fraction(words)
                            db.comStats.update({'_id':_id},{'$set':{'words':' '.join(words),'shortPercentage':shortPercentage}})
                            print db.comStats.find({'_id':_id})[0]
                                 