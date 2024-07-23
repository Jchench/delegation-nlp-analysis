library(tidyverse)

constraint_data <- 
  read_csv("script_1_output/script_1_count.csv") |> 
  pivot_longer(cols = c(constraint, agency_constraint, entity_constraint), 
               names_to = "constraint_type", 
               values_to = "total_constraint")

constraint_avg <- constraint_data |> 
  group_by(year) |> 
  summarize(avg_constraint = mean(total_constraint))

constraint_data |> 
  ggplot(aes(x = year, y = total_constraint)) +
  geom_col(aes(fill = constraint_type), width = 1) +
  geom_point(data = constraint_avg, aes(x = year, y = avg_constraint), color = "black", size = 0.5) +
  geom_line(data = constraint_avg, aes(x = year, y = avg_constraint)) +
  labs(x = NULL,
       y = "Total Constraint",
       fill = "Constraint type") +
  theme_minimal()
