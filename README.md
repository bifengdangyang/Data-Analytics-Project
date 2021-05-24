Project 1: Knowledge Discovery for Crimes Against Children(Group Project) 

This group project seeks to discover knowledge about crimes against children through data mining of the National Incident-Based Reporting System (NIBRS) crime data source.  The main goal is to identify the characteristics of victims, offenders, and the situational threats in which children are especially vulnerable to categories of offenses. 
 My role in the team is to 
•	balance the unbalanced dataset
•	 visualize dataset’s multiple  perspectives using SHAP chart, simple dependence plot, Lime chart( Local interpretable model agnostic explanations) 
•	build several  machine learning models( penalized logistic regression, decision trees, random forest, Gradient Boosting)  to get insight from dataset.  I used Python and R for my work. 
Python API:  Pandas, NumPy, scikit-learn, Xgboost, matplotlib.
R  API:  dplyr,tidyr,DMwR,ggplot2,iml,data.table


1  FINAL KD-CAC Project Presentation.pptx  
2 ProjectCode.R 

Project 2: Domino’s Pizza Delivery
Given the demand at each pizza distribution center (determined from the stores they serve), Dominos needs to make sure it has enough flour delivered to its distribution centers to make the necessary dough. Dominos has signed a contract with Ardent Mills to deliver flour each week. There are 40 mills scattered throughout the US that Ardent can use to supply Dominos. To meet Dominos flour specifications, Ardent must retool each of its mills that will process flour for Dominos at a cost of $700K. Find the minimum cost solution for Ardent Mills to provide Dominos its flour.

Assume: Straight line distance (Haversine or Vincenty) from mill to distribution center is an adequate approximation of road distance between the two points. A truck can carry 880 50 pound sacks of flour in a single trip Each distribution center can only be serviced by a single mill You have to figure out how to convert dough to sack of flour – your professor will not provide you the conversion factor There are 3 ¼ cups of flour in each pizza dough The distribution information provided in “distributor_data.csv” is valid information concerning the distribution centers. The information for Ardent Mills locations provided in “ardent_mills_data.csv” is valid information for use in the problem The information in “average_daily_demand.csv” is valid information regarding the average store demand at each store and the correct “store to distribution center” alignment The $/mile factor in the distribution data center can be used for costing out distance between mills and centers










