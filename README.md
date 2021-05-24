>>>>Project 1: Knowledge Discovery for Crimes Against Children(Group Project) <<<<<<<

This group project seeks to discover knowledge about crimes against children through data mining of the National Incident-Based Reporting System (NIBRS) crime data source.  The main goal is to identify the characteristics of victims, offenders, and the situational threats in which children are especially vulnerable to categories of offenses. 
 My role in the team is to 
•	balance the unbalanced dataset
•	 visualize dataset’s multiple  perspectives using SHAP chart, simple dependence plot, Lime chart( Local interpretable model agnostic explanations) 
•	build several  machine learning models( penalized logistic regression, decision trees, random forest, Gradient Boosting)  to get insight from dataset.  I used Python and R for my work. 
Python API:  Pandas, NumPy, scikit-learn, Xgboost, matplotlib.
R  API:  dplyr,tidyr,DMwR,ggplot2,iml,data.table

Files:  FINAL KD-CAC Project Presentation.pptx ,  ProjectCode.R 

>>>>Project 2: Domino’s Pizza Delivery (personal project) <<<<<<<<

Given the demand at each pizza distribution center (determined from the stores they serve), Dominos needs to make sure it has enough flour delivered to its distribution centers to make the necessary dough. Dominos has signed a contract with Ardent Mills to deliver flour each week. There are 40 mills scattered throughout the US that Ardent can use to supply Dominos. To meet Dominos flour specifications, Ardent must retool each of its mills that will process flour for Dominos at a cost of $700K. Find the minimum cost solution for Ardent Mills to provide Dominos its flour.

Assume: Straight line distance (Haversine or Vincenty) from mill to distribution center is an adequate approximation of road distance between the two points. A truck can carry 880 50 pound sacks of flour in a single trip Each distribution center can only be serviced by a single mill You have to figure out how to convert dough to sack of flour – your professor will not provide you the conversion factor There are 3 ¼ cups of flour in each pizza dough The distribution information provided in “distributor_data.csv” is valid information concerning the distribution centers. The information for Ardent Mills locations provided in “ardent_mills_data.csv” is valid information for use in the problem The information in “average_daily_demand.csv” is valid information regarding the average store demand at each store and the correct “store to distribution center” alignment The $/mile factor in the distribution data center can be used for costing out distance between mills and centers

Files: Files: pizza distribution file

>>>> Prject 3: car manufactor and distrubtion<<<<
The COO and CFO have determined it is inefficient to ship cars manufactured in one plant to another plant in the selling country because the cars must then be moved from that plant to the dealerships.  It is also too costly to move all cars from a plant directly to the dealerships.  Instead they have determined they want 4 distribution centers in the US, 2 in MX, and 3 in CA.  Cars will be shipped from the manufacturing plants to the appropriate distribution centers, and then from distribution centers to the dealerships.  The annual amortized cost to build the distribution centers is $300,000 for each distribution center in the US; $250,000 in MX; and $350,000 in CA.  Find the least cost solution (integrate manufacturing, transportation, and annual building costs into the solution). 

Assume:
Straight line distance (Haversine or Vincenty) from plant to distribution center is an adequate approximation of road distance between the two points.
Dealership demand of automobiles styles is included in the “dealership_data.csv” file
Each dealership can only be serviced by a single distribution center
The $/mile factor, manufacturing costs, and plant manufacturing capacity for each country in homework 3 is still valid
There is no limit on the number of cars that can be stored in a distribution center
All the data you need are provided in the csv files that support this problem

Files: car manufactor and delivery



>>>>NFL scheduling <<<<

Scheduling Rules (those constraints which cannot be violated):
1)	Each game will be played exactly once during the season
2)	Each team must play once a week for each of the 17 weeks of the season (consider the BYE as a game)
3)	BYE games can only happen during weeks 4 through the week before Thanksgiving.  In 2015, Thanksgiving is week 12, therefore BYE games can only be played from week 4 through week 11)
4)	No team that had an early BYE week (week 4) the previous season will have an early BYE (week 4) in the present season
5)	Teams having an international game will have their BYE game the following week
6)	Teams playing an international game will be at home the week before the international game (unless they request otherwise – for this course assume no team makes that request)
7)	Two teams cannot play back to back games or play against each other the week before and the week after a BYE
8)	No team plays 4 away/home games consecutively during the season
9)	No team plays 3 consecutive home/away games during weeks 1,2,3,4,5 and 15,16,17
10)	Week 17 games will consist only of divisional games
11)	No team plays more than two road games against teams coming off their BYE
12)	New York Teams don’t want to play late home games on Yom Kippur and Rosh Hashanah
13)	There are two Monday night games on week 1
14)	There is only one Monday night game during weeks 2 through 16
15)	The home team for the late Monday night game on week 1 will be a team one of the following five teams (ARI, SD, SF, OAK, SEA)
16)	There is only one Thursday night game during weeks 1 through 16
17)	There is only one Sunday night game scheduled during weeks 1 through 16
18)	There will be two Saturday Night games, one each night in weeks 15 and 16 
(The Saturday rule depends on how many Saturdays there are in December and in which month week 17 falls.  Basically, if Thanksgiving is week 12, then there are Saturday Night games during weeks 15 and 16.  If Thanksgiving occurs in week 13, there are two Saturday games - one early and one late - that happen during week 16).
19)	Superbowl champion opens the season at home on Thursday night of week 1
20)	All teams playing road Thursday Night games are home the previous week
21)	There are two Thanksgiving Day games: DET hosts the early game and DAL hosts the late game.  (The networks alternate each year who gets the early game and who gets the late game)
22)	FOX and CBS each will get 8 doubleheaders from week 1 through 16; both networks have a double header on Week 17
23)	FOX and CBS cannot have more than two double headers in a row during weeks 1 through 16.
24)	Every team must play exactly one short week game during the season.  A short week is defined as a Sunday game in week “w” and a Thursday game in week “w+1”.  As a result, two of the six teams playing on Thanksgiving Day must play against each other the following Thursday night.
25)	No team playing on Monday night in week “w” can play Thursday during week “w+1” or Thursday “w+2”
26)	NYG and NYJ cannot play at home on the same day
27)	NYG and NYJ cannot play on the same network on Sunday afternoon
28)	OAK and SF cannot play on the same network on Sunday afternoon
29)	West Coast and Mountain Teams (SD, SF, LAR, OAK, SEA, ARI, DEN) cannot play at home during the Sunday early afternoon game (1:00 PM EST)
30)	CBS and FOX will have at least three 1PM Sunday afternoon games each week.
31)	Teams can play no more than 5 prime time games in a season (with no more than 4 of them being broadcast on NBC).  Thanksgiving Day games do not count as prime time games.  Only Thursday night, Saturday Night, Sunday Night, and Monday Night count as prime time games.

Firm Constraints (those constraints the NFL will violate only to get the best schedule):
32)	Teams cannot play at home on Stadium blackout dates.
33)	CBS and FOX afternoon games will be diverse.  This is a hard one to describe, but with the exception of week 17, they shouldn’t have all games from a single division.  There should be a good distribution of games with respect to quality (on a 1, 2, 3 scale).  There should be games from different time zones in a given week for each network (FOX, CBS)
34)	All teams must play at least 2 away/home games every 6 weeks (exclude BYE games from this constraint)
35)	All teams must play at least 4 away/home games every 10 weeks
36)	No team will play three consecutive away games between weeks 4 through 16 (if they do, they can only play one such set).  
37)	No team plays consecutive road games involving cross-country trips (coast to coast) unless team requests it (for the purpose of this course, assume no one requested consecutive cross-country trips)
38)	Two of the six teams that played Thanksgiving games must play Thursday the following week
39)	No team playing a Thursday night game should travel more than one time zone from home
40)	NYG and NYJ cannot play during the same time slot on Sunday.  This may be violated only if both teams are on the road.  The idea here is you do not want fans with tickets for one team sitting at home watching the game instead of being in the stadium.  
41)	OAK and SF cannot play during the same time slot on Sunday.  This may be violated only if both teams are on the road.  The idea here is you do not want fans with tickets for one team sitting at home watching the game instead of being in the stadium.
42)	CBS and FOX may have fewer than 5 games each on a Sunday exactly once per network.

Soft Constraints (those constraints the NFL will try to honor if they don’t break a good schedule):
43)	No team will open the season with two away games
44)	Florida teams should not play early home games in the month of September (this is generally a “by request” constraint).  Assume all Florida teams requested “no early games”.
Multiple Objectives (those conditions the NFL wishes to ensure are as good as possible):
45)	Maximize separation between each team’s Thursday game and their BYE game
46)	Minimize number of teams playing road game after road MNF game.
47)	Maximize the number of late-season division games.  Allow weeks 11 through 17 to be considered “late-season”.
48)	Minimize the number of times Pacific Time zone teams play at 1:00 PM in the Eastern Time Zone (attempt to share the burden equally between teams within a conference)
49)	Minimize the number of division series that end in the first half of the season.  
50)	Minimize the number of division series that are played less than three weeks apart
(Constraints 5 and 6 can be implemented by trying to keep to keep at least 8 weeks between games in a division series and recognizing that having 3 weeks between games is worse than having 6 weeks between games – i.e., the further apart you can keep a division series, the better off the schedule will be)
51)	Minimize the number of weeks in which CBS and FOX “lose” their key games or an entire division.  (This means try not to allow one entire division to be broadcast on prime time or stick FOX and CBS with a week or really bad games – Good games and bad games are subjectively assessed and scored on a scale of 1, 2, and 3).
52)	Minimize the disparity in network game quality across the season.  Admittedly, game quality is a subjective assessment.  This is based on the 1, 2, 3 scoring system.
 


Files: NFL schedule 6-10



