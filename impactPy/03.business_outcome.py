

"""
Business Outcome Calculation: Gender, Age Group, and Income Segmentation

- Load and merge elasticity scenario data with spending data by market and group (gender, age, income).
- Calculate business outcomes by estimating total spending (median and average) for new customers in local and USD currencies.
- Perform calculations for gender, age group, and income level.
- Save the calculated business outcomes for each segment to separate Excel files.
"""



import pandas as pd

# Function to calculate business outcomes
def calculate_business_outcomes(scenarios_df, spending_df, group_column):
    
    # Perform a left join on 'market' and the group column (gender or age_group)
    merged_df = pd.merge(scenarios_df,
                        spending_df[['market', group_column, 
                                   'median_spent_local', 'median_spent_$',
                                   'avg_spent_local', 'avg_spent_$']],
                        on=['market', group_column],
                        how='left')
    
    # Calculate economic outcomes
    merged_df['economic_outcome_median_local'] = merged_df['new_customers'] * merged_df['median_spent_local']
    merged_df['economic_outcome_median_$'] = merged_df['new_customers'] * merged_df['median_spent_$']
    merged_df['economic_outcome_avg_local'] = merged_df['new_customers'] * merged_df['avg_spent_local']
    merged_df['economic_outcome_avg_$'] = merged_df['new_customers'] * merged_df['avg_spent_$']
    
    # Select relevant columns for business outcome
    business_outcome = merged_df[['scenario_id', 'price', group_column, 'new_customers', 
                                'economic_outcome_median_local', 'economic_outcome_median_$',
                                'economic_outcome_avg_local', 'economic_outcome_avg_$']]
    
    return business_outcome


# 1. Load data for gender analysis
output_scenarios_gender_path = 'data/outputs/elasticity_scenarios_gender.xlsx'
spending_summarised_gender_path = 'data/outputs/spending_summarised_gender.xlsx'

output_scenarios_gender_df = pd.read_excel(output_scenarios_gender_path)
spending_summarised_gender_df = pd.read_excel(spending_summarised_gender_path)

# Calculate business outcomes for gender
business_outcome_gender = calculate_business_outcomes(
    output_scenarios_gender_df, 
    spending_summarised_gender_df,
    'gender'
)

# Save gender business outcomes
gender_output_path = 'data/outputs/business_outcome_gender.xlsx'
business_outcome_gender.to_excel(gender_output_path, index=False)

# 2. Load data for age analysis
output_scenarios_age_path = 'data/outputs/elasticity_scenarios_age_group.xlsx'
spending_summarised_age_path = 'data/outputs/spending_summarised_age_group.xlsx'

output_scenarios_age_df = pd.read_excel(output_scenarios_age_path)
spending_summarised_age_df = pd.read_excel(spending_summarised_age_path)

# Calculate business outcomes for age groups
business_outcome_age = calculate_business_outcomes(
    output_scenarios_age_df, 
    spending_summarised_age_df,
    'age_group'
)

# Save age business outcomes
age_output_path = 'data/outputs/business_outcome_age.xlsx'
business_outcome_age.to_excel(age_output_path, index=False)

# 3. Load data for income analysis
output_scenarios_income_path = 'data/outputs/elasticity_scenarios_income.xlsx'
spending_summarised_income_path = 'data/outputs/spending_summarised_income.xlsx'

output_scenarios_income_df = pd.read_excel(output_scenarios_income_path)
spending_summarised_income_df = pd.read_excel(spending_summarised_income_path)

# Calculate business outcomes for income groups
business_outcome_income = calculate_business_outcomes(
    output_scenarios_income_df, 
    spending_summarised_income_df,
    'income_level'
)

# Save income business outcomes
income_output_path = 'data/outputs/business_outcome_income.xlsx'
business_outcome_income.to_excel(income_output_path, index=False)