library(data.table)

setwd("C:/Users/wanh535/PycharmProjects/icom_abm/Results/Simulation 2")
####Distinguish flood zone and non-flood zone based on Jim's block group level depiction (90% quantile)
fz_bg <- fread("flood_zone_bg_v2.csv")
fz_bg <- fz_bg[, c("GEOID", "flood_zone")]
fz_bg$GEOID <- as.character(fz_bg$GEOID)
fz_bg <- fz_bg[!duplicated(fz_bg)]

data_list <- c()

list1 <- c("0", "0.01", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.9")

for(i in 1:length(list1)){
  file <- fread(paste0("results_utility_budget_reduction_", list1[i], ".csv"))
  file$coeff <- paste0("budget", list1[i])
  file$GEOID_bg <- substr(file$GEOID, 1, 12)
  file <- merge(file, fz_bg, by.x = "GEOID_bg", by.y = "GEOID", all.x = TRUE)
  name <- paste0("budget", list1[i])
  assign(name, file)
  data_list <- cbind(data_list, name)
}

list2 <- c("0", "0.25", "0.5", "0.75", "0.85", "0.95", "1.0")

for(i in 1:length(list2)){
  file <- fread(paste0("results_utility_simple_avoidance_utility_", list2[i], ".csv"))
  file$coeff <- paste0("avoidance", list2[i])
  file$GEOID_bg <- substr(file$GEOID, 1, 12)
  file <- merge(file, fz_bg, by.x = "GEOID_bg", by.y = "GEOID", all.x = TRUE)
  name <- paste0("avoidance", list2[i])
  assign(name, file)
  data_list <- cbind(data_list, name)
}

list3 <- c("0", "-1000", "-10000", "-100000", "-500000", "-1000000", "-10000000")

for(i in 1:length(list3)){
  file <- fread(paste0("results_utility_simple_flood_utility_", list3[i], ".csv"))
  file$coeff <- paste0("utility", list3[i])
  file$GEOID_bg <- substr(file$GEOID, 1, 12)
  file <- merge(file, fz_bg, by.x = "GEOID_bg", by.y = "GEOID", all.x = TRUE)
  name <- paste0("utility", list3[i])
  assign(name, file)
  data_list <- cbind(data_list, name)
}


model_year <- 19

data <- as.data.frame(matrix(0, model_year*length(data_list), 3))
colnames(data) <- c("Year", "Pop Per Change Flood Zone", "coeff")

for(i in 1:length(data_list)){
  dat <- get(data_list[i])
  dat <- dat[dat$flood_zone == "In Flood Zone", ]
  for(t in 1:model_year){
    sub <- dat[dat$model_year == t, ]
    data[t+(i-1)*model_year, 1] <- t
    data[t+(i-1)*model_year, 2] <- sum(sub$population - sub$pop1990) / sum(sub$pop1990)
    data[t+(i-1)*model_year, 3] <- unique(sub$coeff)
  }
}


library(ggplot2)
ggplot(data = data, aes(x = data$Year, y = data$`Pop Per Change Flood Zone`)) + geom_line(aes(colour = coeff))


data <- as.data.frame(matrix(0, model_year*length(data_list), 3))
colnames(data) <- c("Year", "Price change over flood zone", "coeff")

for(i in 1:length(data_list)){
  dat <- get(data_list[i])
  dat <- dat[dat$flood_zone == "In Flood Zone", ]
  for(t in 1:model_year){
    sub <- dat[dat$model_year == t, ]
    data[t+(i-1)*model_year, 1] <- t
    data[t+(i-1)*model_year, 2] <- sum(sub$new_price - sub$salesprice1993, na.rm = TRUE) / sum(sub$salesprice1993, na.rm = TRUE)
    data[t+(i-1)*model_year, 3] <- unique(sub$coeff)
  }
  
}

library(ggplot2)
ggplot(data = data, aes(x = data$Year, y = data$`Price change over flood zone`)) + geom_line(aes(colour = coeff))

