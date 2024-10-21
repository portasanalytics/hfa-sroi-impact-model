 
"""
This script calculates the social outcome of investment. 
The social outcome refers to the change in social levels when a non-customer becomes a customer. 
It is measured using two survey questions related to life satisfaction (S6) and community trust (S7).
"""


import pandas as pd

# Load data
df = pd.read_excel('data/survey_data/Elasticity_Questionnaire_v3.xlsx', sheet_name='Data')

# Mapping for gender
gender_mapping = {
    1: "Male",
    2: "Female",
}
df['gender'] = df['S4'].map(gender_mapping)

# Mapping for markets
market_mapping = {
    1: "Australia", 2: "Canada", 3: "Germany", 4: "Ireland", 5: "Japan",
    6: "KSA (Saudi Arabia)", 7: "New Zealand", 8: "Singapore", 9: "Spain",
    10: "USA (United States of America)"
}
df['market'] = df['S1'].map(market_mapping)

# Mapping for age groups
age_mapping = {
    2: "Young Adults (16-35)",
    3: "Young Adults (16-35)",
    4: "Old Adults (>35)",
    5: "Old Adults (>35)",
    6: "Old Adults (>35)",
    7: "Old Adults (>35)"
}
df['age_group'] = df['dS3_RECODE'].map(age_mapping)

# Filter for Male and Female only
df_filtered = df[df['S4'].isin([1, 2])]

# ---- Gender-wise Summary ----
gender_summary = df_filtered.groupby(['market', 'gender']).apply(
    lambda x: pd.Series({
        'S6_customer': (x[x['dSEGMENT'] == 1]['S6'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S6_non_customer': (x[x['dSEGMENT'] == 2]['S6'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
        'S7_customer': (x[x['dSEGMENT'] == 1]['S7'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S7_non_customer': (x[x['dSEGMENT'] == 2]['S7'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
    })
).reset_index()

# Calculate change in social outcomes for gender
gender_summary['life_satisfaction_change'] = (gender_summary['S6_customer'] - gender_summary['S6_non_customer'])/gender_summary['S6_customer']
gender_summary['community_trust_change'] = (gender_summary['S7_customer'] - gender_summary['S7_non_customer'])/gender_summary['S7_customer']
gender_summary['social_change'] = (gender_summary['life_satisfaction_change'] + gender_summary['community_trust_change']) / 2

# Save gender-wise results
gender_output_file_path = 'data/outputs/social_change_gender.xlsx'
gender_summary.to_excel(gender_output_file_path, index=False)
print(f"Gender-based social outcome analysis saved to {gender_output_file_path}")


# ---- Age group-wise Summary ----
age_group_summary = df_filtered.groupby(['market', 'age_group']).apply(
    lambda x: pd.Series({
        'S6_customer': (x[x['dSEGMENT'] == 1]['S6'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S6_non_customer': (x[x['dSEGMENT'] == 2]['S6'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
        'S7_customer': (x[x['dSEGMENT'] == 1]['S7'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S7_non_customer': (x[x['dSEGMENT'] == 2]['S7'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
    })
).reset_index()

# Calculate change in social outcomes for age groups
age_group_summary['life_satisfaction_change'] = (age_group_summary['S6_customer'] - age_group_summary['S6_non_customer'])/age_group_summary['S6_customer']
age_group_summary['community_trust_change'] = (age_group_summary['S7_customer'] - age_group_summary['S7_non_customer'])/age_group_summary['S7_customer']
age_group_summary['social_change'] = (age_group_summary['life_satisfaction_change'] + age_group_summary['community_trust_change']) / 2

# Save age group-wise results
age_output_file_path = 'data/outputs/social_change_age.xlsx'
age_group_summary.to_excel(age_output_file_path, index=False)




# Calculate market-wise summary
market_summary = df.groupby('market').apply(
    lambda x: pd.Series({
        'S6_customer': (x[x['dSEGMENT'] == 1]['S6'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S6_non_customer': (x[x['dSEGMENT'] == 2]['S6'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
        'S7_customer': (x[x['dSEGMENT'] == 1]['S7'] * x[x['dSEGMENT'] == 1]['WEIGHT']).sum() / x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'S7_non_customer': (x[x['dSEGMENT'] == 2]['S7'] * x[x['dSEGMENT'] == 2]['WEIGHT']).sum() / x[x['dSEGMENT'] == 2]['WEIGHT'].sum(),
        'weighted_customers': x[x['dSEGMENT'] == 1]['WEIGHT'].sum(),
        'weighted_non_customers': x[x['dSEGMENT'] == 2]['WEIGHT'].sum()
    })
).reset_index()

# Calculate change in social outcomes
market_summary['life_satisfaction_change'] = (market_summary['S6_customer'] - market_summary['S6_non_customer'])/market_summary['S6_customer']
market_summary['community_trust_change'] = (market_summary['S7_customer'] - market_summary['S7_non_customer'])/market_summary['S7_customer']
market_summary['social_change'] = (market_summary['life_satisfaction_change'] + market_summary['community_trust_change']) / 2

# Calculate total weighted counts
market_summary['weighted_total'] = market_summary['weighted_customers'] + market_summary['weighted_non_customers']

# Reorder columns for better readability
column_order = [
    'market',
    'S6_customer', 'S6_non_customer',
    'S7_customer', 'S7_non_customer',
    'life_satisfaction_change', 'community_trust_change', 'social_change',
    'weighted_total'
]
market_summary = market_summary[column_order]

# Save results
output_file_path = 'data/outputs/social_change_market.xlsx'
market_summary.to_excel(output_file_path, index=False)


