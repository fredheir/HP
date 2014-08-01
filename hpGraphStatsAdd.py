
import pymongo, urllib3
from pymongo import MongoClient
from hpfunctions import getUrl, stripWhite,stripWhiteList
from lxml import html
from igraph import *
client=MongoClient()
db=client['hp3']

def getComDat(ent):
    results=[]
    names=[]
    c= ent['comments']
    for i in c:
        try:
            entry=(str(i['user_id']),str(i['parent_user']))			
            results.append(entry)
            if str(i['user_id']) not in names:
                names.append(str(i['user_id']))
            if str(i['parent_user']) not in names:
                names.append(str(i['parent_user']))
        except KeyError:pass
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
    try:
        eig=mean(g. eigenvector_centrality ())
    except:eig=None
    return {
        'g_meanBetweenness' :mean(g.betweenness()),
        'g_density':g.density(),
        'g_meanEccentricity' :mean(g.eccentricity()),
        'g_averagePathLength': g.average_path_length(),
        'g_diameter' :g.diameter(),
        #print g.community_multilevel(weights='weight')
        'g_transitivityUndirected' :g.transitivity_undirected(),
        'g_transitivityAvglocalZERO' :g.transitivity_avglocal_undirected(mode=1),
        'g_transitivityAvglocalNAN' :g.transitivity_avglocal_undirected(mode=0),
        'g_meanEigenvectorCentrality' :eig,
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


#add parent_user
counter=0

print db.metadatadb.find({'redone':{'$exists':False}}).count()
curs=db.metadatadb.find({'redone':{'$exists':False}},timeout=False)
for ent in curs:
    counter+=1
    if counter %1000==0:print '%s thousand done' %(counter/float(1000))
    ent['comments']=[]

    for i in db.comStats.find({'entry_id':ent['_id']}):
        if 'parent_user' not in i:
            if i['parent_id']!=0:
                pu=0
                target=i['parent_id']
                pu= db.comStats.find({'_id':target})[0]['user_id']
                db.comStats.update({'_id':i['_id']},{'$set':{'parent_user':pu}})
        ent['comments'].append(i)
    results,names=getComDat(ent)
    #results=[i for i in results if i[1] != '0']
    #names=[i for i in names if i != '0']
    if counter>0:
        #try:
            g=setupGraph(results,names)
            #vs= getLayout(g)
            temp=getGraphStats(g)
            temp['id']=ent['_id']
            temp['timestamp']=ent['timestamp']     
            temp['redone']='aug'     
            db.metadatadb.update({'_id':ent['_id']},{'$set':temp})
        #except:print 'error'
curs.close()

