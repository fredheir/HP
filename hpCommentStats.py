# -*- coding: utf-8 -*-
import codecs
import pymongo
from pymongo import MongoClient
import re
import string
from nltk import*
import nltk
from nltk.corpus import cmudict
from hpfunctions import stripWhite, file_contents
import string
import ner

client = MongoClient()
db = client['hp-database']
counter=0


tagger = ner.SocketNER(host='localhost', port=8089)
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#To start server
#java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.conll.4class.distsim.crf.ser.gz -port 8089 -outputFormat inlineXML

#Functions for working with named entity recognition system
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

#Functions for spellchecker
import enchant
ukDict = enchant.Dict("en_UK")
usDict = enchant.Dict("en_US")
def wordLookup(word):
	if usDict.check(word):
		return True
	if ukDict.check(word):
		return True
	#print word
	return False

#Profanity, hostility
#A list of 1,300+ English terms that could be found offensive. 
#The list contains some words that many people won't find offensive, 
#but it's a good start for anybody wanting to block offensive or profane terms on their Site.
#http://www.cs.cmu.edu/~biglou/resources/bad-words.txt


queue=file_contents("bad-words.txt")
profanity=queue.splitlines()
profanity=profanity[1:]

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
	#t
	tagger = ner.SocketNER(host='localhost', port=8089)
	remove_list = ['html', 'http','https']
	names=0
	typos=0
	caps=0
	nWords=0
	recList=[]
	typoList=[]
	out=stripWhite(comment["text"])
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
			#if word[0].islower():
				if wordLookup(word)==False:
					typoList.append(word)
					typos+=1
				else:recList.append(word)
				if word.isupper()==True:
					caps +=1
	typos=typoList
	return nWords,typos,caps,p1-p2,recList,nNames,pos#reclist= recognised words, and those with first cap (names)



#To remove punctuation
punct=string.punctuation
punct=re.sub("'","",punct)
def enc_trans(s):
	s = s.encode('utf-8').translate(None, punct)
	return s.decode('utf-8')


writer=open("commentStats.txt","w+")
writer.write("_id	entry_id	parent_id	user_id	created_at	nWords	typos	caps	nPunct	nNames	nComma	nSent	avSentLen	avWordLen	nOffensive	avSyllables	threeSylPlus\n")
keepTrack=0
startAt=3908249
go=False
for entry in db.metadatadb.find({"comments":{"$exists":True},"nComments":{"$gt":0}}):
	if go==True:
		out=entry["comments"]
		print("started")
		if len(out)>0:
			for comment in out:
				tt=comment["text"]
				nWords,typos,caps,nPunct,words,nNames,pos=getBaseStats(comment)
				nComma=tt.count(",")
				nSent=len(tokenizer.tokenize(tt))
				TAG_RE = re.compile(r'<.*>')
				text=TAG_RE.sub('', text)
				text=re.sub(r'http.* ', ' ', text, flags=re.MULTILINE)
				text=re.sub(r'www.* ', ' ', text, flags=re.MULTILINE)
				avSentLen= len(text.split())/float(nSent)#(len(comment["text"])/float(l))-l
				try:
					avWordLen=sum([len(x) for x in words])/float(len(words))
				except: avWordLen=0
				nOffensive =  len(set(profanity).intersection(tt.lower().split()))
				avSyllables,threeSylPlus=sylList(words)
				result=[comment["_id"],
						comment["entry_id"],
						comment["parent_id"],
						comment["user_id"],
						comment["created_at"],
						nWords,
						typos,
						caps,
						nPunct,nNames,nComma,nSent,avSentLen,avWordLen,nOffensive,avSyllables,threeSylPlus,words]
				counter=0
				for i in result:
					counter+=1
					if counter>1:
						writer.write("\t"+str(i))
					else: writer.write(str(i))
				writer.write("\n")
	if keepTrack %10==0:print keepTrack
	keepTrack+=1
	if int(entry["_id"])==3908249:
		go=True
writer.close()
