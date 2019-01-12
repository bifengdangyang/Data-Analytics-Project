library(tidyverse)
library(lattice)
library(ggplot2)
library(viridis)

#install.packages('devtools')
# devtools::install_github('UrbanInstitute/urbnmapr')
install.packages('cowplot')
library('cowplot')
library(devtools)

library(urbnmapr)

mpdi <- read.csv("region.csv", header=TRUE, sep=",",
                 quote="\"", colClass=c("character", "numeric"))


mpdi.data <- left_join(mpdi, counties, by = "county_fips")


# Create quantiles
no_classes <- 4
labels <- c()
quantiles <- quantile(mpdi.data$value,
                      probs = seq(0, 1, length.out = no_classes + 1))


# Custom labels, rounding
labels <- c()
for(idx in 1:length(quantiles)){
  labels <- c(labels, paste0(round(quantiles[idx], 2),
                             " – ",
                             round(quantiles[idx + 1], 2)))
}
# Minus one label to remove the odd ending one
labels <- labels[1:length(labels)-1]

# Create new variable for fill
mpdi.data$mpdi.quantiles <- cut(mpdi.data$value,
                                breaks = quantiles,
                                labels = labels,
                                include.lowest = T)


outcome<-ggplot() +
  # County map
  geom_polygon(data = mpdi.data,color='white',
               mapping = aes(x = long, y = lat,
                             group = group,
                             fill = mpdi.data$mpdi.quantil)) +

  # Projection
  coord_map(projection = "polyconic")+

  # Fill color
  scale_fill_viridis(
    option = "viridis",
    name = "Virginia Counties Health Outcome Rank",
    discrete = T,
    direction = -1,
    end=0.9,
    guide = guide_legend(
      keyheight = unit(5, units = "mm"),
      title.position = 'top',
      reverse = F)
  )+
  # Theming
  theme_minimal(base_family = "Open Sans Condensed Light")+
  theme(
    legend.position = "bottom",
    legend.text.align = 0,
    plot.margin = unit(c(.5,.5,.2,.5), "cm")) +
  theme(
    axis.line = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
  )+
  theme(plot.title=element_text(family="Open Sans Condensed Bold", margin = ggplot2::margin(b=15)))+

  theme(plot.margin=unit(rep(0.5, 4), "cm"))+
  labs(x = "",
       y = "",
       title = "Virginia Counties Health Outcome Ranks 2018")







mpdi2 <- read.csv("economicfactor.csv", header=TRUE, sep=",",
                  quote="\"", colClass=c("character", "numeric"))


mpdi2.data <- left_join(mpdi2, counties, by = "county_fips")


# Create quantiles
no_classes <- 4
labels <- c()
quantiles <- quantile(mpdi2.data$value,
                      probs = seq(0, 1, length.out = no_classes + 1))


# Custom labels, rounding
labels <- c()
for(idx in 1:length(quantiles)){
  labels <- c(labels, paste0(round(quantiles[idx], 2),
                             " – ",
                             round(quantiles[idx + 1], 2)))
}
# Minus one label to remove the odd ending one
labels <- labels[1:length(labels)-1]

# Create new variable for fill
mpdi2.data$mpdi2.quantiles <- cut(mpdi2.data$value,
                                  breaks = quantiles,
                                  labels = labels,
                                  include.lowest = T)


EconomicFactor<- ggplot() +
  # County map
  geom_polygon(data = mpdi2.data,color='white',
               mapping = aes(x = long, y = lat,
                             group = group,
                             fill = mpdi2.data$mpdi2.quantil,color='white')) +


  # Projection
  coord_map(projection = "polyconic")+

  # Fill color
  scale_fill_viridis(
    option = "viridis",
    name = "Virginia Counties Economic Factor Rank",
    discrete = T,
    direction = -1,
    end=0.9,
    guide = guide_legend(
      keyheight = unit(5, units = "mm"),
      title.position = 'top',
      reverse = F)
  )+
  # Theming
  theme_minimal(base_family = "Open Sans Condensed Light")+
  theme(
    legend.position = "bottom",
    legend.text.align = 0,
    plot.margin = unit(c(.5,.5,.2,.5), "cm")) +
  theme(
    axis.line = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
  )+
  theme(plot.title=element_text(family="Open Sans Condensed Bold", margin = ggplot2::margin(b=15)))+

  theme(plot.margin=unit(rep(0.5, 4), "cm"))+
  labs(x = "",
       y = "",
       title = "Virginia Counties Economic Factor Ranks 2018")





mpdi3 <- read.csv("ClinicalCare.csv", header=TRUE, sep=",",
                  quote="\"", colClass=c("character", "numeric"))


mpdi3.data <- left_join(mpdi3, counties, by = "county_fips")


# Create quantiles
no_classes <- 4
labels <- c()
quantiles <- quantile(mpdi3.data$value,
                      probs = seq(0, 1, length.out = no_classes + 1))


# Custom labels, rounding
labels <- c()
for(idx in 1:length(quantiles)){
  labels <- c(labels, paste0(round(quantiles[idx], 2),
                             " – ",
                             round(quantiles[idx + 1], 2)))
}
# Minus one label to remove the odd ending one
labels <- labels[1:length(labels)-1]

# Create new variable for fill
mpdi3.data$mpdi3.quantiles <- cut(mpdi3.data$value,
                                  breaks = quantiles,
                                  labels = labels,
                                  include.lowest = T)


Clinicalcare<- ggplot() +
  # County map
  geom_polygon(data = mpdi3.data,color='white',
               mapping = aes(x = long, y = lat,
                             group = group,
                             fill = mpdi3.data$mpdi3.quantil,color='white')) +


  # Projection
  coord_map(projection = "polyconic")+

  # Fill color
  scale_fill_viridis(
    option = "viridis",
    name = "Virginia Counties Clinical Care Rank",
    discrete = T,
    direction = -1,
    end=0.9,
    guide = guide_legend(
      keyheight = unit(5, units = "mm"),
      title.position = 'top',
      reverse = F)
  )+
  # Theming
  theme_minimal(base_family = "Open Sans Condensed Light")+
  theme(
    legend.position = "bottom",
    legend.text.align = 0,
    plot.margin = unit(c(.5,.5,.2,.5), "cm")) +
  theme(
    axis.line = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
  )+
  theme(plot.title=element_text(family="Open Sans Condensed Bold", margin = ggplot2::margin(b=15)))+

  theme(plot.margin=unit(rep(0.5, 4), "cm"))+
  labs(x = "",
       y = "",
       title = "Virginia Counties Clinical Care Ranks 2018")





mpdi4 <- read.csv("HealthBehavior.csv", header=TRUE, sep=",",
                  quote="\"", colClass=c("character", "numeric"))


mpdi4.data <- left_join(mpdi4, counties, by = "county_fips")


# Create quantiles
no_classes <- 4
labels <- c()
quantiles <- quantile(mpdi4.data$value,
                      probs = seq(0, 1, length.out = no_classes + 1))


# Custom labels, rounding
labels <- c()
for(idx in 1:length(quantiles)){
  labels <- c(labels, paste0(round(quantiles[idx], 2),
                             " – ",
                             round(quantiles[idx + 1], 2)))
}
# Minus one label to remove the odd ending one
labels <- labels[1:length(labels)-1]

# Create new variable for fill
mpdi4.data$mpdi4.quantiles <- cut(mpdi4.data$value,
                                  breaks = quantiles,
                                  labels = labels,
                                  include.lowest = T)


HealthBehavior<- ggplot() +
  # County map
  geom_polygon(data = mpdi4.data,color='white',
               mapping = aes(x = long, y = lat,
                             group = group,
                             fill = mpdi4.data$mpdi4.quantil,color='white')) +


  # Projection
  coord_map(projection = "polyconic")+

  # Fill color
  scale_fill_viridis(
    option = "viridis",
    name = "Virginia Counties Health Behavior Rank",
    discrete = T,
    direction = -1,
    end=0.9,
    guide = guide_legend(
      keyheight = unit(5, units = "mm"),
      title.position = 'top',
      reverse = F)
  )+
  # Theming
  theme_minimal(base_family = "Open Sans Condensed Light")+
  theme(
    legend.position = "bottom",
    legend.text.align = 0,
    plot.margin = unit(c(.5,.5,.2,.5), "cm")) +
  theme(
    axis.line = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
  )+
  theme(plot.title=element_text(family="Open Sans Condensed Bold", margin = ggplot2::margin(b=15)))+

  theme(plot.margin=unit(rep(0.5, 4), "cm"))+
  labs(x = "",
       y = "",
       title = "Virginia Counties Health Behavior Ranks 2018")





mpdi5 <- read.csv("PhysicalEnviroment.csv", header=TRUE, sep=",",
                  quote="\"", colClass=c("character", "numeric"))


mpdi5.data <- left_join(mpdi5, counties, by = "county_fips")


# Create quantiles
no_classes <- 4
labels <- c()
quantiles <- quantile(mpdi5.data$value,
                      probs = seq(0, 1, length.out = no_classes + 1))


# Custom labels, rounding
labels <- c()
for(idx in 1:length(quantiles)){
  labels <- c(labels, paste0(round(quantiles[idx], 2),
                             " – ",
                             round(quantiles[idx + 1], 2)))
}
# Minus one label to remove the odd ending one
labels <- labels[1:length(labels)-1]

# Create new variable for fill
mpdi5.data$mpdi5.quantiles <- cut(mpdi5.data$value,
                                  breaks = quantiles,
                                  labels = labels,
                                  include.lowest = T)


PhysicalEnviroment<- ggplot() +
  # County map
  geom_polygon(data = mpdi5.data,color='white',
               mapping = aes(x = long, y = lat,
                             group = group,
                             fill = mpdi5.data$mpdi5.quantil,color='white')) +


  # Projection
  coord_map(projection = "polyconic")+

  # Fill color
  scale_fill_viridis(
    option = "viridis",
    name = "Virginia Counties Physical Enviroment Rank",
    discrete = T,
    direction = -1,
    end=0.9,
    guide = guide_legend(
      keyheight = unit(5, units = "mm"),
      title.position = 'top',
      reverse = F)
  )+
  # Theming
  theme_minimal(base_family = "Open Sans Condensed Light")+
  theme(
    legend.position = "bottom",
    legend.text.align = 0,
    plot.margin = unit(c(.5,.5,.2,.5), "cm")) +
  theme(
    axis.line = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
  )+
  theme(plot.title=element_text(family="Open Sans Condensed Bold", margin = ggplot2::margin(b=15)))+

  theme(plot.margin=unit(rep(0.5, 4), "cm"))+
  labs(x = "",
       y = "",
       title = "Virginia Counties Physical Enviroment Ranks 2018")

plot_grid(outcome, EconomicFactor, Clinicalcare,HealthBehavior,PhysicalEnviroment, nrow = 3)

plot_grid( EconomicFactor, Clinicalcare,HealthBehavior,PhysicalEnviroment, nrow = 2)
