#questiion:This data set consists of 24 trip files contained in a zipped folder and 1 terminal file.  
# =============================================================================
# Capital_Bikeshare_Terminal_Locations.csv (1 file in total)
# •	TERMINAL_NUMBER:  The unique numeric identifier for the terminal
# •	ADDRESS:  The street address for the terminal
# •	LATITUDE:  The latitude for the terminal
# •	LONGITUDE:  The longitude of the terminal
# •	DOCKS:  The number of docking stations at the terminal
# 
# Year_201X_QTR_Y_bikeTrips.csv (24 files in total)
# •	TRIP_DURATION:  The length of time the bike was leased (measured in milliseconds)
# •	START_DATE:  The date and time the bike lease started
# •	START_STATION:  The station ID where the bike trip started
# •	STOP_DATE:  The date and time the bike lease ended
# •	STOP_STATION:  The station ID where the bike lease ended
# •	BIKE_ID:  The unique identifier for the bike that was leased
# •	USER_TYPE:  Indicates whether the user was a registered user (member) or a casual user (not a member)
# =============================================================================


# 1 Get the basic station information into the database
import csv,sqlite3
con=sqlite3.connect('newgmu.db')
cur=con.cursor()


cur.execute('DROP TABLE IF EXISTS bike_terminal')   
cur.execute('CREATE TABLE bike_terminal(OBJECTID INTEGER,ID INTEGER,ADDRESS TEXT,TERMINAL_NUMBER  NUMERIC,\
LATITUDE NUMRIC,LONGITUDE NUMRIC,INSTALLED  BOOLEAN,LOCKED  BOOLEAN,INSTALL_DATE ,REMOVAL_DATE ,\
TEMPORARY_INSTALL BOOLEAN,NUMBER_OF_BIKES INTEGER,NUMBER_OF_EMPTY_DOCKS INTEGER,\
X NUMRIC,Y NUMRIC,SE_ANNO_CAD_DATA)')

with open('C:/Users/xianci/.spyder/Capital_Bike_Share_Locations.csv','rb') as f:
    reader=csv.reader(f)
    next(reader)
    bikelocation=list(reader)
    
cur.executemany('INSERT INTO bike_terminal VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',bikelocation) 

con.commit() 
cur.execute('SELECT* FROM bike_terminal')
count=0
for i in cur:
    count=count+1
print count

f.close()
con.close()




 # 2  Get the trip data into the database,Iterate over all the data files that contain trip history (these are the 24 data files contained in the
# zipped directory) and load them into a single data table in a database.  
 #unzip Capital_BikeShare_Data.zip in current directory , find all related files in the directory
import glob
filenames = glob.glob('*bikeTrips.csv')

#create table 
con=sqlite3.connect('newgmu.db')
cur=con.cursor()
cur.execute('DROP TABLE IF EXISTS trips')   
cur.execute('CREATE TABLE trips(TRIP_DURATION INTEGER,START_DATE DATETIME,START_STATION NUMERIC,STOP_DATE  DATETIME,\
STOP_STATION NUMRIC,BIKE_ID TEXT,USER_TYPE TEXT)')

# iterate through all files, save it to list ,then load in table
alllist=[]
for files in filenames:       
    with open(files,'rb') as f:
        reader=csv.reader(f)
        next(reader,None)
        bike=list(reader)
        alllist.extend(bike)
        to_db=[(i[0],i[1],i[2],i[3],i[4],i[5],i[6]) for i in bike]
    print files+' number of records loaded: ',len(bike)  
    f.close()
    cur.executemany('INSERT INTO trips(TRIP_DURATION,START_DATE,START_STATION,STOP_DATE,STOP_STATION,BIKE_ID,USER_TYPE)\
                    VALUES(?,?,?,?,?,?,?);',to_db) 
    con.commit()


print 'Total number of records for 24 dataset  : ',len(alllist)
con.close()

#3 Create a routine that returns a dictionary that has as its keys all pairs of bike terminals and the distance between those two locations
import sqlite3 ,haversine,pickle
from haversine import haversine


con=sqlite3.connect('newgmu.db')
cur=con.cursor()

# retrieve data from joined table
cur.execute('SELECT bikes1.TERMINAL_NUMBER,bikes1.LATITUDE,bikes1.LONGITUDE,bikes2.TERMINAL_NUMBER,bikes2.LATITUDE,bikes2.LONGITUDE \
            FROM bike_terminal AS bikes1 , bike_terminal AS bikes2 WHERE bikes1.TERMINAL_NUMBER>bikes2.TERMINAL_NUMBER ;' )
con.commit()

#save data that meet conditon to dictionary , save dictionary to file
terminal_distance={}
for row in cur:
    station1 = (row[1],row[2])
    station2 = (row[4],row[5])
    terminal_distance[(row[0],row[3])]= haversine(station1, station2)    
    con.commit()
print terminal_distance  
pickle.dump(terminal_distance ,open('terminaldict.p','wb'))


con.commit()
cur.close()
con.close()

#4 Create a routine that takes as its argument a dictionary, a Bikeshare terminal, and a distance and returns
# a list of all stations that are within the specified distance of the specified docking station

import sqlite3 ,haversine,pickle
from haversine import haversine

# load dictionary file from current directory (produced from problem 4),find data that meet condition, save to a list
terminals=pickle.load(open('terminaldict.p','rb'))

def nearbystations(allstation,terminal_number,distance):
    stations=[]
    for i in terminals:
        if terminal_number == i[0]:
            if terminals[i]<=distance:
                stations.append(i[1])
        if terminal_number == i[1]:
            if terminals[i]<=distance:
                stations.append(i[0])
    return 'Stations that are within {} km from station {} are: {}  and number of these stations is:{}'.format(distance,\
                                     terminal_number, stations,len(stations))

    
    
    
   
    
print nearbystations(terminals,31621,1)


#5 Create a routine that takes as its argument any two BikeShare stations and a start and end date and returns the total number
# of trips made by riders between those two stations over the period of time specified by the start and stop date.  

import sqlite3

con=sqlite3.connect('newgmu.db')
cur=con.cursor()

def allbikes(station1,station2,startdate,stopdate):
    cur.execute('SELECT START_STATION,STOP_STATION,DATE(START_DATE),DATE(STOP_DATE) FROM trips')
    con.commit()
    count1=0
    count2=0
    for row in cur:
        if station1==row[0] and station2==row[1]:
            if row[2] >=startdate and row[3]<=stopdate:
                count1=count1+1
                print row
        if station1==row[1] and station2==row[0]:
            if row[2] >=startdate and row[3]<=stopdate:
                count2=count2+1
                print row
    count=count1+count2
    return count  
                


print allbikes(31613,31607,'2010-12-31','2011-01-10')
con.close()