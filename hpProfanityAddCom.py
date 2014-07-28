#Upon revisiting the code, set the profanities to the comment, that way much quicker extraction
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
from hpfunctions import file_contents
client=MongoClient()
db=client['hp3']
print db.comStats.find().count()

#FOR working with data about profanity
queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]
db.comStats.create_index('entry_id')
db.metadatadb.create_index('category')

def interactAndProfanity(ref):
    participants={}
    rootComsSeen=[]
    rootComsUnseen=[]
    nReplies=nComs=0
    nAdopted=0
    nOrphans=0
    nTotSeen=0
    temp1=[]
    temp2={}
    
    #part 2 
    
        
    
    
    for ent in db.comStats.find({'entry_id':ref['_id']}):
        #Interactions
        nTotSeen+=1
        if ent['parent_id']==0:
            nComs+=1
            rootComsSeen.append(ent['_id'])
            rootComsUnseen.append(ent['_id'])
        else:
            nReplies+=1
            if ent['parent_id'] in rootComsSeen:
                rootComsSeen.remove(ent['parent_id'])       

        if str(ent['user_id']) not in participants:
            d={ent['user_id']:1}
            participants[str(ent['user_id'])]=1
        else:
            participants[str(ent['user_id'])]+=1
        
        #profanity
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
                        #try:
                            entry= {'created_at':ent['created_at'],
                                'parent_id':ent['parent_id'],
                                'entry_id':ent['entry_id'],
                                'user_id':ent['user_id'],
                                'source':d[i],
                                'target':j
                                }
                        #except:pass
                            temp1.append(entry)                
                
                
    nOrphans=len(rootComsSeen)
    nAdopted=len(rootComsUnseen)-len(rootComsSeen)
    tt=[int(i) for i in participants.keys()]

    entry={
            'participants':[participants],
            'participantIds':[int(i) for i in tt],
           'nCommenters':len(participants),
           'nReplies':nReplies,
           'nComsSeen':nComs,
           'nAdoptedComs':nAdopted,
           'nOrphanComs':nOrphans,
            'profEdges':temp1,
            'profNodes':temp2
           }    
    return entry

results=[]
counter=0
togo=db.metadatadb.find({'nReplies':{'$exists':False}}).count()
print 'len to go: %s' % togo
for ref in db.metadatadb.find({'nReplies':{'$exists':False}}):
    counter+=1
    if counter %10==0: print '%s thousand seen. Percentage done: %s. N to go: %s' %(counter/float(1000),round(100*(counter/float(togo)),2),togo-counter)
    if 'nReplies' not in ref:
        entry1= interactAndProfanity(ref)


        db.metadatadb.update({'_id':ref['_id']},{'$set':entry1})
#N unique commenters
#repliesto comments on roots