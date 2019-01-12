library(tidyverse)
library(lattice)
library(ggplot2)



health<-read_csv('combine.csv')


healthdata<-health[,3:8]



pairs(~HealthyRank+Healthybehavior+Clinicalcare+Economicalfactor+Physicalenviroment,data=healthdata,font.labels =2,label.pos = 0.5 )


row<-nrow(healthdata)
trainingSize<- ceiling(row/2)

set.seed(3)
trainindex<-sample(row,trainingSize)
train<-healthdata[trainindex,]
test<-healthdata[-trainindex,]


trainfit<-lm(HealthyRank ~ Healthybehavior + Clinicalcare + Economicalfactor + Physicalenviroment , data=train)

summary(trainfit)

testfit<-lm(HealthyRank ~ Healthybehavior + Clinicalcare + Economicalfactor + Physicalenviroment , data=test)

summary(testfit)

residual<-residuals(trainfit)
hist(residual,breaks=20)

residual<-residuals(trainfit)
layout(matrix(c(1,2,3,4),2,2))
plot(trainfit)

null<-lm(HealthyRank~1, data=train)
summary(null)

forward<-step(null, scope=list(upper=trainfit), direction='forward')
coefficients(forward)

backward<-step(trainfit, direction='backward')
coefficients(backward)


PredBase<-predict(trainfit, test, se.fit=TRUE)
PredBase$residual.scale


PredForward<-predict(forward, test, se.fit=TRUE)
PredForward$residual.scale

trainfit2<-lm(HealthyRank ~  Clinicalcare + Economicalfactor+Clinicalcare :Economicalfactor , data=train)

summary(trainfit2)

Predconnect<-predict(trainfit2, test, se.fit=TRUE)
Predconnect$residual.scale

