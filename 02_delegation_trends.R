library(tidyverse)

delegation_data <- 
  read_csv("script_2_output/script_2_count_dates.csv") |> 
  pivot_longer(cols = c(MandatoryDelegation, Permissive.Delegation), 
               names_to = "delegation_type", 
               values_to = "total_delegation")

delegation_avg <- delegation_data |> 
  group_by(year) |> 
  summarize(avg_delegation = mean(total_delegation))

delegation_data |>
  group_by(year) |> 
  ggplot(aes(x = year, y = total_delegation)) +
  geom_col(aes(fill = delegation_type), width = 1) +
  geom_point(data = delegation_avg, aes(x = year, y = avg_delegation), color = "black", size = 0.5) +
  geom_line(data = delegation_avg, aes(x = year, y = avg_delegation)) +
  labs(x = NULL,
       y = "Total Delegation",
       fill = "Delegation Type") +
  theme_minimal()
