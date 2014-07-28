#Upon revisiting the code, set the profanities to the comment, that way much quicker extraction
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
client=MongoClient()
db=client['hp3']

#FOR working with data about profanity
from hpfunctions import file_contents
queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]
print db.comStats.find().count()
db.comStats.create_index('entry_id')
db.metadatadb.create_index('category')

#Add profanity words seen in the root article, don't include these when merging
queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]
db.comStats.create_index('entry_id')
db.metadatadb.create_index('category')
errors=0

from hpCommentStats import getBaseStats
counter=0
for ent in db.metadatadb.find():
    print 'started'
    counter+=1
    if counter%100==0:print counter
    if 'offensive' not in ent:
        if len(ent['body'])==0:
            errors+=1
            print 'error'
        else:
            comment={'text':ent['body'][0]}
            nRecWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
            found= [t for t in words if t in profanity]
            offensive=list(set(found))
            result={
            "nRecWords": nRecWords,
            "typos": typos,
            "nCaps": caps,
            "nNames":nNames,
            "names":pos,
            "offensive":offensive
            }
            if len(offensive)>0:print offensive
            db.metadatadb.update({'_id':ent['_id']},{'$set':result})