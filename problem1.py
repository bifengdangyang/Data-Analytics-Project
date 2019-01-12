from gurobipy import*
import csv
import sqlite3
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()


# Build indexes: cm(calve month), dm(demand month);  Data define: production   
with open('production.csv', 'r') as f1:
    myReader = csv.reader(f1)
    production={}
    cm=(next(myReader)[1:13])
    dm=cm    
    for rows in myReader:
        for j in dm:
            production[(rows[0],j)]=float(rows[int(j)] ) 
f1.close()

#Data define: price(milk selling price/gallon) 
with open('demand_price.csv', 'r') as f2:
    myReader = csv.reader(f2)
    myReader.next()
    demand={}
    price={}    
    for rows in myReader:
        demand[rows[0]]=int(rows[1])
        price[rows[0]]=float(rows[2].replace('$',''))
f2.close() 

#Data define: fcost(feedcost/year)
with open('feedstock.csv', 'r') as f3:
    myReader = csv.reader(f3)
    fcost={}
    myReader.next()
    for rows in myReader:      
            fcost[rows[0]]=float(rows[1].replace('$',''))
f3.close() 

# create model        
cow=Model()
cow.modelSense=GRB.MINIMIZE
cow.update()  


#create  variables: for each month, the number of cows calve.
cownumber= {}
for c in cm:
    cownumber[c] = cow.addVar(obj=fcost[c],vtype =GRB.INTEGER,name ='cows_{0}'.format (c))

# create varaiables: for each month, the amount of milk that exceed demand   
excess={} 
exloss=0.2
for d in dm:
    excess[d]=cow.addVar(obj=exloss*price[d],vtype=GRB.CONTINUOUS,name='excess_%s'% (d))
 
# create varaiables: for each month, the amount of milk that is  in shortage
shortage={}
shortloss=1
for d in dm:
    shortage[d]=cow.addVar(obj=shortloss*price[d],vtype=GRB.CONTINUOUS,name='shortage_%s'% (d))
    
# create varaiables: for each month, whether it exceed demand
more={}
for d in dm:
    more[d]=cow.addVar(vtype=GRB.BINARY,name='more_%s' % (d))

# create varaiables: for each month, whether it will be in shortage
less={}
for d in dm:
    less[d]=cow.addVar(vtype=GRB.BINARY,name='less_%s'% (d))
    
cow.update() 


#create constraints: for each demand month, supply-exess+shortage=demand

days={'1':31,'2':28,'3':31,'4':30,'5':31,'6':30,'7':31,'8':31,'9':30,'10':31,'11':30,'12':31} 
   
Constrs={}

for d in dm:
    constrName = 'aimdemand_{0}'.format (d)
    Constrs[constrName] = cow.addConstr((quicksum(cownumber[c]*production[c,d] for c in cm)*days[d]-excess[d]+shortage[d]==demand[d]), name = constrName)

#create constraints: for each demand month, excess[d] should not exceed demand[d]. Because excess milk will be counted as cost,
# the moer it exceed demand,  higher cost coop will have, also  excess of milk require feeding more cow. so coop try to control milk 
# production around demand.  if more[d]=1, excess[d] exists; if more[d]=0, excess[d]=0

for d in dm:
    constrName = 'excesscap_{0}'.format (d)
    Constrs[constrName] = cow.addConstr(excess[d]<= demand[d]*more[d],name = constrName)

# create constraints : for each demand month, shortage can not be more than demand.
# if less[d]=1, less[d] exists; if less[d]=0, less[d]=0
for d in dm:
    constrName = 'shortcap_{0}'.format (d)
    Constrs[constrName] = cow.addConstr(shortage[d]<= demand[d]*less[d],name = constrName)

#create constraints: for each demand month, if the total production exceed (exceed[d]>0), then  no shortage(shortage[d]=0)
# if there is a shortage( shortage[d]>0), then no exceed.( exceed[d]=0). In conlusion, exceed[d] and shortage[d] can not both be 1.
for d in dm:
    constrName = 'notboth_{0}'.format (d)
    Constrs[constrName] = cow.addConstr(more[d]+less[d]<=1, name = constrName)

#solve model   
cow.optimize() 
 
cow.write('cow.lp') 

# get Solution
if cow.status == GRB.OPTIMAL:
    Solution1 = [] 
    Solution2 = [] 
    Solution3 = [] 
    total=0
    for v in cownumber:
        if cownumber[v].x > 0.0:
            total=total+cownumber[v].x
            #print (v, cownumber[v].x)
            # save Solution
            Solution1.append((v, cownumber[v].x))
    print '\nTotal number of cows needed is %s ' % (total)
    for v in excess:
        if excess[v].x > 0.0:
            #print ('excess',v, excess[v].x)
            # save Solution
            Solution2.append((v, excess[v].x))
    for v in shortage:
        if shortage[v].x > 0.0:
            #print ('shortage',v, shortage[v].x) 
            # save Solution
            Solution3.append((v, shortage[v].x))            

# save solution to database

cur.execute('DROP TABLE IF EXISTS problem1Solution1') 
cur.execute('CREATE TABLE problem1Solution1(carlvemonth TEXT, cownumber NUMERIC)')
cur.executemany('INSERT INTO  problem1Solution1 VALUES(?,?)', Solution1)
con.commit()

cur.execute('DROP TABLE IF EXISTS problem1Solution2') 
cur.execute('CREATE TABLE problem1Solution2(demandmonth TEXT, exceedmilk NUMERIC)')
cur.executemany('INSERT INTO  problem1Solution2 VALUES(?,?)', Solution2)
con.commit()

cur.execute('DROP TABLE IF EXISTS problem1Solution3') 
cur.execute('CREATE TABLE problem1Solution3(demandmonth TEXT, shortagemilk NUMERIC)')
cur.executemany('INSERT INTO  problem1Solution3 VALUES(?,?)', Solution3)
con.commit()
#print out on screen, uncomment below 
cur.execute('SELECT* FROM problem1Solution1')
for i in cur:
     print (i)

cur.execute('SELECT* FROM problem1Solution2')
for i in cur:
     print 'excess for demand month %s  is %s' %(i[0],i[1])
     
cur.execute('SELECT* FROM problem1Solution3')
for i in cur:
     print 'shortage for demand month %s is %s' %(i[0],i[1])     
