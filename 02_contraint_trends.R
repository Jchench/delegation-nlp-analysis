library(tidyverse)

constraint_data <- 
  read_csv("script_1_output/script_1_count.csv") |> 
  pivot_longer(cols = c(constraint, agency_constraint, entity_constraint), 
               names_to = "constraint_type", 
               values_to = "total_constraint")

constraint_data |> 
  ggplot(aes(x = year, y = total_constraint)) +
  geom_col(aes(fill = constraint_type))
