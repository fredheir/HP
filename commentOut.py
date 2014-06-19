#script to save csv with comment data
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
client=MongoClient()
db=client['hp']
import pandas
import numpy
from monary import Monary 

mon=Monary()

print 'available columns'

for i in db.comStats.find()[0]:print i

columns = ['typos', 'avSyllables', 'nPunct']
numpy_arrays = mon.query('hp', 
                        'comStats', 
                        {},
                        columns, 
                        ['int32', 'int32', 'int32:20'])

df = numpy.matrix(numpy_arrays).transpose() 
df = pandas.DataFrame(df, columns=columns)
print 'starting to write file pandasTest.csv'
df.to_csv('pandasTest.csv', sep='\t')