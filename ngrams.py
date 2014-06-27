from google_ngram_downloader import readline_google_store
fname, url, records = next(readline_google_store(ngram_len=2))
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['ngrams']

def getEntry(d):
    ngram,year,match_count,volume_count=d[0:4]
    entry={
           'ngram':ngram,
           'year':year,
           'match_count':match_count,
           'volume_count':volume_count
           }
    return entry

inspect=[]
counter=0
previous=""
keep=0
target=[u'conspir',u'plot',u'scheme',u'stratagem',u'machination',u'cabal',u'deception',u'deceit',
        u'deceive', u'ploy', u'ruse',u'dodge', u'subterfuge', u'complot',u'coup',u'colluder', u'collusion',
         u'collaborator', u'conniver', u'machinator', u'traitor',u'connive']
while True:
    d=next(records)
    if d[0]==previous:
        if keep !=0:
            inspect.append(getEntry(d))
    else:
        if any (t in target for t in d[0].lower().split(' ')):
            inspect.append(getEntry(d))
            print d[0]
            keep=1
        else:
            keep=0
        previous=d[0]
    counter+=1
    if counter %1000000==0:
        if counter <= 1000000000:
            print str( counter/(1000000)) + (' (million)')    
        else:
            print str( counter/float(1000000000)) + (' (billion)')
        print 'latest record: '+str(d)
        #Archiving
        if len (inspect)>0:
            try: 
                db.ngrams.insert(inspect,continue_on_error=True)
            except pymongo.errors.DuplicateKeyError:
                pass
            inspect=[]
        