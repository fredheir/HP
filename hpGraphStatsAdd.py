import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
from igraph import *
client=MongoClient()
db=client['hp2']

def getComDat(ent):
	results=[]
	names=[]
	c= ent['comments']
	for i in c:
		entry=(str(i['user_id']),str(i['parent_user']))			
		results.append(entry)
		if str(i['user_id']) not in names:
			names.append(str(i['user_id']))
		if str(i['parent_user']) not in names:
			names.append(str(i['parent_user']))
	return results,names

def setupGraph(results,names):
	g=Graph(directed=True)
	g.add_vertices(len(names))
	g.vs['name']=names
	g.add_edges(results)
	#g.es['weight']=1
	#g=g.simplify(combine_edges=sum,loops=False)
	return g

def getGraphStats(g):
	return {
		'g_meanBetweenness' :mean(g.betweenness()),
		'g_density':g.density(),
		'g_meanEccentricity' :mean(g.eccentricity()),
		'g_averagePathLength': g.average_path_length(),
		'g_diameter' :g.diameter(),
		#print g.community_multilevel(weights='weight')
		'g_transitivityUndirected' :g.transitivity_undirected(),
		'g_transitivityAvglocal' :g.transitivity_avglocal_undirected(),
		'g_meanEigenvectorCentrality' :mean(g. eigenvector_centrality ()),
		'g_meanDeg' :mean(g.degree())
}

def getLayout(g):
	layout = g.layout('kk')
	vs={}
	vs["vertex_label"] = g.vs["name"]
	deg=g.degree()
	deg= [3+i for i in deg]
	vs["vertex_size"] = deg

	#vs['edge_width']=g.es['weight']
	vs["vertex_label_size"] = 10
	vs["vertex_label_dist"] = 3
	vs["edge_arrow_size"] = 0.5
	vs["edge_curved"] = True
	vs["label_dist"] = 100
	return vs



counter=0
for ent in db.metadatadb.find():
	#if not 'g_density' in ent:
		counter+=1
		if counter %2==0:print str(float(counter)/1000) +' thousand'
		results,names=getComDat(ent)
		results=[i for i in results if i[1] != '0']
		names=[i for i in names if i != '0']
		if len (results)>0:
			try:
				print len(results)
				g=setupGraph(results,names)
				#vs= getLayout(g)
				temp=getGraphStats(g)
				temp['id']=ent['_id']
				temp['timestamp']=ent['timestamp']		  	
				db.metadatadb.update({'_id':ent['_id']},{'$set':temp})
			except:print 'error'
		try:
			print db.metadatadb.find({'_id':ent['_id']})[0]['g_density']
		except:'error'
	#else:
	#	print 'seen'



