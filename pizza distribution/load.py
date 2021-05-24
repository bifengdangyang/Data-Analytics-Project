import sqlite3
import pandas as pd
con=sqlite3.connect('newgmu.db')
con.text_factory = str
cur=con.cursor()

# read in dailydemand data, create dailydm table, 1 pound of pizza flour =3.57 cups of pizza flour
# The number of pounds of flour for each center=dailydemand for each center *7* 3.25 /3.57 
# save it to dictionry weekdm  in pounds
reader=pd.read_csv("average_daily_demand.csv")
cur.execute('DROP TABLE IF EXISTS dailydm') 
reader.to_sql("dailydm",con)
con.commit()

weekdm={}
cur.execute('select  "Distribution center"as center,sum("average daily demand")*7*3.25/3.57 as totalweekdemand from dailydm\
            where "average daily demand" is not NULL group by center' ) 
for i in cur:
    weekdm[i[0]]=i[1]


    
    
