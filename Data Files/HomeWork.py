
import sqlite3
import pandas as pd

con=sqlite3.connect('cici.db')
con.text_factory = str
cur=con.cursor()

df=pd.read_csv('Stacked Roster.csv',parse_dates=['Snapshot Date','Start Date'])
df['Snapshot Date']=pd.to_datetime(df['Snapshot Date']).dt.date
df['Start Date']=pd.to_datetime(df['Start Date']).dt.date
df = df.where(pd.notnull(df), None)
StackedRoster=[]
StackedRoster=df.values.tolist()

cur.execute('DROP TABLE IF EXISTS StackedRoster') 
cur.execute('CREATE TABLE StackedRoster(SnapshotDate date, ID integer, fullName text, firstName text, lastName text, StartDate date, YearsService double)')
cur.executemany('INSERT OR IGNORE INTO StackedRoster VALUES(?,?,?,?,?,?,?)', StackedRoster)
con.commit()

df2=pd.read_csv('Employee Terminations.csv',parse_dates=['Termination Date'])
df2['Termination Date']=pd.to_datetime(df2['Termination Date']).dt.date
df2 = df2.where(pd.notnull(df2), None)
EmployeeTermination=[]
EmployeeTermination=df2.values.tolist()

cur.execute('DROP TABLE IF EXISTS EmployeeTermination') 
cur.execute('CREATE TABLE EmployeeTermination(ID integer, TerminationDate date)')
cur.executemany('INSERT OR IGNORE INTO EmployeeTermination VALUES(?,?)', EmployeeTermination)
con.commit()


df3=pd.read_csv('Employee Education.csv',parse_dates=['Year Degree Received'])
df3['Year Degree Received']=pd.to_datetime(df3['Year Degree Received']).dt.date
df3 = df3.where(pd.notnull(df3), None)
EmployeeEducation=[]
EmployeeEducation=df3.values.tolist()
 

cur.execute('DROP TABLE IF EXISTS EmployeeEducation') 
cur.execute('CREATE TABLE EmployeeEducation(ID integer, school text, degree text, received text, degreeDate date)')
cur.executemany('INSERT OR IGNORE INTO EmployeeEducation VALUES(?,?,?,?,?)', EmployeeEducation)
con.commit()


df4=pd.read_csv('Employee Demographics.csv',parse_dates=['Employee Birth Date'])
df4['Employee Birth Date']=pd.to_datetime(df4['Employee Birth Date']).dt.date
df4 = df4.where(pd.notnull(df4), None)
EmployeeDemographics=[]
EmployeeDemographics=df4.values.tolist()
 

cur.execute('DROP TABLE IF EXISTS EmployeeDemographics') 
cur.execute('CREATE TABLE EmployeeDemographics(ID integer, gender text, birthday date, diversity text)')
cur.executemany('INSERT OR IGNORE INTO EmployeeDemographics VALUES(?,?,?,?)', EmployeeDemographics)
con.commit()


sql1 = '''CREATE TABLE IF NOT EXISTS Stack_age AS 
select *, (StackedRoster.SnapshotDate- EmployeeDemographics.birthday) AS AGE from StackedRoster JOIN EmployeeDemographics on StackedRoster.ID=EmployeeDemographics.ID '''

cur.execute(sql1)
con.commit()

sql = '''CREATE TABLE IF NOT EXISTS HighDegree AS 
select ID , school, degree, received, max(degreeDate) as highestDegreeDate from EmployeeEducation group by ID  ORDER BY ID, degreeDate DESC'''

cur.execute(sql)
con.commit()


sql2 = '''CREATE TABLE IF NOT EXISTS Stack_age_HighDegree AS 
select SnapshotDate, Stack_age.ID, fullName, firstName, lastName, StartDate,YearsService,birthday,AGE, school,  degree as 'HighestDegree'  from Stack_age JOIN HighDegree on Stack_age.ID=HighDegree.ID AND HighDegree."max(degreeDate)"<SnapshotDate AND  received NOT NULL'''

cur.execute(sql2)
con.commit()


sql3 = '''CREATE TABLE IF NOT EXISTS Stack_age_HighDegree_percentage AS 
select * ,(select count(distinct(ID)) from EmployeeEducation where school=Stack_age_HighDegree.school)* 1.0/(select count(distinct(ID)) from EmployeeEducation) AS School_Attend_percentage from Stack_age_HighDegree'''

cur.execute(sql3)
con.commit()


sql4 = '''CREATE TABLE IF NOT EXISTS Stack_age_HighDegree_percentage_terminateInSix AS 
select SnapshotDate, Stack_age_HighDegree_percentage.ID, fullName, firstName, lastName, StartDate,YearsService,birthday,AGE, school, HighestDegree, School_Attend_percentage, (Date(Stack_age_HighDegree_percentage.SnapshotDate,'+6 months' )<EmployeeTermination.TerminationDate) as TerminateInSix from Stack_age_HighDegree_percentage JOIN EmployeeTermination on Stack_age_HighDegree_percentage.ID=EmployeeTermination.ID '''

cur.execute(sql4)
con.commit()




