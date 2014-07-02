from google_ngram_downloader import readline_google_store
fname, url, records = next(readline_google_store(ngram_len=2))
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['ngrams']
import re

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
target=[u'conspir',u'scheme',u'stratagem',u'machination',u'cabal',u'deception',u'deceit',
        u'deceive', u'ploy', u'ruse',u'dodge', u'subterfuge', u'complot',u'colluder', u'collusion',
         u'collaborator', u'conniver', u'machinator', u'traitor',u'connive']
words_re = re.compile(r"|\b".join(target))
started=False
for fname, url, records in readline_google_store(ngram_len=5,verbose=True):
	if 'ac.gz' in str(fname):
		started=True
	while started==True
	print fname
	for d in records:
	    if d[0]==previous:
	        if keep !=0:
	            inspect.append(getEntry(d))
	    else:
	        if words_re.search(d[0]):
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
	                db.ngrams2.insert(inspect,continue_on_error=True)
	            except pymongo.errors.DuplicateKeyError:
	                pass
	            inspect=[]
        