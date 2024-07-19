library(tidyverse)

delegation_data <- 
  read_csv("script_2_output/script_2_count_dates.csv") |> 
  pivot_longer(cols = c(MandatoryDelegation, Permissive.Delegation), 
               names_to = "delegation_type", 
               values_to = "total_delegation")

delegation_data |>
  ggplot(aes(x = year, y = total_delegation)) +
  geom_col(aes(fill = delegation_type))