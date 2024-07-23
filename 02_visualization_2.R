library(tidyverse)
library(ggpattern)

# Read the data
delegation_data <- read_csv("script_2_output/script_2_count_dates.csv") |> 
  pivot_longer(cols = c(MandatoryDelegation, Permissive.Delegation), 
               names_to = "delegation_type", 
               values_to = "total_delegation")

cum_delegation <- 
  delegation_data |> 
  group_by(citation, year, delegation_type) |> 
  summarize(total_delegation = sum(total_delegation))

cum_constraints <- 
  delegation_data |> 
  group_by(citation, year) |> 
  summarize(total_constraints = sum(constraint))

# Example of pseudo-log transformation
pseudo_log <- function(x) sign(x) * log10(abs(x) + 1)

# Plot with cumulative sums
ggplot() +
  geom_col_pattern(data = cum_delegation,
    aes(x = year, y = pseudo_log(total_delegation), fill = delegation_type),
    pattern = "none") +
  geom_col_pattern(data = cum_constraints,
    aes(x = year, y = -pseudo_log(total_constraints), fill = "Constraint"),
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
  labs(title = "Cumulative Constraints and Delegations Over Time",
       x = NULL, y = "Cumulative Constraint and Delegation (pseudo-log)", fill = "Type")

# Save the plot
# ggsave("cumulative_constraints_and_delegations4.jpg", plot = plot_texture, device = "jpeg", width = 10, height = 7, dpi = 300)
