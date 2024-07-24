library(tidyverse)
library(ggpattern)

delegation_data <- 
  read_csv("script_2_output/script_2_count_dates.csv") |> 
  pivot_longer(cols = c(MandatoryDelegation, Permissive.Delegation), 
               names_to = "delegation_type", 
               values_to = "total_delegation")

# Example of pseudo-log transformation
pseudo_log <- function(x) sign(x) * log10(abs(x) + 1)

# Apply pseudo-log transformation to the necessary columns
delegation_data <- 
  delegation_data |> 
  mutate(total_delegation = pseudo_log(total_delegation),
         constraint = pseudo_log(constraint)) |> 
  filter(year >= 1990)

# Example with a simpler pattern
plot_texture <- 
  ggplot(delegation_data) +
  geom_col_pattern(
    aes(x = year, y = total_delegation, fill = delegation_type),
    pattern = "none"
  ) +
  geom_col_pattern(
    aes(x = year, y = -constraint, fill = "Constraint"),
    pattern = "stripe",
    pattern_fill = "black",
    pattern_angle = 45,
    pattern_density = 0.1,
    pattern_spacing = 0.02  
  ) +
  scale_fill_manual(
    values = c("MandatoryDelegation" = "black", 
               "Permissive.Delegation" = "gray40",
               "Constraint" = "gray60"),
    labels = c("MandatoryDelegation" = "Mandatory Delegation", 
               "Permissive.Delegation" = "Permissive Delegation",
               "Constraint" = "Constraint")
  ) +
  scale_y_continuous(labels = function(x) abs(x)) +
  theme_minimal() +
  labs(title = "Constraints and Delegations Over Time",
       x = NULL, y = "Total Constraint and Delegation (pseudo-log)", fill = "Type")

ggsave("constraints_and_delegations.jpg", plot = plot_texture, device = "jpeg", width = 10, height = 7, dpi = 300)


