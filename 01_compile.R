library(tidyverse)

short <- read_csv("script_1_output/public_laws_1.csv")
long <- read_csv("script_1_output/public_laws_2.csv")
missing <- read_csv("script_1_output/public_laws_3.csv")

final <- bind_rows(short, long, missing)

write_csv(final, file = "script_1_count.csv")
