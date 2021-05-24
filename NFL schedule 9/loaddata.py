from gurobipy import*
import csv
import pandas as pd



# Build indexes: teamsta
with open('stadium_avail.csv', 'r') as f1:
    myReader = csv.reader(f1)
    teamsta={}
    for rows in myReader:
        teamsta[rows[0]]=[x for x in rows[1:] if x]

f1.close()

#Data define: matchup
with open('matchUps_2018.csv', 'r') as f2:
    myReader = csv.reader(f2)
    myReader.next()
    matchup=[]   # home, away, match num
    match=[]    # home and away

    
    for rows in myReader:
        matchup.append((rows[0],rows[1],rows[2]))

        if rows[:2] not in match:
            match.append(rows[:2])


f2.close()

#Data define: team
with open('team_data_2018.csv', 'r') as f3:
    myReader = csv.reader(f3)
    teamin={}
    team=[]
    myReader.next()
    for rows in myReader: 
        teamin[rows[1]]=rows[2:]
        team.append(rows[1])
            
f3.close()

days=[]
for i in range(1,177):
     days.append(str(i))



       
