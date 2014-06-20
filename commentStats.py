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



def getCommentStats(out):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	results=[]
	for comment in out:
		if "text" in comment:
			text=comment["text"]
			nWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
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
			#shortPercentage=content_fraction(words)
			result={"_id":comment["_id"],
					"entry_id":comment["entry_id"],
					"parent_id": comment["parent_id"],
					"user_id": comment["user_id"],
					"created_at": comment["created_at"],
					"nWords": nWords,
					"typos": typos,
					"caps": caps,
					"nPunct": nPunct,
					"nNames": nNames,
					"nComma": nComma,
					"nSent": nSent,
					"avSentLen": avSentLen,
					"avWordLen": avWordLen,
					"nOffensive": nOffensive,
					"avSyllables": avSyllables,
					"threeSylPlus": threeSylPlus#,
					#"shortPercentage": shortPercentage
					}
			counter=0
			results.append(result)
		else:
			text=comment["message"]
			nWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
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
			result={"_id":comment["id"],
					#"entry_id":comment["entry_id"],
					#"parent_id": comment["parent_id"],
					#"user_id": comment["user_id"],
					"created_at": comment["created_time"],
					"nWords": nWords,
					"typos": typos,
					"caps": caps,
					"nPunct": nPunct,
					"nNames": nNames,
					"nComma": nComma,
					"nSent": nSent,
					"avSentLen": avSentLen,
					"avWordLen": avWordLen,
					"nOffensive": nOffensive,
					"avSyllables": avSyllables,
					"threeSylPlus": threeSylPlus
					}
			counter=0
			results.append(result)
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
		print 'strange error'
		return False

#To remove punctuation
punct=string.punctuation
punct=re.sub("'","",punct)
def enc_trans(s):
	s = s.encode('utf-8').translate(None, punct)
	return s.decode('utf-8')
