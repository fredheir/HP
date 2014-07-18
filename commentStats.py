# -*- coding: utf-8 -*-
#Comment stats functions

import codecs
import pymongo
from pymongo import MongoClient
import re
import string
from nltk import*
import nltk
from nltk.corpus import cmudict
import ner
from hpfunctions import stripWhite, file_contents
import string
import enchant

ukDict = enchant.Dict("en_UK")
usDict = enchant.Dict("en_US")

queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
from nltk.corpus import stopwords
sl=stopwords.words('english')

tagger = ner.SocketNER(host='localhost', port=8089)

def getPosLen(a):
	count=0
	for i in a:
		for j in a[i]:
			count+=1
	return(count)

def removePos(text,a):
	todo=[]
	for i in a:
		for j in a[i]:
			todo.append(j)
	todo.sort(lambda x,y: cmp(len(y), len(x))) # sort by decreasing string length
	for i in todo:
		text=re.sub(i," ",text)
	return stripWhite(text)


#syllables
from nltk.corpus import cmudict
d = cmudict.dict()
def nsyl(word):
  return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]] 

def sylList(wordList):
	r=[]
	threePlus=[]
	av=0
	outres=0
	for word in wordList:
		try:
			t=nsyl(word)
			r.append(t[0])
			if t[0]>2:threePlus.append(t[0])
		except:pass
	#print len(r)
	if len(r)>0:
		av= sum(r)/float(len(r))
		outres=len(threePlus)/float(len(r))
	return av,outres



def getBaseStats(comment):
	tagger = ner.SocketNER(host='localhost', port=8089)
	remove_list = ['html', 'http','https']
	names=0
	typos=0
	caps=0
	nWords=0
	recList=[]
	try:
		out=stripWhite(comment["text"])
	except: out= stripWhite(comment["message"])
	p1=len(out)
	out=re.sub('/', ' ', out)
	out=re.sub('-', ' ', out)
	out=re.sub(u'“', '', out)
	out=re.sub(u'”', '', out)
	out=re.sub('\.\.\.', ' ', out)
	out=enc_trans(out)
	p2=len(out)
	#remove links
	out=re.sub(r'www.* ', ' ', out, flags=re.MULTILINE)
	out=re.sub(' +',' ',out)
	word_list = out.split()
	out=' '.join([i for i in word_list if i not in remove_list])
	
	pos= tagger.get_entities(out)
	nNames=getPosLen(pos)
	out=removePos(out,pos)

	ne=tagger.get_entities(out)

	for word in out.split():
		nWords+=1
		if len(word)>0 and word not in ["http","https","html"]:
			if word[0]=='"' or word[0]=="'":word=word[1:]
			if len(word)>0:
				if word[-1]=='"' or word[-1]=="'":word=word[:-1]
				#if word[0].islower():
				if wordLookup(word)==False:
					typos+=1
				else:recList.append(word)
				if word.isupper()==True:
					caps +=1
	return nWords,typos,caps,p1-p2,recList,nNames,pos#reclist= recognised words, and those with first cap (names)

def content_fraction(text):
    import nltk
    stopwords = nltk.corpus.stopwords.words('english')
    content = [w for w in text if w.lower() not in stopwords]
    return float(len(content)) / float(len(text))

def getOneCom(comment):
	if "text" in comment:
		text=comment["text"]
		nRecWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
		nComma=text.count(",")
		nSent=len(tokenizer.tokenize(text))
		TAG_RE = re.compile(r'<.*>')
		text=TAG_RE.sub('', text)
		text=re.sub(r'http.* ', ' ', text, flags=re.MULTILINE)
		text=re.sub(r'www.* ', ' ', text, flags=re.MULTILINE)
		text=enc_trans(text)
		avSentLen= len(text.split())/float(nSent)#(len(comment["text"])/float(l))-l
		try:
			avWordLen=sum([len(x) for x in words])/float(len(words))
		except: avWordLen=0
		nOffensive =  len(set(profanity).intersection(text.lower().split()))
		avSyllables,threeSylPlus=sylList(words)
		nStop=len(filter(set(words).__contains__, sl))
		#shortPercentage=content_fraction(words)
		result={"_id":comment["_id"],
				"entry_id":comment["entry_id"],
				"parent_id": comment["parent_id"],
				"user_id": comment["user_id"],
				"created_at": comment["created_at"],
				"nWords": len(text.split()),
				"nRecWords": nRecWords,
				"nTypos": typos,
				"nCaps": caps,
				"text":comment['text'],
				"words":' '.join(words),
				"names":pos,
				"nPunct": nPunct,
				"nNames": nNames,
				"nComma": nComma,
				"nSent": nSent,
				"nStop":nStop,
				"avSentLen": avSentLen,
				"avWordLen": avWordLen,
				"nOffensive": nOffensive,
				"avSyllables": avSyllables,
				"threeSylPlus": threeSylPlus#,
				#"shortPercentage": shortPercentage
				}
		counter=0
	else:
		text=comment["message"]
		nRecWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
		nComma=text.count(",")
		nSent=len(tokenizer.tokenize(text))
		TAG_RE = re.compile(r'<.*>')
		text=TAG_RE.sub('', text)
		text=re.sub(r'http.* ', ' ', text, flags=re.MULTILINE)
		text=re.sub(r'www.* ', ' ', text, flags=re.MULTILINE)
		text=enc_trans(text)
		avSentLen= len(text.split())/float(nSent)#(len(comment["text"])/float(l))-l
		try:
			avWordLen=sum([len(x) for x in words])/float(len(words))
		except: avWordLen=0
		nOffensive =  len(set(profanity).intersection(text.lower().split()))
		avSyllables,threeSylPlus=sylList(words)
		nStop=len(filter(set(words).__contains__, sl))
		result={"_id":comment["id"],
				#"entry_id":comment["entry_id"],
				#"parent_id": comment["parent_id"],
				#"user_id": comment["user_id"],
				"created_at": comment["created_time"],
				"nWords": len(text.split()),
				"nRecWords": nRecWords,
				"nTypos": typos,
				"nCaps": caps,
				"text":comment['message'],
				"words":' '.join(words),
				"names":pos,
				"nTypos": typos,
				"nCaps": caps,
				"nPunct": nPunct,
				"nNames": nNames,
				"nComma": nComma,
				"nSent": nSent,
				"nStop":nStop,
				"avSentLen": avSentLen,
				"avWordLen": avWordLen,
				"nOffensive": nOffensive,
				"avSyllables": avSyllables,
				"threeSylPlus": threeSylPlus
				}
		counter=0
	return result


def getCommentStats(out):
	import time

	results=[]
	for comment in out:
		getCom=0
		while getCom ==0:
			try:
				results.append(getOneCom(comment))
				getCom=1
			except:
				print 'SLEEEPING_extra'
				time.sleep(5)
	print 'debug test: len results == '+str(len(results))
	return results


def wordLookup(word):
	try:
		if usDict.check(word):
			return True
		if ukDict.check(word):
			return True
		#print word
		return False
	except:
		return False

#To remove punctuation
punct=string.punctuation
punct=re.sub("'","",punct)
def enc_trans(s):
	s = s.encode('utf-8').translate(None, punct)
	return s.decode('utf-8')




def enterFile(url):
    if url[0]=='/':url='http://www.huffingtonpost.com'+url
    f = urllib2.urlopen(url)
    data = f.read()
    oid = fs.put(data)
    return oid

def getComment(parent_user,entry):
    cc=[]
    counter=0
    if not "models" in entry:
        print "apparently 1/100 chance error or commenting disabled"
        return "error"
    for i in entry["models"]:
        try:
            nSeen=len(i['replies']['models'])
        except:
            nSeen=0
        counter+=1
        dict={
        "_id":i["id"],
        "user_id":i["user_id"],
        "created_at": i["created_at"],
        "text":i["text"],
        "parent_id":i["parent_id"],
        "parent_user":parent_user,
        "entry_id":i["entry_id"],
        "publication":"HP",
        "level":i['level'],
        "stats":i['stats'],
        'nSeen':nSeen,
        "site":"com"}
        cc.append(dict)
        if i["replies"]["options"]["total"]>0:
            cc+=(getComment(i["user_id"],i["replies"]))
    return cc


def getMore3(p,count=10):
    additions=getDescendants(p)
    if additions is not None: #and 'models' in additions:
        out={} 
        out['users']=additions['users']
        yield out
        for a in additions['models']:
                if len(a['replies']['models'])>0:
                    for resid in a['replies']['models']:
                        yield resid
                        a['replies']['models']=[]
                if a['stats']['replies']>0:
                    yield a
                    for sub in getMore3(a):
                        yield a
                else:
                    yield a

def identifyParents(dat2,lev,pid):
    temp=dat2.copy()
    new={}
    for x in range(len(temp['models'])):
        if temp['models'][x]['level']==(lev+1):
            temp['models'][x]['parent_id']=pid

    for x in range(len(temp['models'])):
        d=temp['models'][x]['level']
        for j in range(x+1,len(temp['models'])):
            d2=temp['models'][j]['level']
            if d2==d+1:
                temp['models'][j]['parent_id']=temp['models'][x]['id']
    return temp

def getDescendants(i):

    t=i['stats']['replies']

    if 'models' not in i['replies']:
        i['replies']['models']=[]
    if t==0:
        return None

    pid=i['id']
    lev=i['level']
    if i['stats']['children']==1:
        url="http://www.huffingtonpost.com/conversations/entries/"+str(id)+"/comments/"+str(pid)+"/descendants?app_token=d6dc44cc3ddeffb09b8957cf270a845d&limit=90&order=4"
        string = getUrl(url)
        dat2=json.loads(string)#['models']

    elif i['stats']['children']>1:
        url="http://www.huffingtonpost.com/conversations/entries/"+str(id)+"/comments/"+str(pid)+"/replies?app_token=d6dc44cc3ddeffb09b8957cf270a845d&limit=90&order=4"        
        string = getUrl(url)
        dat2={}
        temp=json.loads(string)#['models']
        for pp in temp:
            dat2[pp]=temp[pp]

    if i['stats']['children']==0:
        return None

    newEntries= identifyParents(dat2,lev,pid)
    #newEntries = identifyNSeen(newEntries,lev)

    return(newEntries)

def getRootCommentUrl(i,id,n,dat):
    base="http://www.huffingtonpost.com/conversations/entries/"
    options="order_0=1&order_1=4&limit_0="+str(n)+"&limit_1=98"
    if i==0:
        url=base+str(id)+"/comments?app_token=d6dc44cc3ddeffb09b8957cf270a845d&filter=0&"+options
    else:
        tg=[]
        for x in dat["models"]:
            tg.append(x["id"]) #+=[i["id"]]
        target=min(tg)
        url = base+str(id)+"/comments?app_token=d6dc44cc3ddeffb09b8957cf270a845d&filter=0&last="+str(target)+'&'+options
    return url



def getMissingReplies(dat,users):
    counter=0
    for t in dat['models']:
        if counter%10==0:print 'added conversations for '+str(counter)+' N to go: '+str(len(dat['models']))
        counter+=1
        #print t['nSeen']
        nParentReps=len([i['id'] for i in t['replies']['models'] if i['parent_id']==t['id']])
        if t['stats']['replies']<len(t['replies']['models']):      
            if t['stats']['children']<=nParentReps:
                for page in t['replies']['models']:
                    for hit in getMore3(page):
                        if 'users' in hit:
                            users.append(hit['users'])
                        else:
                            if hit['id'] not in [i['id'] for i in t['replies']['models']]:
                                t['replies']['models'].append(hit)
    return dat,users                    


def getUserPics(users):
    for i in users:
        url=i['photo_url']
        if url[0]=='/':url='http://www.huffingtonpost.com'+url
        i['oid']=enterFile(url)
    return users

def getComment(entry):
    cc=[]
    counter=0
    if not "models" in entry:
        print "apparently 1/100 chance error or commenting disabled"
        return "error"
    for i in entry["models"]:
        try:
            nSeen=len(i['replies']['models'])
        except:
            nSeen=0
        counter+=1
        dict={
        "_id":i["id"],
        "user_id":i["user_id"],
        "created_at": i["created_at"],
        "text":i["text"],
        "parent_id":i["parent_id"],
        #"parent_user":parent_user,
        "entry_id":i["entry_id"],
        "publication":"HP",
        "level":i['level'],
        "stats":i['stats'],
        'nSeen':nSeen,
        "site":"com"}
        cc.append(dict)
        if i["replies"]["options"]["total"]>0:
            cc+=(getComment(i["replies"]))
    return cc

