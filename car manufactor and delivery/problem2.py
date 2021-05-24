from gurobipy import*
import csv
from haversine import haversine
import sqlite3
import pandas as pd
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()

# Build indexes: cartype, country;  Data define: hours   
with open('hours.csv', 'r') as f1:
    myReader = csv.reader(f1)
    cartype=next(myReader)[1:6]
    country=[]
    hours={}
    for rows in myReader: 
        country.append(rows[0])
        for i in range(1,6):        
            hours[rows[0],cartype[i-1]]=float(rows[i])
f1.close()

# Data define: carcost (manufacturing cost)
with open('costs.csv', 'r') as f2:
    myReader = csv.reader(f2)
    carcost={}
    myReader.next()
    for rows in myReader: 
        for i in range(1,6):       
            carcost[rows[0],cartype[i-1]]=int(rows[i])
f2.close()
#Data define: milecost
with open('milecost.csv', 'r') as f3:
    myReader = csv.reader(f3)
    milecost={}
    myReader.next()
    for rows in myReader: 
        for i in range(1,4):       
            milecost[rows[0],country[i-1]]=float(rows[i])
f3.close()

#Data define: totalhour, aunalcost(anual amortized cost for distribution center in each country)
with open('totalhour.csv', 'r') as f4:
    myReader = csv.reader(f4)
    totalhour={}
    anualcost={}
    for rows in myReader:        
            totalhour[rows[0]]=int(rows[1])
            anualcost[rows[0]]=int(rows[2])
f4.close()

#Create index: center(distribution center);  Data define: clon(distribution center longitude), clati(distribution center latitude),
with open('distribution_center_data.csv', 'r') as f5:
    myReader = csv.reader(f5)
    center=[]
    clon={}
    clati={}
    myReader.next()
    for rows in myReader: 
        center.append((rows[0],rows[1]))
        clati[(rows[0],rows[1])]=float(rows[2])
        clon[(rows[0],rows[1])]=float(rows[3])       
f5.close()

#Data define: delon(dealer longitude), delati(dealer latitude), dedemand(dealer demanf for each type of car),detotaldm( each dealer's total demand )

with open('dealership_data.csv', 'r') as f6:
    myReader = csv.reader(f6)
    dealer=[]
    delati={}
    delon={}
    dedemand={}
    detotaldm={}
    myReader.next()
    for rows in myReader: 
        if any(x.strip() for x in rows):
            dealer.append((rows[0],rows[1]))
            delati[(rows[0],rows[1])]=float(rows[2])
            delon[(rows[0],rows[1])]=float(rows[3])
            detotaldm[(rows[0],rows[1])]=float(rows[4])+float(rows[5])+float(rows[6])+float(rows[7])+float(rows[8])
            i=0
            for cars in cartype:
                dedemand[(rows[0],rows[1]),cars]=float(rows[4+i])
                i=i+1
print dedemand[(('US', 'US-00054'), 'Su')]        
f6.close()
#Data define: plantlati(factoary latitude), plantlon(factory longitude)
with open('plant_data.csv', 'r') as f7:
    myReader = csv.reader(f7)
    plantlati={}
    plantlon={}
    myReader.next()
    for rows in myReader:        
            plantlati[rows[0]]=float(rows[1])
            plantlon[rows[0]]=float(rows[2])
f7.close()

# distance between plants and distribution center
plant_center={}
for i in country:
    plant=(plantlati[i],plantlon[i])
    for j in center:  
        discenter=(clati[j],clon[j])
        plant_center[i,j]=haversine(plant,discenter)
# distance between distribution center and dealership
center_dealer={}
for i in center:
    discenter2=(clati[i],clon[i])
    for j in dealer:
        dealership=(delati[j],delon[j])
        center_dealer[i,j]=haversine(discenter2,dealership)

# data define: number of distribution centers in each country
limit={'US':4,'CA':3, 'MX':2}
        
# create model        
car=Model()
car.modelSense=GRB.MINIMIZE
car.update()

#create the variables: for each type of car, how many to ship from each plant to  each distribution center

tocenter = {}

for i in cartype:
    for j in country:
        for k in center:
            tocenter[(i,j,k)] = car.addVar(obj =carcost[j,i]+plant_center[j,k]*milecost[j,k[0]],vtype = GRB.INTEGER, name = 'x_%s_%s_%s' % (i,j,k))
car.update() 

 
# create variables: for each distribution center, whether or not it will open 
ope={}
for i in center:
    ope[i] = car.addVar(obj =anualcost[i[0]],vtype = GRB.BINARY, name = 'ope_%s_%s' % i)
    

# create variables: for each distribution center, whether or not it will service each dealership
sp={}
for c in center:
    for d in dealer:
        sp[c,d] = car.addVar(obj =center_dealer[c,d]*milecost[c[0],d[0]]*detotaldm[d],vtype = GRB.BINARY, name = 'sp_%s_%s' % (c,d))
    
#create Constraints that one dealer can only be serviced by one distribution center ,save it to carConstrs Dictionary
carConstrs={}
for d in dealer:
    constrName = 'onlyone_{0}' .format (d)
    carConstrs[constrName] = car.addConstr(quicksum(sp[c,d] for c in center ) == 1, name = constrName)
car.update()   

#create constraints that  not exceed manufacturing capacity hours
for p in country:
    constrName = 'totalhour_{0}' .format (p)
    carConstrs[constrName] = car.addConstr(quicksum(hours[p,t]*tocenter[t,p,k] for t in cartype for k in center ) <=totalhour[p] , name = constrName)
car.update() 

#create constraints that  total number of each type of car delivery to each distribution center is great and equal than 
#the total demand of each dealership that distribution center serve.

for c in center:
    for t in cartype:
        constrName = 'fullfil_{0}' .format (c,t)
        carConstrs[constrName] = car.addConstr(quicksum(tocenter[t,p,c]*ope[c] for p in country) >=quicksum(sp[c,d]*dedemand[d,t] for d in dealer), name = constrName)
car.update() 
   
#create constraints that want 4 distribution center in US,2 in MX, 3 in CA (previous defined as limit dictionary)
#limit={'US':4,'CA':3, 'MX':2}

for p in country:
    constrName = 'limit_{0}'.format(p) 
    carConstrs[constrName] = car.addConstr(quicksum(ope[i] for i in center if i[0]==p)==limit[p], name =constrName)
    
# create constraints that if the total number of cars deliver to each distribution center is positive(>=1), the center is open(ope[c]=1); 
#if no car deliver to the distribution center (0), the center is not open(ope[c]=0);  if the total number of dealerships each distribution 
#serve is positive(>=1), it is open(ope[c]=1);if the distribution center serve no dealership(ope[c]=0) ,it is not open(0). 

for c in center:
    constrName1 = 'matcht12_{0}' .format (c)
    constrName = 'match23_{0}' .format (c)   
    carConstrs[constrName1] = car.addConstr(quicksum(tocenter[t,p,c] for t in cartype  for p in country )>=ope[c], name =constrName1)
    carConstrs[constrName] = car.addConstr(quicksum(sp[c,d] for d in dealer )>=ope[c], name =constrName)

car.update()

# Solve model
car.optimize()       
car.write('car.lp') 

# get Solution
if car.status == GRB.OPTIMAL:
   tocenterSolution = [] 
   opeSolution=[]
   spSolution=[]
   for v in tocenter:
        if tocenter[v].x > 0.0:
            #print (v, tocenter[v].x) 
            # save Solution
            tocenterSolution.append((v[0], v[1], v[2][0], v[2][1], tocenter[v].x))
   for k in ope:
        if ope[k].x > 0.0:
           #print (k,ope[k].x) 
           opeSolution.append((k[0],k[1], ope[k].x))
   for j in sp:
        if sp[j].x> 0.0:
            #print (j,sp[j].x)
            spSolution.append((j[0][0],j[0][1],j[1][0],j[1][1], sp[j].x))
        
# save solution to database

cur.execute('DROP TABLE IF EXISTS tblSolution21') 
cur.execute('CREATE TABLE tblSolution21(cartype TEXT,plant TEXT, centercountry TEXT,centerID TEXT, Number of car  NUMERIC)')
cur.executemany('INSERT INTO tblSolution21 VALUES(?,?,?,?,?)', tocenterSolution)

cur.execute('DROP TABLE IF EXISTS tblSolution22') 
cur.execute('CREATE TABLE tblSolution22(centercountry TEXT, centerID TEXT,openornot NUMERIC)')
cur.executemany('INSERT INTO tblSolution22 VALUES(?,?,?)', opeSolution)

cur.execute('DROP TABLE IF EXISTS tblSolution23') 
cur.execute('CREATE TABLE tblSolution23(centercountry TEXT, centerID TEXT,dealercountry TEXT, dealerID TEXT, serviceornot NUMERIC)')
cur.executemany('INSERT INTO tblSolution23 VALUES(?,?,?,?,?)', spSolution)

con.commit() 

#print out on screen


cur.execute('SELECT* FROM tblSolution21')

for i in cur:
    print (i)
    
cur.execute('SELECT* FROM tblSolution22')

for i in cur:
    print (i) 

cur.execute('SELECT* FROM tblSolution23')
for i in cur:
    print (i) 
    
