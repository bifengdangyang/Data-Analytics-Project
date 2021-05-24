
setwd("C:/Users/xianci/Desktop/GMU/DAEN690/topic")
library(data.table)
library(dplyr)
library(tidyr)
library(DMwR)
library(sjPlot)
library(ggplot2)
mydata = read.csv("KDCACdata_16Jun2019.csv",header=TRUE)
# for model
#str(mydata[,c(2:59)])
modeldata<-mydata[,c(2:59)]
# for reference
#str(mydata[,c(60:82)])
# identiy numeric variables to do correlation ， change some columns data
structure
numcol<-c('V4018.AGE.OF.VICTIM','V5007.AGE.OF.OFFENDER','V1008.TOTAL.OFFENSE
          .SEGMENTS','V1009.TOTAL.VICTIM.SEGMENTS','V1010.TOTAL.OFFENDER.SEGMENTS','AG
          ENCY.POPULATION.TOTAL')
modeldata[numcol] <- sapply(modeldata[numcol],as.numeric)
categdata<-modeldata[ , !(names(modeldata) %in% numcol)]
categcol<-colnames(categdata)
modeldata[categcol] <- sapply(modeldata[categcol],as.factor)
modeldata <-modeldata %>% mutate_if(is.character,as.factor)
#str(modeldata)
dmy <- dummyVars(" ~ LOCATION.CATEGORY", data = modeldata)
newmodeldata <- data.frame(predict(dmy, newdata = modeldata))
str(newmodeldata)
#write.csv(modeldata, file = "modeldata.csv")
### model building
##0 divide to training and validation ; balance data use SMOTE
#########################################
exclude<-c('TARGET.Assault','TARGET.Homicide_Nonnegligent','TARGET.Negligent
           _Manslaughter','TARGET.Kidnaping_Abduction','TARGET.Human_Trafficking',
           'V2011.LOCATION.TYPE','BH011.COUNTRY.REGION')
binadata<-modeldata[ , !(names(modeldata) %in% exclude)]
str(binadata)
row<-nrow(modeldata)
trainindex <- sample(row, 0.6*row, replace=FALSE)
training <- binadata[trainindex,]
validation = binadata[-trainindex,]
str(training)
table(training$TARGET.Sex_Offense)
prop.table(table(training$TARGET.Sex_Offense))
# another method to balance data ,but not good as SMOTE, but run fast
library(ROSE)
rosedata <- ROSE(TARGET.Sex_Offense ~ ., data = training,seed = 1)$data
table(rosedata$TARGET.Sex_Offense)
# use SMOTE to fix unbalanced problem
library(DMwR)
set.seed(1)
btraining <- SMOTE(TARGET.Sex_Offense~., k=10,training,perc.over = 100 )
prop.table(table(btraining$TARGET.Sex_Offense))
write.csv(btraining, file = "btraining.csv")
# because it takes long time to run smote, so I save the balanced data to
file
btraining<- read.csv("btraining.csv",header=TRUE)
head(btraining)
prop.table(table(btraining$TARGET.Sex_Offense))
# weird thing is the data structure change for some columns after I read it in from csv
str(btraining)
# so I match the data structure with previous right data form
common <- names(btraining)[names(btraining) %in% names(training)]
btraining[common] <- lapply(common, function(x) {
  match.fun(paste0("as.", class(training[[x]])))(btraining[[x]])
})
btraining<-btraining[,-1]
str(btraining)
str(training)

## 1 binary decision tree model #########################################
library(rpart)
set.seed(12345)
modfit.rpart <- rpart(TARGET.Sex_Offense ~ ., data=btraining,
                      method="class")
print(modfit.rpart, digits = 3)
library(rpart.utils)
library(rpart.plot)
rpart.rules(modfit.rpart)
rpart.plot(modfit.rpart, type = 2, clip.right.labs = FALSE, branch = .5,
           under = TRUE)
plot(modfit.rpart)
text(modfit.rpart)
library(rpart.plot)
prp(modfit.rpart,varlen=50)
summary(btraining$LOCATION.CATEGORY)
# Predict validation with the trained model
predictions1 <- predict(modfit.rpart, validation, type = "class")
predictions_prop <- predict(modfit.rpart, validation, type = "prob")
# Accuracy and other metrics
library(caret)
confusionMatrix(predictions1, validation$TARGET.Sex_Offense)
# ROC curve
library(ROCR)
cart_scores <- prediction(predictions_prop[,2],
                          validation$TARGET.Sex_Offense)
cart_perf <- performance(cart_scores, "tpr", "fpr")
plot(cart_perf,
     main="CART ROC Curves",
     xlab="1 - Specificity: False Positive Rate",
     ylab="Sensitivity: True Positive Rate",
     col="darkblue", lwd = 3)
abline(0,1, lty = 300, col = "green", lwd = 3)
grid(col="aquamarine")
# AREA UNDER THE CURVE

rf_auc <- performance(cart_scores, "auc")
as.numeric(rf_auc@y.values)
# Getting Lift Charts
rf_lift <- performance(cart_scores, measure="lift", x.measure="rpp")
plot(rf_lift,
     main="CART Lift Chart",
     xlab="% Populations (Percentile)",
     ylab="Lift",
     col="darkblue", lwd = 3)
abline(1,0,col="red", lwd = 3)
grid(col="aquamarine")
## 2 binary random forest #########################################
library(randomForest)
library(e1071)
# Algorithm Tune (tuneRF)
trainingnet <- na.omit(btraining)
validationnet<-na.omit(validation)
x <- trainingnet[,-1]
y <- trainingnet[,1]
set.seed(7)
bestmtry <- tuneRF(x, y, stepFactor=1.5, improve=1e-5, ntree=500)
print(bestmtry)
#bestmty is 15 which has lowest test error estimate
set.seed(12345)
rf = randomForest(TARGET.Sex_Offense~., btraining, mtry=15,
                  importance=TRUE,na.action=na.exclude)
plot(rf)
importance(rf)
varImpPlot(rf,sort = T,
           main="Variable Importance")
predicted.response <- predict(rf, validation)
library(caret)
confusionMatrix(data=predicted.response,

                reference=validation$TARGET.Sex_Offense)
# Plot the performance of the model applied to the evaluation set as an ROC
curve.
library(ROCR)
pred_prob <- predict(rf,validation, type = 'prob')
rf_scores <- prediction(pred_prob[,2], validation$TARGET.Sex_Offense)
rf_perf <- performance(rf_scores, "tpr", "fpr")
plot(rf_perf,
     main="Random Forest ROC Curves",
     xlab="1 - Specificity: False Positive Rate",
     ylab="Sensitivity: True Positive Rate",
     col="darkblue", lwd = 3)
abline(0,1, lty = 300, col = "green", lwd = 3)
grid(col="aquamarine")
# AREA UNDER THE CURVE
rf_auc <- performance(rf_scores, "auc")
as.numeric(rf_auc@y.values)
# Getting Lift Charts
rf_lift <- performance(rf_scores, measure="lift", x.measure="rpp")
plot(rf_lift,
     main="Random Forest Lift Chart",
     xlab="% Populations (Percentile)",
     ylab="Lift",
     col="darkblue", lwd = 3)
abline(1,0,col="red", lwd = 3)
grid(col="aquamarine")
# exploration partial dependence plot
par.age <- partial(rf, pred.var = c("V4018.AGE.OF.VICTIM"), chull = TRUE)
plot.age <- autoplot(par.age, contour = TRUE,legend.title =
                       "Partial\ndependence")
par.race <- partial(rf, pred.var = c('V4020.RACE.OF.VICTIM'), chull = TRUE)


plot.race <- autoplot(par.race, contour = TRUE,legend.title =
                        "Partial\ndependence")
par.ageage<- partial(rf, pred.var = c("V4018.AGE.OF.VICTIM",
                                      "V5007.AGE.OF.OFFENDER"), chull = TRUE)
plot.ageage <- autoplot(par.ageage, contour = TRUE, legend.title =
                          "Partial\ndependence")
## 3 basic binary logistc regression
#########################################
library(caret)
remove_cols <- nearZeroVar(training, names = TRUE,
                           freqCut = 19, uniqueCut = 10, saveMetrics = TRUE)
#which ones are the zero variance predictors
out1<-remove_cols[remove_cols[,"zeroVar"] > 0, ]
out1var<-rownames(out1)
#which ones are the near-zero variance predictors
out2<-remove_cols[remove_cols[,"zeroVar"] + remove_cols[,"nzv"] > 0, ]
out2var<-rownames(out2)
out<-c('V1009.TOTAL.VICTIM.SEGMENTS')
out2<-c("CIRCUMSTANCES.ARGUMENT","CIRCUMSTANCES.DRUG.DEALING","CIRCUMSTANCES
        .GANG","CIRCUMSTANCES.LOVER.QUARREL","CIRCUMSTANCES.OTHER.FELONY","CIRCUMSTA
        NCES.OTHER.CIRC","CIRCUMSTANCES.NEGLIGENT.WEAPON",
        "CIRCUMSTANCES.NEGLIGENT.OTHER.KILLING")
out3<-c( "COLLEGE.UNIVERSITY")
#drop<-c(out1var,out2var,out)
drop<-c(out,out2,out3)
logtraining<-btraining[, !(names(btraining) %in% drop)]
logvalidation<-validation[, !(names(validation) %in% drop)]
str(logtraining)
table(logtraining$TARGET.Sex_Offense)
prop.table(table(logtraining$TARGET.Sex_Offense))

glmtry<-glm(TARGET.Sex_Offense ~ ., data=logtraining, family=binomial)
summary(glmtry)
# Predict probablities from logisitic regression on validation sets
glmtry$xlevels[["BH009.POPULATION.GROUP"]] <-
  union(glmtry$xlevels[["BH009.POPULATION.GROUP"]],
        levels(validationlog$BH009.POPULATION.GROUP))
glmtry.probs<-predict(glmtry, logvalidation, type ="response")
d<-table(logvalidation$TARGET.Sex_Offense, glmtry.probs>0.5 )
# accuracy rate
sum(diag(d))/sum(d)
library(ROCR)
glmpred <- prediction(glmtry.probs, logvalidation$TARGET.Sex_Offense)
glmperf <- performance(glmpred, 'tpr','fpr')
plot(glmperf,
     main="Log ROC Curves",
     xlab="1 - Specificity: False Positive Rate",
     ylab="Sensitivity: True Positive Rate",
     col="darkblue", lwd = 3)
abline(0,1, lty = 300, col = "green", lwd = 3)
grid(col="aquamarine")
# AREA UNDER THE CURVE
glm_auc <- performance(glmpred, "auc")
as.numeric(glm_auc@y.values)
library(caret)
varImp(glmtry)
imp <- as.data.frame(varImp(glmtry))
imp <- data.frame(overall = imp$Overall,
                  names = rownames(imp))
imp[order(imp$overall,decreasing = T),]
## 4 penalized logistic regression #########################################
trainingnet <- na.omit(btraining)
validationnet<-na.omit(validation)

library(glmnet)
#x <- as.matrix(trainingnet[,-1])
x <- model.matrix( ~ ., trainingnet[,-1])
y <- trainingnet$TARGET.Sex_Offense
head(x)
# Find the best lambda using cross-validation
set.seed(123)
cv.lasso <- cv.glmnet(x, y, alpha = 1, family = "binomial")
plot(cv.lasso)
# Fit the final model on the training data
model <- glmnet(x, y, alpha = 1, family = "binomial",
                lambda = cv.lasso$lambda.min)
# Display regression coefficients
coef(model)
# Make predictions on the test data
x.test <- model.matrix( ~., validationnet)[,-1]
probabilities <- model %>% predict(newx = x.test)
predicted.classes <- ifelse(probabilities > 0.5, "1", "0")
# Model accuracy
observed.classes <- validationnet$TARGET.Sex_Offense
mean(predicted.classes == observed.classes)
library(ROCR)
glmpred <- prediction(probabilities, validationnet$TARGET.Sex_Offense)
glmperf <- performance(glmpred, 'tpr','fpr')
plot(glmperf,
     main="penalized logistic regression ROC Curves",
     xlab="1 - Specificity: False Positive Rate",
     ylab="Sensitivity: True Positive Rate",
     col="darkblue", lwd = 3)
abline(0,1, lty = 300, col = "green", lwd = 3)
grid(col="aquamarine")
# AREA UNDER THE CURVE
glm_auc <- performance(glmpred, "auc")
as.numeric(glm_auc@y.values)
library(caret)
varImp(model)
imp <- as.data.frame(varImp(model))

imp <- data.frame(overall = imp$Overall,
                  names = rownames(imp))
imp[order(imp$overall,decreasing = T),]
## 5 XGBoost - Gradient Boosting #########################################
#using one hot encoding
trainingnet <- na.omit(btraining)
validationnet<-na.omit(validation)
labels <- trainingnet$TARGET.Sex_Offense
ts_label <- validationnet$TARGET.Sex_Offense
new_tr <- model.matrix(~.,data = trainingnet[,-1])
new_ts <- model.matrix(~.,data = validationnet[,-1])
#convert factor to numeric
labels <- as.numeric(labels)-1
ts_label <- as.numeric(ts_label)-1
#preparing matrix
dtrain <- xgb.DMatrix(data = new_tr,label = labels)
dtest <- xgb.DMatrix(data = new_ts,label=ts_label)
## Tuning over hyperparameters ############
gbmHyper <- expand.grid(
  eta = c(.05),
  max_depth = c(1,2,3,4,5,6),
  min_child_weight = c(5,7,10,15),
  subsample = c(1),
  colsample_bytree = c(.7),
  alpha = 0,
  lambda = 0,
  gamma = 0
)


nrow(gbmHyper)
for(i in 1:nrow(gbmHyper)) {
  gbmParamsshort <- list(eta = gbmHyper$eta[i],
                         max_depth = gbmHyper$max_depth[i],
                         min_child_weight = gbmHyper$min_child_weight[i],
                         subsample = gbmHyper$subsample[i],
                         colsample_bytree = gbmHyper$subsample[i],
                         objective = "binary:logistic",
                         booster = "gbtree",
                         eval_metric = "auc",
                         nrounds = 3000,
                         nthread = 4,
                         alpha = 0,
                         lambda = 0,
                         gamma = 0
  )
  set.seed(101)
  xgb <- xgb.train(gbmParamsshort, dtrain, gbmParamsshort$nrounds, list(val
                                                                        = dtest), print_every_n = 50, early_stopping_rounds = 300)
  gbmHyper$best[i] <- xgb$best_score
}
# Best results were 5 max depth and 5 min child weight
xgb
### 6 unsupervised learning: cluster
#########################################
library(klaR)
cluster_data<- filter(modeldata[,-c(1,2,3,4,6,58)], TARGET.Human_Trafficking
                      == 1)
str(cluster_data)


names <-
  c('V4018.AGE.OF.VICTIM','V1008.TOTAL.OFFENSE.SEGMENTS','V1009.TOTAL.VICTIM.S
    EGMENTS','V1010.TOTAL.OFFENDER.SEGMENTS')
cluster_data[,names] <- lapply(cluster_data[,names] , factor)
#cluster_data <-cluster_data %>% mutate_if(is.numeric,as.factor)
cluster_data <- cluster_data[, sapply(cluster_data, is.factor)]
cluster.results <-kmodes(cluster_data, 3, iter.max = 10, weighted = FALSE )
cluster.output <- cbind(cluster_data,cluster.results$cluster)
write.csv(cluster.output, file = "kmodes clusters.csv", row.names = TRUE)
### cluster method 2
library(cluster)
cluster_data<- filter(modeldata[,-c(1,2,3,4,6)], TARGET.Human_Trafficking ==
                        1)
str(cluster_data)
gower_dist <- daisy(cluster_data,
                    metric = "gower",
                    type = list(logratio = 3))
summary(gower_dist)
gower_mat <- as.matrix(gower_dist)
# Output most similar pair
cluster_data[
  which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]),
        arr.ind = TRUE)[1, ], ]
# Output most dissimilar pair
cluster_data[
  which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),
        arr.ind = TRUE)[1, ], ]
# Calculate silhouette width for many k using PAM
sil_width <- c(NA)
for(i in 2:10){

  pam_fit <- pam(gower_dist,
                 diss = TRUE,
                 k = i)
  sil_width[i] <- pam_fit$silinfo$avg.width
}
# Plot sihouette width (higher is better)
plot(1:10, sil_width,
     xlab = "Number of clusters",
     ylab = "Silhouette Width")
lines(1:10, sil_width)
pam_fit <- pam(gower_dist, diss = TRUE, k = 8)
pam_results <- cluster_data %>%
  mutate(cluster = pam_fit$clustering) %>%
  group_by(cluster) %>%
  do(the_summary = summary(.))
pam_results$the_summary
pam_results$the_summary[1]
library(Rtsne)
tsne_obj <- Rtsne(gower_dist, is_distance = TRUE)
tsne_data <- tsne_obj$Y %>%
  data.frame() %>%
  setNames(c("X", "Y")) %>%
  mutate(cluster = factor(pam_fit$clustering),
         name = cluster_data$name)
clusterplot<-ggplot(aes(x = X, y = Y), data = tsne_data) +
  geom_point(aes(color = cluster))
clusterplot+ scale_color_manual(values=c("#999999", "#E69F00",
                                         "#56B4E9","red", "blue", "green",'purple',"black"))
