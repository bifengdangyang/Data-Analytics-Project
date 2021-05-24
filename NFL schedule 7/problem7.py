import sys
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
    
    
#create constraint 11: no team plays 4 consecutive home/away games in a season
for i in range(14):
    for t in ateam:
        constrName = '11_No4ConsecuAway_{0}_during_{1}_{2}'.format(t,i+1,i+4)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[i:i+4],'*','*'))<=3,name=constrName)
        constrName1 = '11_No4ConsecuHome_{0}_during_{1}_{2}'.format(t,i+1,i+4)
        Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[i:i+4],'*','*'))<=3,name=constrName1)
        

#create constraint 12: no team plays 3 consecutive home/away games in weeks1,2,3,4,5 and 15,16,17
for i in range(3):
    for t in ateam:
        constrName = '12a_No3ConsecuAway_{0}_during{1}_{2}'.format(t,i+1,i+3)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[i:i+3],'*','*'))<=2,name=constrName)
        constrName1 = '12a_No3ConsecuHome_{0}_during{1}_{2}'.format(t,i+1,i+3)
        Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[i:i+3],'*','*'))<=2,name=constrName1)   


for t in ateam:
    constrName = '12b_No3ConsecuAway15_17_{0}'.format(t)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[14:17],'*','*'))<=2,name=constrName)
    constrName1 = '12b_No3ConsecuHome15_17_{0}'.format(t)
    Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[14:17],'*','*'))<=2,name=constrName1) 

#create constraint 13: each team play at least 2 home/away games every 6 weeks
for i in range(12):
    for t in ateam:
        constrName = '13a_atleast2Away_{0}_during{1}_{2}'.format(t,i+1,i+6)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[i:i+6],'*','*'))>=2,name=constrName)
        constrName1 = '13b_atleast2Home_{0}_during{1}_{2}'.format(t,i+1,i+6)
        Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[i:i+6],'*','*'))>=2,name=constrName1)   

#create constraint 14 : each team play at least 4 home/away games every 10 weeks
for i in range(7):
    for t in ateam:
        constrName = '14a_atleast4Away_{0}_during{1}_{2}'.format(t,i+1,i+10)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[i:i+10],'*','*'))>=4,name=constrName)
        constrName1 = '14b_atleast4Home_{0}_during{1}_{2}'.format(t,i+1,i+10)
        Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[i:i+10],'*','*'))>=4,name=constrName1)   

#create constraint 15 : Professor drops it
#create constraint 16 : For team that playing on MONN in a given week, they can not play Thursday in the next two weeks
thur=['THUN','THUL','THUE']   
for i in ateam:
    for w in week[:15]:
        constrName = '16_MONNNoThurafter2_{0}_{1}'.format(i,w)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',week[int(w):int(w)+2],thur,'*')) +quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',i,week[int(w):int(w)+2],thur,'*')) 
                                        + quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',w,'MONN','*'))+quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',i,w,'MONN','*'))<=1,name=constrName)


#create constraint 17 : For team that playing on Thursday night will play at home on sundays the previous week
    
sun=['SUNN', 'SUND', 'SUNE', 'SUNL', 'SUNI', 'SUNB']   

for i in ateam:
    for w in week[1:17]:
        constrName = '17_ThurhomebeforeA_{0}_{1}'.format(i,w)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',str(int(w)-1),sun,'*')) +quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',w,thur,'*'))+
           quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',i,w,thur,'*'))<=1,name=constrName)

   

#create constraint 18 : For team that coming off a BYE ,they can not play Thursday game in the next week
   
for i in ateam:
    for w in week[:16]: 
        constrName = '18_BYEnoThur_{0}_on{1}'.format(i,w)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',week[int(w)],thur,'*')) + quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'BYE',w,'*','*'))+
                                        quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',i,week[int(w)],thur,'*')) <=1,name=constrName)   

#create constraint 19 : week 17 can only consist of games between division oppoments
# check the data file ,all games in week17 are division oppoments, not necessary to write constraints here, but I write anyway
for a in ateam:
    for h in ateam:        
        constrName = '19_ifNotdivmemNo17_{0}_{1}'.format(a,h)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,'17','*','*') if teamin[a][0]!=teamin[h][0] or teamin[a][1]!=teamin[h][1])==0,name=constrName)      

#create constraint 20 : for teams that playing Thursday as away team, they should not travel one than 1 time zone 
#combine with constraint 6 
for w in range(1,16):
    constrName = '20_THUNtravelatmost1Zone_{0}'.format(w)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*',str(w),thur,'*') if abs(int(teamin[a][2])-int(teamin[h][2]))<=1 )==1,name=constrName)

 
foot.update
foot.write('foot.lp') 

#solve model
#foot.setParam('SolutionLimit', 1)
foot.setParam('MIPFocus', 1) 
foot.optimize()                     


i=0
if foot.status == GRB.OPTIMAL:
# if you only want to see the feasible solution and take less time, uncomment line 203 and 195 , comment line 201
#if foot.status != GRB.INFEASIBLE:  
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

cur.execute('DROP TABLE IF EXISTS problem7solution') 
cur.execute('CREATE TABLE problem7solution(Awayteam TEXT, Hometeam TEXT, Week TEXT,Slot TEXT,Network TEXT)')
cur.executemany('INSERT INTO  problem7solution VALUES(?,?,?,?,?)', Solution)
con.commit()

#print out on screen, uncomment below 
cur.execute('SELECT* FROM problem7solution')
for i in cur:
    print (i) 