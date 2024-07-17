library(tidyverse)

short <- read_csv("provisions_count_output/public_laws.csv")
long <- read_csv("provisions_count_output/DF-Rules-FR.csv")

final <- bind_rows(short, long)

write_csv(final, file = "provisions_count.csv")
