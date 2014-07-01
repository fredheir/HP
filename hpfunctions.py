# -*- coding: utf-8 -*-
#For Facebook comments:
#http://graph.facebook.com/comments?id=http://www.huffingtonpost.com/james-peron/why-hate-defeats-itself_b_5463965.html&limit=5000&fields=message&filter=stream&order=chronological&&fields=parent.fields(id),message,from,likes


import urllib3
import re
import json
from itertools import chain
from bs4 import BeautifulSoup
from lxml import html
import lxml
from datetime import date, timedelta, datetime
import codecs

def archive(db,target,dat):
	import pymongo
	print ("entering scraped")
	if len (dat)>0:
		try: 
			db[target].insert(dat,continue_on_error=True)
		except pymongo.errors.DuplicateKeyError:pass


def addOneDay(date):
	start=0
	results = []
	df=date.strftime("%Y%m%d")
	while True:
		result=addToQueue2(start,df)
		if result == "No data":
			return results
		results+=result
		if len(result)<20:
			return results
		print("completed entry "+ str(start))
		start+=20
	print("completed scraping "+ str(date))
	return(result)


def addOneDay2(date,baseUrls,db):
	start=0
	result = []
	df=date.strftime("%Y%m%d")
	for i in baseUrls:
		if df in i:
			target=i
	sublinks=getSubLinks(target)
	print str(len (sublinks)) + " sublinks identified. Starting scraping."
	for i in sublinks:
		print "scraping "+i
		_id=getIds(i)
		if db.metadatadb.find({"_id":_id}).limit(1).count() ==0:
			try:
				temp=addToQueue3(i)
				temp["seen"]=[df]
				result.append(temp)
			except:
				print "Previous link FAILED\n\n\n"
		else: 
			try:
				print "duplicated entry. Skipping scrape. Adding seen"
				if df not in db.metadatadb.find({"_id":_id})[0]["seen"]:
					db.metadatadb.update({'_id' : _id}, { '$push':{'seen': df}})
					print db.metadatadb.find({"_id":_id})[0]["seen"]
			except:pass
			#ADD update seen information here, e.g. page still on front page x days later


	print("completed scraping "+ str(date))
	return(result)


def addToQueue2(start,date):
	url="https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=10&num=20&hl=en&prettyPrint=false&source=gcsc&gss=.com&sig=9d8da27b023599b9c9de8a149abbd171&start="+str(start)+"&cx=004830092955692134028:an6per91wyc&q=as+the+a&sort=date%3Ar%3A"+str(date)+"%3A"+str(date)+"&as_sitesearch=huffingtonpost.com&googlehost=www.google.com&callback=google.search.Search.apiary2270&nocache=1401460955799"
	rx=getUrl(url)	
	if "Invalid Value" in rx:
		print("invalid data")
		return "No data"
	t=rx.split("(",1)
	dat=json.loads(t[1][0:-2])
	results=[]
	for i in dat["results"]:
		url=i["url"]
		cat="none"
		author="none"
		article="none"
		u="none"
		title="none"		
		try:
			category=i["richSnippet"]["metatags"]["category"]
		except:
			pass
		try:author=i["richSnippet"]["metatags"]["author"]
		except:
			pass
		try:article=i["richSnippet"]["metatags"]["ogDescription"]
		except:
			pass
		try:u=i["richSnippet"]["metatags"]["ogUrl"]
		except:
			pass
		try:title=i["richSnippet"]["metatags"]["ogTitle"]
		except:
			pass
		dict={"_id":getIds(url),"title":title, "author":author, "date": date,"url":u,"category":cat,"publication":"HP","site":"com"}

		results.append(dict)
	return results


def addToQueue3(url):
	from lxml import html
	rx=getUrl(url)
	tree = html.fromstring(rx)
	title= tree.xpath("//meta[@property='og:title']/@content")[0]
	title=stripWhite(title)
	category= tree.xpath("//meta[@name='category']/@content")[0]
	try:
		author = tree.xpath("//meta[@name='author']/@content")[0]
	except:
		author=tree.xpath("//div[@class='articleBody']/p/strong")[0].text_content()
		author=author.split("(")[0]
		author =author.replace("By ","")
	author=stripWhite(author)
	try:
		date = tree.xpath("//meta[@name='sailthru.date']/@content")[0]
	except:
		date = tree.xpath("//span[@class='posted']/time/@datetime")[0]
	try:
		tags= tree.xpath("//div[contains(@class,'follow_tags')]/span")[0].text_content().split(",")
		t=[]
		for i in tags:
			t+=[i.replace(u'\xa0', u'').lstrip()]
		t=stripWhiteList(t)
	except: t=tree.xpath("//div[contains(@class,'follow_tags')]/a/text()")
	body=tree.xpath("//*[@class='entry_body_text']/p")
	if len(body) ==0:
		body= tree.xpath("//*[@class='articleBody']/p")
	bod=[]
	for i in body:
		bod.append(i.text_content())
	timestamp=formatDate(date)
	#try:
	#	date= tree.xpath("*[@itemprop='datePublished']")[0]
	#except:
	#	date= tree.xpath("//div[contains(@class,'datetime')]")[0].text_content()
	#	date
	articleType="news"
	if "_b_" in url:
		articleType="blog"
	dict={"_id":getIds(url),
		  "title":title,
		  "author":author,
		  "date": date,
		  "url":url,
		  "category":category,
		  "publication":"HP",
		  "site":"com",
		  "tags":t,
		  "body":bod,
		  "articleType":articleType,
		  "timestamp":timestamp
		  }
	return(dict)



def commentSelector(d,_id,url):
	print int(d.strftime("%Y%m%d"))
	if int(d.strftime("%Y%m%d"))<20140605:
		print("getting conventional comments")
		coms=getComments(_id)
	if int(d.strftime("%Y%m%d"))>20140604 and int(d.strftime("%Y%m%d"))<20140612:
		print("getting both comments")
		coms=getComments(_id)
		print str(len(coms)) +" comments before fb"
		try:
			coms2=(getFbComment(url)["data"])
			coms=coms+coms2
		except:pass
		print str(len(coms)) +" comments after fb"

	if int(d.strftime("%Y%m%d"))>20140604:
		if int(d.strftime("%Y%m%d"))<20140612:
			print("getting both comments")
			coms=getComments(_id)
			print str(len(coms)) +" comments before fb"
			try:
				coms2=(getFbComment(url)["data"])
				coms=coms+coms2
			except:pass
			print str(len(coms)) +" comments after fb"
		else:
			try:
				coms=getFbComment(url)["data"]
				print("getting fb comments")
			except:coms=[]
	if len(coms)==0:
		print "no comments found for text at "+url
	return(coms)


def dateUp(date):
	return date+timedelta(days=1)

def dateDown(date):
	return date+timedelta(days= -1)


def file_contents(file_name):
	with codecs.open(file_name,encoding="utf-8") as f:
		try:
			return f.read()
		finally:
			f.close()


def fbComSearch(dat,term):
	for i in dat["data"]:
		if term in str(i):
			print i


def formatDate(t):
	out=t
	try:
		t1=datetime.strptime(t,"%a, %d %b %Y %H:%M:%S -0500")
		out=t1.strftime("%Y%m%d")
	except:
		try:
			t1=datetime.strptime(t,"%a, %d %b %Y %H:%M:%S -0400")
			out=t1.strftime("%Y%m%d")
		except:
			try:
				t1=datetime.strptime(t,"%Y-%m-%dT%H:%M:%S-05:00")
				out=t1.strftime("%Y%m%d")
			except:pass
	if "2014-" in t:
		try:
			t2=datetime.strptime(t,"%Y-%m-%dT%H:%M:%S-04:00")
			out=t2.strftime("%Y%m%d")
		except:
			try:
				t2=datetime.strptime(t,"%Y-%m-%dT%H:%M:%S-05:00")
				out=t2.strftime("%Y%m%d")
			except:pass
	return(out)


def getBaseLinks(d):
	if "2013" in str(d):
		baseurl="http://web.archive.org/web/20130201000110*/http://www.huffingtonpost.com/"
		StartDate="20130101"
	else:
		baseurl="http://web.archive.org/web/20140201000110*/http://www.huffingtonpost.com/"
		StartDate="20140101"

	string = getUrl(baseurl)
	parsed=lxml.html.fromstring(string)
	links=[]

	d = datetime.strptime(StartDate, "%Y%m%d")
	df=d.strftime("%Y%m%d")

	for link in parsed.xpath('//a/@href'):
		if str(df) in link and "www" in link:
			links.append("http://web.archive.org"+link)
			d=d=d+timedelta(days=1)
			df=d.strftime("%Y%m%d")
	print "returning "+ str(len(links))+" base urls"
	return links


def getComments(id):
	comments=[]
	i=0
	n=99
	while i<10:#Limit to 1000 comments
		if i==0:
			url="http://www.huffingtonpost.com/conversations/entries/"+str(id)+"/comments?app_token=d6dc44cc3ddeffb09b8957cf270a845d&filter=0&order_0=1&order_1=4&limit_0="+str(n)+"&limit_1=9"
		else:
			tg=[]
			for x in dat["models"]:
				tg.append(x["id"]) #+=[i["id"]]
			target=min(tg)
			#print("\n\n\n Now targetting commments since: "+str(target)+"")
			url = "http://www.huffingtonpost.com/conversations/entries/"+str(id)+"/comments?app_token=d6dc44cc3ddeffb09b8957cf270a845d&filter=0&last="+str(target)+"&order_0=1&order_1=4&limit_0="+str(n)+"&limit_1=9"
		i+=1
		string = getUrl(url)
		dat=json.loads(string)
		newCom=getComment(0,dat)
		if newCom=="error":
			return(comments)
		comments+=newCom
		print "comments added: "+str(len(comments))
		if(len(dat["models"])<99):
			return comments
	return comments


def getComment(parent_user,entry):
	cc=[]
	counter=0
	if not "models" in entry:
		print "apparently 1/100 chance error or commenting disabled"
		return "error"
	for i in entry["models"]:
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
		"site":"com"}
		cc.append(dict)
		if i["replies"]["options"]["total"]>0:
			cc+=(getComment(i["user_id"],i["replies"]))
	return cc


def getIds(url):
	temp=re.split(r"[_\\.]",url)
	for i in temp:
		try:
			if int(i):
				return(int(i))
		except:pass

def getSubLinks(url):
	string = getUrl(url)
	sublinks=[]
	parsed=lxml.html.fromstring(string)
	for link in parsed.xpath('//a/@href'):
		if "html" in link and "www" in link and "huffingtonpost" in link:
			if "_n_" in link or "_b_" in link:
				a=link.split("html")[0]
				a=a.split("www")[1]
				sublinks.append("http://www"+a+"html")
	return list(set(sublinks))


def getFbComment(url):
	baseurl="http://graph.facebook.com/comments?id="+url+"&filter=toplevel&fields=message,from,likes,created_time,comment_count,like_count,message_tags&limit=500&"
	get=[]
	string = getUrl(baseurl)
	dat=json.loads(string)
	wait=0
	while wait==0:
		if "error" in dat:
			print "error caught"
			if "Application request limit reached" in dat["error"]["message"]:
				print "oauth error. FB overloaded. Sleeping"
				time.sleep(30)
			else: wait=1
		else: wait=1
		print("downloaded base")
	try:
		for i in dat["data"]:
			if i["comment_count"]>0:
				get.append(i["id"])
		for i in get:
			print i
			url="https://graph.facebook.com/"+str(i)+"/comments?&fields=parent.fields(id),message,from,likes,created_time,comment_count,like_count,message_tags"
			string = getUrl(url)
			dat2=json.loads(string)
			for j in dat2["data"]:
				dat["data"].append(j)
	except:pass
	return(dat)




def getUrl(url):
	http = urllib3.PoolManager()
	rx = http.request('GET', url).data
	return(rx)




def getTags(url):
	from lxml import html
	rx=getUrl(url)
	tree = html.fromstring(rx)
	tree.xpath("//div[contains(@class,'follow_tags')]/span/text()")
	results=tree.xpath("//div[contains(@class,'follow_tags')]/span")
	t=[]
	try:
		tags=results[0].text_content().split(",")
	except:
		pass
		print "no tags found for url"
		return t
	for i in tags:
		t+=[i.replace(u'\xa0', u'').lstrip()]
	print "tags from file "+str(t)
	return(t)


def huffTime(d):
	d=datetime.strptime(d, "%a, %d %b %Y %H:%M:%S -0400")
	df=d.strftime("%Y%m%d")
	return(int(df))


def loadQueue(file="queue.txt"):
	counter=0
	queue=file_contents(file)
	todo=content.splitlines()
	for i in todo:
		counter +=1
		queue+=[(i)]
	print("Added "+str(counter)+" files to queue")
	return(queue)

def stripWhite(text):
	TAG_RE = re.compile(r'<.*>')
	text=TAG_RE.sub('', text)
	text=text.rstrip()
	text=text.lstrip()
	text=re.sub('<br />',' ',text)
	text=re.sub('\t',' ',text)
	text=re.sub('\n',' ',text)
	text=re.sub(' +',' ',text)
	return(text)


#t=db.metadatadb.find({'tags':{'$regex':'  '}})[0]["tags"]
def stripWhiteList(t):
	t = [stripWhite(s) for s in t]
	t= [s for s in t if s!= u'']
	return(t)

def writeQueue(file,output):
	writer=open(file,"w+")
	counter=0
	for i in output:
		counter +=1
		try:
			writer.write(str(i[0])+"\n")
			for j in i[1]:
				writer.write(str(j)+",")
			writer.write("\n")
		except:pass
	print("Wrote "+str(counter)+" files to queue")
	writer.close()




# def getArticleData(url)
# 	string <- getUrl(url)

# 	title=as.character(xpathSApply(PARSED, "//meta[@property='og:title']/@content",))
# 	category=as.character(xpathSApply(PARSED, "//meta[@name='category']/@content",))
# 	author=as.character(xpathSApply(PARSED, "//meta[@name='author']/@content",))
# 	tags <- xpathSApply(PARSED, "//div[contains(@class,'follow_tags')]/span",xmlValue)
# 	tags <- list(unlist(str_split(tags,", ")))
# 	body <- list(xpathSApply(PARSED, "//*[@class='entry_body_text']/p",xmlValue))
# 	d <- xpathSApply(PARSED, "//*[@itemprop='datePublished']",xmlValue)
# 	if(length(d)==0){
# 	d <- xpathSApply(PARSED, "//div[contains(@class,'datetime')]",xmlValue)
# 	d <- (unlist(str_split(d," "))[2])

# 	}
# 	d <- (unlist(str_split(d," "))[1])
# 	date <- mdy(gsub("/","-",d))
# 	temp <- as.numeric(unlist(str_split(url,"_|\\.")))
# 	id <- unique(temp[!is.na(temp)])
# 	dat <- data.frame(id,title,date,category,author,I(tags),I(body))
# 	return(dat)

# for (i in 16:20){
#   print (i)
#   target <- urls[i]
#   articles <- rbind(articles,getArticleData(target))
#   output <- getArticle(articles$id[i])
#   users <- rbind(users,output[[2]])
#   entries <- rbind(entries,output[[1]])
# }