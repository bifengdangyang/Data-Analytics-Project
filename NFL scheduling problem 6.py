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

myVars= {}
for a in ateam:
    for h in hteam:
        for w in week:
            for s in slot:
                for n in network:
                    if (a,h,w,s,n) in matchpoint:
                        myVars[a,h,w,s,n] = foot.addVar(obj=matchpoint[(a,h,w,s,n)]  ,vtype =GRB.BINARY,name ='playornot_{0}_{1}_{2}_{3}_{4}'.format (a,h,w,s,n))

#create constraint 1: each teammatch is played exactly once during the season
Constrs={}   
for i in matchlist:
    constrName = '01_EachGameOnce_{0}_{1}'.format(i[0],i[1])
    Constrs[constrName] = foot.addConstr(quicksum(myVars[i[0],i[1],w,s,n] for w in week for s in slot for n in network if(i[0],i[1],w,s,n) in matchpoint)==1,name = constrName)

# create constraint 2 :team play exactly one  game per week
for w in week:
    for t in ateam:
        constrName = '02_TeamOncePerWeek_{0}_{1}'.format(w,t)
        Constrs[constrName] = foot.addConstr(quicksum(myVars[t,h,w,s,n] for h in hteam for s in slot for n in network if (t,h,w,s,n) in matchpoint)
        +quicksum(myVars[a,t,w,s,n] for a in ateam for s in slot for n in network if (a,t,w,s,n) in matchpoint)== 1,name = constrName)


#create constraint 3: Bye can only happen between 4 and 12 weeks 
# each team can only have one BYE in whole season(1-17)
for t in ateam:
     constrName = '03_OneByeEachTeam_{0}'.format(t)
     Constrs[constrName] = foot.addConstr(quicksum(myVars[t,'BYE',w,s,n] for w in week for s in slot for n in network if (t,'BYE',w,s,n) in matchpoint)
     == 1,name = constrName)

#create constraint 3: each team can only have one BYE in (4-12)weeks; combine with previous constraint, it makes Bye happen only between week4-week12
for t in ateam:
     constrName = '03_ByeBw4and12_{0}'.format(t)
     Constrs[constrName] = foot.addConstr(quicksum(myVars[t,'BYE',w,s,n] for w in week[3:12] for s in slot for n in network if (t,'BYE',w,s,n) in matchpoint)
     == 1,name = constrName) 
# create constraint : no team plays 4 consecutive home/away games in a season

for i in range(14):
    for t in ateam:
        constrName = '03b_No4ConsecuAway_{0}'.format(t)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for h in hteam for w in week[i:i+4] for s in slot for n in network if (t,h,w,s,n) in matchpoint)<=3,name=constrName)
        constrName1 = '03b_No4ConsecuHome_{0}'.format(t)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a in ateam for w in week[i:i+4] for s in slot for n in network if (a,t,w,s,n) in matchpoint)<=3,name=constrName1)     
#create constraint 4: no more than 6 byes in a given week  
for w in week:
    constrName = '04_Atmost6ByePerWeek_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,'BYE',w,s,n] for a in ateam for s in slot for n in network if (a,'BYE',w,s,n) in matchpoint)<=6,name=constrName)

#create constraint 5: if have early bye in 2017 ,no ealry bye in 2018
earlybird=['MIA','TB']
constrName = '05_earlybirdnoearly'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,'BYE','4',s,n] for a in earlybird for s in slot for n in network if (a,'BYE','4',s,n) in matchpoint)==0,name=constrName)

#create constraint 6: one THUN per week between week1 and week15    
for w in week[0:15]:
    constrName = '06_OneThunPerWeek_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'THUN',n] for a in ateam  for h in hteam for n in network if (a,h,w,'THUN',n) in matchpoint)==1,name=constrName)
       
#create constraint 7:  one SATE and one SATL each week during week15, week16
for w in week[14:16]:
    constrName1 = '07_OneSATE15_16_{0}'.format(w)
    constrName2 = '07_OneSATL15_16_{0}'.format(w)
    Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,h,w,'SATE',n] for a in ateam  for h in hteam for n in network if (a,h,w,'SATE',n) in matchpoint)==1,name=constrName1)
    Constrs[constrName2]=foot.addConstr(quicksum(myVars[a,h,w,'SATL',n] for a in ateam  for h in hteam for n in network if (a,h,w,'SATL',n) in matchpoint)==1,name=constrName2)
    
#create constraint 8a:  one double header per week in week1 through 16
for w in week[0:16]:
    constrName = '08a_OneSUNDperWeek1_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'SUND',n] for a in ateam  for h in hteam  for n in network if (a,h,w,'SUND',n) in matchpoint)==1,name=constrName)
    
#create constraint 8b:CBS and FOX cannot have more than two double headers in a row

for i in range(15):
    constrName = '08b_NomoreTwoSUNDCBS_{0}_{1}'.format(i+1,i+3)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'SUND','CBS'] for a in ateam  for h in hteam for w in week[i:i+3] if (a,h,w,'SUND','CBS') in matchpoint)<=2,name=constrName)    
    constrName1 = '08b_NomoreTwoSUNDFOX_{0}_{1}'.format(i+1,i+3)
    Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,h,w,'SUND','FOX'] for a in ateam  for h in hteam for w in week[i:i+3] if (a,h,w,'SUND','FOX') in matchpoint)<=2,name=constrName1) 
# create constraint 8c: CBS and FOX each have a double header in week17
constrName = '08c_CBSDoubleHeader'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'SUND','CBS'] for a in ateam  for h in hteam for w in week[16:17] if (a,h,w,'SUND','CBS') in matchpoint)==1,name=constrName)   

constrName = '08c_FOXDoubleHeader'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'SUND','FOX'] for a in ateam  for h in hteam for w in week[16:17] if (a,h,w,'SUND','FOX') in matchpoint)==1,name=constrName)

#create  constraint 9: One SUNN game per week from week1 to week16
for w in week[0:16]:
    constrName = '09_OneSUNN1_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'SUNN',n] for a in ateam  for h in hteam for n in network if (a,h,w,'SUNN',n) in matchpoint)==1,name=constrName)

#create  constraint 10a: Two MONN in week1;
constrName = '10a_TwoMONN1'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,'1','MONN',n] for a in ateam  for h in hteam for n in network if (a,h,'1','MONN',n) in matchpoint)==2,name=constrName)

#create  constraint 10b: MONN must be hosted by west coast team or mountain team;
hoster=['LAC','SF','SEA','OAK','LAR','DEN','ARI']
constrName = '10b_host'
Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'MONN',n] for a in ateam  for h in hoster for w in week for n in network if (a,h,w,'MONN',n) in matchpoint)==17,name=constrName)
#create  constraint 10c: one MONN per week from week2 to week16.      15 in total;
for w in week[1:16] :
    constrName = '10c_OneMONN2_16_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,'MONN',n] for a in ateam  for h in hteam for n in network if (a,h,w,'MONN',n) in matchpoint)==1,name=constrName)

 #solve model   
foot.optimize()                     
foot.write('foot.lp')  


i=0
if foot.status == GRB.OPTIMAL:  
    Solution = [] 
    for v in myVars:
        if myVars[v].x> 0:
            i=i+1
            #print (v)
            Solution.append((v[0],v[1],v[2],v[3],v[4]))
elif foot.status == GRB.INFEASIBLE:
     foot.computeIIS()
     foot.write('myInfeasibleModel.ilp')
print i 

# save solution to database

cur.execute('DROP TABLE IF EXISTS problem6solution') 
cur.execute('CREATE TABLE problem6solution(Awayteam TEXT, Hometeam TEXT, Week TEXT,Slot TEXT,Network TEXT)')
cur.executemany('INSERT INTO  problem6solution VALUES(?,?,?,?,?)', Solution)
con.commit()

#print out on screen, uncomment below 
cur.execute('SELECT* FROM problem6solution')
for i in cur:
    print (i)   
