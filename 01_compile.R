library(tidyverse)

short <- read_csv("script_2_output/all_provisions_1.csv")
long <- read_csv("script_2_output/all_provisions_2.csv")
cares <- read_csv("script_2_output/all_provisions_3.csv")

final <- bind_rows(short, long, cares)

write_csv(final, file = "script_2_output/script_2_count.csv")
