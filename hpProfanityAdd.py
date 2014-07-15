#Upon revisiting the code, set the profanities to the comment, that way much quicker extraction
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
from hpfunctions import file_contents
client=MongoClient()
db=client['hp2']
print db.comStats.find().count()

#FOR working with data about profanity
queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]
db.comStats.create_index('entry_id')
db.metadatadb.create_index('category')

counter=0
for ref in db.metadatadb.find():
    temp1=[]
    temp2={}
    #if ref['category'] in target:
    counter+=1
    if counter%100==0:print str(float(counter)/1000.0)+' thousand'
    if 'profNodes' not in ref:
            for ent in db.comStats.find({'entry_id':ref['_id']}):
                    #print ent['entry_id']
                    terms=ent['words'].lower().split()
                    found= [t for t in terms if t in profanity]
                    #nodesCalc
                    if len(found)>0:
                        for i in found:
                            if i not in temp2:
                                temp2[i]=[]
                            temp2[i].append(ent['created_at'])


                    #Edges calc
                    if len (found) >1:
                        d=list(set(found))
                        for i in range(len(d)):
                            for j in d[i:]:
                                if d[i] !=j:
                                    try:
                                        entry= {'created_at':ent['created_at'],
                                            'parent_id':ent['parent_id'],
                                            'entry_id':ent['entry_id'],
                                            'user_id':ent['user_id'],
                                            'source':d[i],
                                            'target':j
                                            }
                                    except:pass
                                    temp1.append(entry)

    db.metadatadb.update({'_id':ref['_id']},{'$set':{
'profEdges':temp1,
'profNodes':temp2
}})
