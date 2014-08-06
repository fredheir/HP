import urllib2
from hpfunctions import getUrl
from urllib3 import PoolManager, Timeout

id=4

def getIps(url):
    import urllib3
    http = urllib3.PoolManager()
    rx = http.request('GET', url)
    rx=rx.data[0:2000]
    try:
        sIp=rx.split('Received: from [')[1].split(']')[0]
    except:sIp=None
    try:
        sender=rx.split('Return-path: <')[1].split('>')[0]
    except:sender=None
    import re
    if 'for <' in rx:
        recipient=rx.split('for <')[1].split('>')[0]
    else:
        try:
            recipient =rx.split('for ')[1].split(';')[0]
        except:recipient=None
    #if 'SMTP' in rx and 'MIME' in rx:
    #    try:
    #        rx=rx.split('MIME')[1].split('SMTP')[1]
    #    except:pass
    ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', rx )
    try:
        rIp=[i for i in ip if i!=sIp]
        rIp=[i for i in rIp if len(i.split('.')[-1])<4]
    except:rIp=None
    return sender, sIp,recipient, rIp

import pymongo
from pymongo import MongoClient
client = MongoClient()
targetDb='data'
db = client['slivmail']

for i in db[targetDb].find({'sIp':{'$exists':False}},timeout=False):
    print i['_id']
    url='http://slivmail.com/messages/original/'+str(i['_id'])
    try:
        a,b,c,d=getIps(url)
        ent={
            'sender':a,
            'sIp':b,
            'recipient':c,
            'rIp':d,
             }
        db[targetDb].update({'_id':i['_id']},{'$set':ent})
    except:pass