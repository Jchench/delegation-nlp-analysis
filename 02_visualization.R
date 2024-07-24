library(tidyverse)
library(ggpattern)

# Read the data
delegation_data <- read_csv("script_2_output/script_2_count_dates.csv") |> 
  pivot_longer(cols = c(MandatoryDelegation, Permissive.Delegation), 
               names_to = "delegation_type", 
               values_to = "total_delegation")

# Create a complete sequence of years
all_years <- full_seq(delegation_data$year, 1)

# Calculate cumulative delegation with filled gaps
cum_delegation <- 
  delegation_data |> 
  group_by(delegation_type, year) |> 
  summarize(total_delegation = sum(total_delegation, na.rm = TRUE), .groups = 'drop') |> 
  complete(year = all_years, delegation_type, fill = list(total_delegation = 0)) |> 
  arrange(delegation_type, year) |> 
  group_by(delegation_type) |> 
  mutate(cumulative_delegation = cumsum(total_delegation)) |> 
  fill(cumulative_delegation, .direction = "down") |> 
  ungroup()

# Calculate cumulative constraints with filled gaps
cum_constraints <- 
  delegation_data |> 
  group_by(year) |> 
  summarize(total_constraints = sum(constraint, na.rm = TRUE), .groups = 'drop') |> 
  complete(year = all_years, fill = list(total_constraints = 0)) |> 
  arrange(year) |> 
  mutate(cumulative_constraints = cumsum(total_constraints)) |> 
  fill(cumulative_constraints, .direction = "down") |> 
  ungroup()

# Example of pseudo-log transformation
pseudo_log <- function(x) sign(x) * log10(abs(x) + 1)

# Plot with cumulative sums using geom_area and geom_ribbon for pattern
ggplot() +
  geom_area(data = cum_delegation,
            aes(x = year, y = pseudo_log(cumulative_delegation), fill = delegation_type)) +
  geom_ribbon_pattern(data = cum_constraints,
                      aes(x = year, ymin = 0, ymax = -pseudo_log(cumulative_constraints), 
                          fill = "Constraint"),
                      pattern = "stripe",
                      pattern_fill = "black",
                      pattern_angle = 45,
                      pattern_density = 0.1,
                      pattern_spacing = 0.02,
                      alpha = 0.6) +
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
