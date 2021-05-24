from gurobipy import*
import sys
import csv
import pandas as pd
from sets import Set


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
    away={}    #for each team, the away teams that they play with
    
    for rows in myReader:
        matchup.append((rows[0],rows[1],rows[2]))
        if rows[0] not in away:
            away[rows[0]]=[rows[1]]
        else:
            if rows[1] not in away[rows[0]]:
                away[rows[0]].append(rows[1])

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

teamloc={}
for t in team:
    teamloc[t]=[float(teamin[t][0]), -1*float(teamin[t][1].replace('-',''))]

nostarday=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '129', '130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176']

