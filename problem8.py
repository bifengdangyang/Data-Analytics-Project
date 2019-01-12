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
                                        + 2*( quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(i,'*',w,'MONN','*'))+quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',i,w,'MONN','*')))<=2,name=constrName)


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



#create constraint 21 :  no team play moe than 2 road games against teams coming off a BYE(4-12)
link1={}

for t in ateam:
    for w in week[4:13]:
        link1[t,w]=foot.addVar(obj=0,vtype =GRB.BINARY,name ='21hardornot_{0}_{1}'.format(t,w))
        
for i in range(4,13):
    for h in ateam:
        for t in ateam:
            constrName = '21a_agaistByeNoMoreTwo_{0}_{1}_{2}'.format(i+1,h,t)
            Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,'BYE',week[i-1],'*','*'))+
               quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(t,h,week[i],'*','*'))<=1+link1[t,week[i]],name=constrName)
        
for t in ateam:
    constrName = '21b_agaistByeNoMoreTwo_{0}'.format(t)
    Constrs[constrName]=foot.addConstr(quicksum(link1[t,w] for w in week[4:13])<=2,name=constrName)
    
#create constraint 22a :  division oppoments cannot play each other back to back 
for i in range(16):
    for a in ateam:
        for h in match[a]:
            if h in divmem[a]:        
                constrName = '22a_NoBacktoBack_{0}_{1}_{2}'.format(i+1,a,h)
                Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,week[i],'*','*')) +
                           quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,week[i+1],'*','*'))
                           <=1,name=constrName)    


#create constraint 22b :  division oppoments cannot play each other gapped with a BYE 
for i in range(1,16):
    for a in ateam:
        for h in match[a]:
            if h in divmem[a]:        
                constrName = '22bb_NoGappedBYE_{0}_{1}_{2}'.format(i+1,a,h)
                Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,week[i-1],'*','*')) +
                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'BYE',week[i],'*','*'))+
                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,week[i+1],'*','*'))
                       <=2,name=constrName)            

for i in range(1,16):
    for a in ateam:
        for h in match[a]:
            if h in divmem[a]:                
                constrName = '22bc_NoGappedBYE_{0}_{1}_{2}'.format(i+1,a,h)
                Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,week[i-1],'*','*')) +
                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,'BYE',week[i],'*','*'))+
                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,week[i+1],'*','*'))
                        <=2,name=constrName)
#create constraint 23 :  team should not play 3 consecutive home/away games between week4 to 16
pena1={}
for t in ateam:
    for w in week[3:14]:
        pena1[t,w]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='23softornot_{0}_{1}'.format(t,w))
        

for i in range(3,14):
    for t in ateam:
        constrName = '23a_No3ConsecuAway_{0}_during_{1}_{2}'.format(t,i+1,i+3)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[t,h,w,s,n] for t,h,w,s,n in season.select(t,'*',week[i:i+3],'*','*'))<=2+pena1[t,week[i]],name=constrName)
        constrName1 = '23a_No3ConsecuHome_{0}_during_{1}_{2}'.format(t,i+1,i+3)
        Constrs[constrName1]=foot.addConstr(quicksum(myVars[a,t,w,s,n] for a,t,w,s,n in season.select('*',t,week[i:i+3],'*','*'))<=2+pena1[t,week[i]],name=constrName1)

for t in ateam:
    constrName = '23b_agaistByeNoMoreTwo_{0}'.format(t)
    Constrs[constrName]=foot.addConstr(quicksum(pena1[t,w] for w in week[3:14])<=1,name=constrName)

#create constraint 24 : No team should play consecutive road games involving travel across more than 1 time zone.
pena2={}
for t in ateam:
    for w in range(1,17):
        pena2[t,str(w)]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='24softornot_{0}_{1}'.format(t,str(w)))
      
for w in range(1,17):
    for a in ateam:
        for h1 in match[a]:
            for h2 in match[a]:
                constrName = '24_TwoRoadin1Zone_{0}_{1}'.format(w,a)
                Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h1,str(w),'*','*') if abs(int(teamin[a][2])-int(teamin[h1][2]))>=2 )+
                                   quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h2,str(w+1),'*','*') if  
                                   abs(int(teamin[a][2])-int(teamin[h2][2]))>=2)<=1+pena2[a,str(w)],name=constrName)

#create constraint 25 :  no team should open the season with two away games
pena3={}

for t in ateam:
    pena3[t]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='25softornot_{0}'.format(t))
                      
for a in ateam:               
    constrName = '25_NoOpenTwoAway_{0}'.format(a)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*','1','*','*'))+
                               quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*','2','*','*'))<=1+pena3[a],name=constrName)
           
#create constraint 26 :  no team should end the season with two away games 
pena4={}
for t in ateam:
    pena4[t]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='26softornot_{0}'.format(t))
                      
for a in ateam:              
    constrName = '26_NoEndTwoAway_{0}'.format(a)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*','16','*','*'))+
                               quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*','17','*','*'))<=1+pena4[a],name=constrName)
                
#create constraint 27 : Florida teams should not play Early home games in the month of SEPT
pena5={}
for t in ateam:
    pena5[t]=foot.addVar(obj=-2,vtype =GRB.INTEGER,name ='27softornot_{0}'.format(t))
                  
florida=['TB','JAC','MIA']
sep=['1','2','3','4']
early=['SUNE']
for t in florida:
    constrName = '27_FloridaNoEgameinSep_{0}'.format(t)
    Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',t,sep,early,'*'))==0+pena5[t],name=constrName)
                    
#create constraint 28 : CBS and FOX  should not have fewer than 5 games each on a Sunday. if it happens,
# it can only happen once in the season for each network
sunday=['SUND','SUNE','SUNL'] 
two=['CBS','FOX']

pena6={}
for n in two:
    for w in week:
        pena6[n,w]=foot.addVar(obj=-2,vtype =GRB.BINARY,name ='28softornot_{0}_{1}'.format(n,w))
       
for w in week:
    for n in two:
            constrName = '28a_less5Sunday_{0}_{1}'.format(n,w)
            Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*','*',w,sunday,n))>=5-pena6[n,w],name=constrName)

for n in two:
    constrName = '28b_less5Sunday_{0}'.format(n)
    Constrs[constrName]=foot.addConstr(quicksum(pena6[n,w] for w in week)<=1,name=constrName)
                                 
            
#create constraint 29 : CBS and FOX should not lose both games between divisional opponents for their assigned 
# conference(FOX-NFC; CBS-AFC)
pena7={}
for a in ateam:
    for h in divmem[a]:
        pena7[a,h]=foot.addVar(obj=-3,vtype =GRB.BINARY,name ='29softornot_{0}_{1}'.format(a,h))
    
for a in ateam:
        for h in match[a]:
            if h in divmem[a]:    
                if teamin[a][0]=='AFC' and teamin[h][0]=='AFC':
                     constrName = '29a_CBSAtLeastOne_{0}_{1}'.format(a,h)
                     Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,'*','*','CBS'))+
                                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,'*','*','CBS'))>=1-pena7[a,h],name=constrName)

for a in ateam:
        for h in match[a]:
            if h in divmem[a]:
                if teamin[a][0]=='NFC'and teamin[h][0]=='NFC':
                     constrName = '29b_FOXAtLeastOne_{0}_{1}'.format(a,h)
                     Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,'*','*','FOX'))+
                                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,'*','*','FOX'))>=1-pena7[a,h],name=constrName)
                     
            
#create constraint 30 : The series between two divisional opponents should not end in the first half of the season
# week 1 through week 9
pena8={}
for a in ateam:
        for h in match[a]:
            if h in divmem[a]:
                pena8[a,h]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='30softornot_{0}_{1}'.format(a,h))
             
for a in ateam:
        for h in match[a]:
            if h in divmem[a]:
                constrName = '30_Notfirst9week{0}_{1}'.format(a,h)
                Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,h,week[:9],'*','*'))+
                                       quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(h,a,week[:9],'*','*'))<=1+pena8[a,h],name=constrName)
                        
            
#create constraint 31 : Teams should not play on the road the week following a Monday night game
pena9={}
for a in ateam:
    for w in week[:16]:
        pena9[a,w]=foot.addVar(obj=-1,vtype =GRB.BINARY,name ='31softornot_{0}_{1}'.format(a,w))
           
for w in week[:16]:
    for a in ateam:
        constrName = '31_NoroadAfterMONN{0}_{1}'.format(a,w)
        Constrs[constrName]=foot.addConstr(quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*',w,'MONN','*'))+
                           quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select('*',a,w,'MONN','*'))+
                           quicksum(myVars[a,h,w,s,n] for a,h,w,s,n in season.select(a,'*',str(int(w)+1),'*','*'))<=1+pena9[a,w],name=constrName)
 
              
foot.update
foot.write('foot.lp') 
#solve model
foot.setParam('SolutionLimit', 1)
#foot.setParam('MIPGap', 0.38)
foot.setParam('MIPFocus', 1) 
foot.optimize() 

i=0
Solution = []
#if foot.status == GRB.OPTIMAL:
if foot.status != GRB.INFEASIBLE:  
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

cur.execute('DROP TABLE IF EXISTS problem8solution') 
cur.execute('CREATE TABLE problem8solution(Awayteam TEXT, Hometeam TEXT, Week TEXT,Slot TEXT,Network TEXT)')
cur.executemany('INSERT INTO  problem8solution VALUES(?,?,?,?,?)', Solution)
con.commit()

#print out on screen, uncomment below 
cur.execute('SELECT* FROM problem8solution')
for i in cur:
    print (i) 

