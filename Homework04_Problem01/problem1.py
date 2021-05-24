from gurobipy import*
import csv
from haversine import haversine
import sqlite3
import pandas as pd
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()

#create index:mill   data define: mlati,mlon,msupply,mcost
with open('Ardent_Mills_Data.csv', 'r') as f1:
    myReader = csv.reader(f1)
    myReader.next()
    mill=[]
    mlati={}
    mlon={}
    msupply={}
    mcost={}
    for rows in myReader:  
        mill.append(rows[0])
        mlati[rows[0]]=float(rows[1])
        mlon[rows[0]]=float(rows[2])
        msupply[rows[0]]=float(rows[3].replace(',',''))
        mcost[rows[0]]=float(rows[4])
f1.close()

#create index: dis    data define: dislati, dislon, dissupply,discost
with open('Distributor_Data.csv', 'r')as f2:
    myReader = csv.reader(f2)
    myReader.next()
    dis=[]
    dislati={}
    dislon={}
    dissupply={}
    discost={}
    for row in myReader:
        dis.append(row[0].replace(' ',''))
        dislati[row[0].replace(' ','')]=float(row[2])
        dislon[row[0].replace(' ','')]=float(row[3])
        dissupply[row[0].replace(' ','')]=int(row[4].replace(',',''))
        discost[row[0].replace(' ','')]=float(row[5])
f2.close()

#  find out distance between mills and distribution center, save it to dictionary distance

distance={}
for i in dis:
    center=( dislati[i],dislon[i])
    for j in mill:
        mills=(mlati[j],mlon[j])
        distance[i,j]=haversine(center,mills)
# read in dailydemand data, create dailydm table, 1 pound of pizza flour =3.57 cups of pizza flour
# The number of pounds of flour for each center=dailydemand for each center *7* 3.25 /3.57 
# save it to dictionry weekdm  in pounds
reader=pd.read_csv("average_daily_demand.csv")
cur.execute('DROP TABLE IF EXISTS dailydm') 
reader.to_sql("dailydm",con)
con.commit()

weekdm={}
cur.execute('select  "Distribution center"as center,sum("average daily demand")*7*3.25/3.57 as totalweekdemand from dailydm\
            where "average daily demand" is not NULL group by center' ) 
for i in cur:
    weekdm[i[0]]=i[1]

rtool=700000         
# create model        
piz=Model()
piz.modelSense=GRB.MINIMIZE
piz.update()



#create the variables: for each mill , whether or it supply certain distribution center

myVars = {}
for d in dis:
    for m in mill:
        myVars[(d,m)] = piz.addVar(obj =2*distance[d,m]*discost[d]*(weekdm[d]/(880*50))+(mcost[m]/50)*weekdm[d],vtype = GRB.BINARY, name = 'x_%s_%s' % (d,m))

#create the variables: for each mill ,whether or not it  supply distribution center,
go={} 
for m in mill:
    go[m]=piz.addVar(obj=rtool,vtype=GRB.BINARY,name='y_%s' % (m))
 
piz.update()

#create one distribution center can only be serviced by one mill Constraints,save it to pizConstrs Dictionary
pizConstrs={}
for d in dis:
    constrName = 'onemillonly_%s' % d
    pizConstrs[constrName] = piz.addConstr(quicksum(myVars[d,m] for m in mill ) == 1, name = constrName)
piz.update()    
    
 
#  create supply demand. the total flour each mill provide to distrubution centers must not exceed its capacity
for m in mill:
    constrName = 'supply_%s' % m
    pizConstrs[constrName] = piz.addConstr(quicksum(myVars[d,m]*weekdm[d] for d in dis ) <= go[m]*msupply[m]*50, name = constrName)
piz.update() 
 
#create constraint, if one mill is used for distribution flour(go[m]=1), then the total number of centers it serves must be positive(>=1) .
#if the mill is not used(go[m]=0) , then it serves no center(0)
for m in mill:
    constrName = 'open_%s' % m
    pizConstrs[constrName] = piz.addConstr(quicksum(myVars[d,m] for d in dis ) >= go[m], name = constrName)
piz.update()

# Solve model
piz.optimize()
     
piz.write('piz.lp')

# get Solution
if piz.status == GRB.OPTIMAL:
    Solution1 = [] 
    Solution2=[]
    for v in myVars:
        if myVars[v].x > 0.0:
            #print (v, myVars[v].x)   
            # save Solution
            Solution1.append((v[0],v[1], myVars[v].x))
    for k in go:
        if go[k].x > 0.0:
           #print (k,go[k].x)
           Solution2.append((k, go[k].x))
# save solution to database

cur.execute('DROP TABLE IF EXISTS tblSolution1') 
cur.execute('CREATE TABLE tblSolution1(center TEXT,mill TEXT, deliveryornot NUMERIC)')
cur.executemany('INSERT INTO tblSolution1 VALUES(?,?,?)', Solution1)
con.commit() 


cur.execute('DROP TABLE IF EXISTS tblSolution2') 
cur.execute('CREATE TABLE tblSolution2(Mill TEXT, openornot NUMERIC)')
cur.executemany('INSERT INTO tblSolution2 VALUES(?,?)', Solution2)
con.commit() 

#print out on screen, uncomment below 

cur.execute('SELECT* FROM tblSolution1')
for i in cur:
     print (i)
     

cur.execute('SELECT* FROM tblSolution2')
for i in cur:
     print (i)




