from gurobipy import*
import csv
import sqlite3
from loaddata import *
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()

# create model        
foot=Model()
foot.modelSense=GRB.MAXIMIZE
foot.update()

#create variables: for each game whether or not it will play at that week ,that slot, that newwork
#create tuplelist season 
with open('GAME_VARIABLES_2018_V1.csv', 'r') as f2:
    myReader = csv.reader(f2)
    myReader.next()
    myVars= {}
    for rows in myReader:
        myVars[rows[0],rows[1],rows[2],rows[3],rows[4]] = foot.addVar(obj=matchpoint[(rows[0],rows[1],rows[2],rows[3],rows[4])] ,vtype =GRB.BINARY,name ='playornot_{0}_{1}_{2}_{3}_{4}'.format (rows[0],rows[1],rows[2],rows[3],rows[4]))
f2.close()


#create constraint 1: each teammatch is played exactly once during the season
Constrs={}   
for i in matchlist:
    constrName = '01_EachMatchOnce_{0}_{1}'.format(i[0],i[1])
    Constrs[constrName] = foot.addConstr(quicksum(myVars[i[0],i[1],w,s,n] for i[0],i[1],w,s,n in season.select(i[0],i[1],'*','*','*' ))==1,name = constrName)
    
#create constraint 2 :team play exactly one game per week(including both home and away game)
for w in week:
    for t in ateam:
        constrName = '02_TeamOncePerWeek_{0}_{1}'.format(w,t)
        Constrs[constrName] = foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',w,'*','*'))
        +quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,w,'*','*'))== 1,name = constrName) 

        
#create constraint 3: Bye can only happen between 4 and 12 weeks : see the game variables file, all BYE happen between 4 and 12 weeks. 
#the constraint can be ignored, but I write it anyway
for t in ateam:
     constrName = '03_ByeBw4and12_{0}'.format(t)
     Constrs[constrName] = foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'BYE',week[3:12],'*','*') )
     == 1,name = constrName)
     
#create constraint 4: no more than 6 byes in a given week  
for w in week:
    constrName = '04_Atmost6ByePerWeek_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','BYE',w,'*','*'))<=6,name=constrName)

#create constraint 5: if have early bye in 2017 ,no ealry bye in 2018
earlybird=['MIA','TB']
constrName = '05_earlybirdnoearly'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(earlybird,'BYE','4','*','*'))==0,name=constrName)


#create constraint 6: one THUN per week between week1 and week15    
for w in week[0:15]:
    constrName = '06_OneTHUNPerWeek_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*',w,'THUN','*'))==1,name=constrName)
       
#create constraint 7:  one SATE and one SATL each week during week15, week16
for w in week[14:16]:
    for s in ['SATE','SATL']:
        constrName = '07_One_{0}15_16_{1}'.format(s,w)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*',w,s,'*'))==1,name=constrName)
   
#create constraint 8a:  one double header per week in week1 through 16
for w in week[0:16]:
    constrName = '08a_OneSUNDperWeek1_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n  in season.select('*','*',w,'SUND','*'))==1,name=constrName)
    
#create constraint 8b:CBS and FOX cannot have more than two double headers in a row
for n in ['CBS','FOX']:
    for i in range(15):
        constrName = '08b_NomoreTwoSUND_{0}_{1}_{2}'.format(n,i+1,i+3)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*', week[i:i+3],'SUND',n))<=2,name=constrName)    

    
# create constraint 8c: CBS and FOX each have a double header in week17
for n in ['CBS','FOX']:
    constrName = '08c_{0}_OneDoubleHeader17'.format(n)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*', week[16:17],'SUND',n))==1,name=constrName)   

#create  constraint 9: One SUNN game per week from week1 to week16
for w in week[0:16]:
    constrName = '09_OneSUNN1_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n  in season.select('*','*', w,'SUNN','*'))==1,name=constrName)

#create  constraint 10a: Two MONN in week1;
constrName = '10a_TwoMONN1'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*','1','MONN','*'))==2,name=constrName)

#create  constraint 10b: MONN must be hosted by west coast team or mountain team;
hoster=['LAC','SF','SEA','OAK','LAR','DEN','ARI']
constrName = '10b_host'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',hoster,'*','MONN','*'))==17,name=constrName)

#create  constraint 10c: one MONN per week from week2 to week16.      15 in total;
for w in week[1:16] :
    constrName = '10c_OneMONN2_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*',w,'MONN','*'))==1,name=constrName)
    
    
#solve model   
foot.optimize()                     
foot.write('foot.lp')  
foot.write('foot.sol')
foot.write('foot.mst')
i=0
if foot.status == GRB.OPTIMAL:  
    Solution = [] 
    for v in myVars:
        if myVars[v].x> 0:
            i=i+1
            #print (v)
            Solution.append(v)
elif foot.status == GRB.INFEASIBLE:
     foot.computeIIS()
     foot.write('myInfeasibleModel.ilp')
print (i)

# save solution to database

cur.execute('DROP TABLE IF EXISTS problem6solution') 
cur.execute('CREATE TABLE problem6solution(Awayteam TEXT, Hometeam TEXT, Week TEXT,Slot TEXT,Network TEXT)')
cur.executemany('INSERT INTO  problem6solution VALUES(?,?,?,?,?)', Solution)
con.commit()

#print out on screen, uncomment below 
cur.execute('SELECT* FROM problem6solution')
for i in cur:
    print (i)    
    
