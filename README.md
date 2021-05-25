>>>>Project 1: Knowledge Discovery for Crimes Against Children(Group Project) <<<<<<<

This group project seeks to discover knowledge about crimes against children through data mining of the National Incident-Based Reporting System (NIBRS) crime data source.  The main goal is to identify the characteristics of victims, offenders, and the situational threats in which children are especially vulnerable to categories of offenses. 
 My role in the team is to 
•	balance the unbalanced dataset
•	 visualize dataset’s multiple  perspectives using SHAP chart, simple dependence plot, Lime chart( Local interpretable model agnostic explanations) 
•	build several  machine learning models( penalized logistic regression, decision trees, random forest, Gradient Boosting)  to get insight from dataset.  I used Python and R for my work. 
Python API:  Pandas, NumPy, scikit-learn, Xgboost, matplotlib.
R  API:  dplyr,tidyr,DMwR,ggplot2,iml,data.table

Files:  capstone project

>>>>Project 2: Domino’s Pizza Delivery (personal project) <<<<<<<<

Given the demand at each pizza distribution center (determined from the stores they serve), Dominos needs to make sure it has enough flour delivered to its distribution centers to make the necessary dough. Dominos has signed a contract with Ardent Mills to deliver flour each week. There are 40 mills scattered throughout the US that Ardent can use to supply Dominos. To meet Dominos flour specifications, Ardent must retool each of its mills that will process flour for Dominos at a cost of $700K. Find the minimum cost solution for Ardent Mills to provide Dominos its flour.

Assume: Straight line distance (Haversine or Vincenty) from mill to distribution center is an adequate approximation of road distance between the two points. A truck can carry 880 50 pound sacks of flour in a single trip Each distribution center can only be serviced by a single mill You have to figure out how to convert dough to sack of flour – your professor will not provide you the conversion factor There are 3 ¼ cups of flour in each pizza dough The distribution information provided in “distributor_data.csv” is valid information concerning the distribution centers. The information for Ardent Mills locations provided in “ardent_mills_data.csv” is valid information for use in the problem The information in “average_daily_demand.csv” is valid information regarding the average store demand at each store and the correct “store to distribution center” alignment The $/mile factor in the distribution data center can be used for costing out distance between mills and centers

Files: Files: pizza distribution 


>>>>Project 3: car manufactor and distrubtion (personal project) <<<<
    The COO and CFO have determined it is inefficient to ship cars manufactured in one plant to another plant in the selling country because the cars must then be moved from that plant to the dealerships.  It is also too costly to move all cars from a plant directly to the dealerships.  Instead they have determined they want 4 distribution centers in the US, 2 in MX, and 3 in CA.  Cars will be shipped from the manufacturing plants to the appropriate distribution centers, and then from distribution centers to the dealerships.  The annual amortized cost to build the distribution centers is $300,000 for each distribution center in the US; $250,000 in MX; and $350,000 in CA.  Find the least cost solution (integrate manufacturing, transportation, and annual building costs into the solution). 

Assume:
Straight line distance (Haversine or Vincenty) from plant to distribution center is an adequate approximation of road distance between the two points.
Dealership demand of automobiles styles is included in the “dealership_data.csv” file
Each dealership can only be serviced by a single distribution center
The $/mile factor, manufacturing costs, and plant manufacturing capacity for each country in homework 3 is still valid
There is no limit on the number of cars that can be stored in a distribution center
All the data you need are provided in the csv files that support this problem

Files: car manufactor and delivery



>>>>Project 4: NFL scheduling (personal project) <<<<

schedule NFL games based on constraints rules

Files: NFL schedule 6,7,8,9,10



