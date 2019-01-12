from gurobipy import*
import csv
import sqlite3
import pandas as pd
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()

# Build indexes: team; Data define: match(away vs home); 
with open('opponents_2018_V1.csv', 'r') as f1:
    myReader = csv.reader(f1)
    matchlist=[]
    ateam=[]
    hteam=['BYE']
    myReader.next()  
    for rows in myReader:
        matchlist.append(rows)        
        if rows[0] not in hteam:
            hteam.append(rows[0])
        if rows[0] not in ateam:
            ateam.append(rows[0])
f1.close()

#Data define: week, network, slot 
with open('GAME_VARIABLES_2018_V1.csv', 'r') as f2:
    myReader = csv.reader(f2)
    myReader.next()
    week=[]   
    network=[]
    slot=[]
    matchpoint={}
    for rows in myReader:
        if rows[2] not in week:
            week.append(rows[2])
        if rows[3] not in slot:
            slot.append(rows[3])
        if rows[4] not in network:
            network.append(rows[4])             
        matchpoint[(rows[0],rows[1],rows[2],rows[3],rows[4])]=float(rows[5])

f2.close() 

#Data define: w_slot_net(for each week, slot combination, the network that are available)
with open('NETWORK_SLOT_WEEK_2018_V1.csv', 'r') as f3:
    myReader = csv.reader(f3)
    w_slot_net={}
    myReader.next()
    for rows in myReader: 
        if(rows[0],rows[1]) not in w_slot_net:
            w_slot_net[(rows[0],rows[1])]=[rows[2]]
        else:
            w_slot_net[(rows[0],rows[1])].append(rows[2])
f3.close()

#Data define: teamin(information about team: conference, division, timezone, quality)
with open('TEAM_DATA_2018_v1.csv', 'r') as f4:
    myReader = csv.reader(f4)
    teamin={}
    myReader.next()
    for rows in myReader:      
            teamin[rows[0]]=(rows[1],rows[2],rows[3],rows[4])
f4.close() 

