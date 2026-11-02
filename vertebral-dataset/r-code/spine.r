# Load library
library(tidyverse)
install.packages("skimr")
library(skimr)
install.packages("janitor")
library(janitor)
install.packages("naniar")
library(naniar)
install.packages("GGally")
library(GGally)
install.packages("corrplot")
library(corrplot)
install.packages("psych")
library(psych)
install.packages("patchwork")
library(patchwork)
install.packages("ggpubr")
library(ggpubr)
install.packages("rstatix")
library(rstatix)
# Load dataset
spine <- read.csv("../data/Dataset_spine.csv")

# # Dataset overview
glimpse(spine)

# Check classification
table(spine$Class_att, useNA = "ifany")

# Descriptive statistics
skim(spine)

# Distribution of target
ggplot(spine, aes(x = class_att, fill = class_att)) +
  geom_bar() +
  labs(
    title = "Distribution of Spinal Classification",
    x = "Classification",
    y = "Number of Observations"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
