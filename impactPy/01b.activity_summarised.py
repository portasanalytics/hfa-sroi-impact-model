

"""
This script processes survey and activity data to create scenario breakdowns for the SROI model
across different gender, age group, and income level cuts per market.

- Loads and merges survey and activity data.
- Maps demographic variables (gender, age group, market, and income levels).
- Calculates summaries for customer activity and spending behavior, grouped by gender, age group, and income levels.
- Computes weighted averages and medians to produce the final reports.
- Results are saved in separate Excel files for different demographic segments.

"""



import pandas as pd
import numpy as np

# Load Data
def load_data():
    survey_df = pd.read_excel('data/survey_data/Elasticity_Questionnaire_Latest.xlsx', sheet_name='Data')
    activity_df = pd.read_excel('data/outputs/activity_output.xlsx')
    return pd.merge(survey_df, activity_df, on=['S1', 'dSEGMENT', 'uuid'], how='left')

# Mappings
GENDER_MAPPING = {1: "Male", 2: "Female", 3: "Others", 4: "Prefer not to answer"}
AGE_MAPPING = {2: "Young Adults (16-35)", 3: "Young Adults (16-35)", 
               4: "Old Adults (>35)", 5: "Old Adults (>35)", 6: "Old Adults (>35)", 7: "Old Adults (>35)"}
MARKET_MAPPING = {1: "Australia", 2: "Canada", 3: "Germany", 4: "Ireland", 5: "Japan",
                  6: "KSA (Saudi Arabia)", 7: "New Zealand", 8: "Singapore", 9: "Spain",
                  10: "USA (United States of America)"}
COLUMN_MAPPING = {1: "AU", 2: "CA", 3: "DE", 4: "IE", 5: "JP", 6: "SA", 7: "NZ", 8: "SG", 9: "ES", 10: "US"}

# Income level mapping
INCOME_MAPPINGS = {
    1: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Australia
    2: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Canada
    3: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'High'},  # Germany
    4: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Ireland
    5: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'High', 6: 'High'},  # Japan
    6: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Saudi Arabia
    7: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # New Zealand
    8: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'High', 6: 'High'},  # Singapore
    9: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'High', 7: 'High', 8: 'High'},  # Spain
    10: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'}  # USA
}

# Data Processing Functions
def map_income_level(row):
    market = row['S1']
    income_column = f'S5_{COLUMN_MAPPING[market]}'
    income_value = row[income_column]
    
    if income_value == 99:
        return 'Prefer not to answer'
    
    return INCOME_MAPPINGS.get(market, {}).get(income_value, 'Unknown')

def process_data(df):
    df['gender'] = df['S4'].map(GENDER_MAPPING)
    df['age_group'] = df['dS3_RECODE'].map(AGE_MAPPING)
    df['market'] = df['S1'].map(MARKET_MAPPING)
    df['income_level'] = df.apply(map_income_level, axis=1)
    return df

# Analysis Functions
def weighted_average(group):
    return np.average(group['active_flag'], weights=group['WEIGHT'])

def calculate_segment_summary(segment_data, group_columns):
    grouped = segment_data.groupby(['market'] + group_columns)
    weighted_active = grouped.apply(weighted_average, include_groups=False)
    total_weight = grouped['WEIGHT'].sum()
    weighted_count = grouped['WEIGHT'].sum()
    
    return pd.DataFrame({
        'Active': weighted_active,
        'Total Weight': total_weight,
        'Weighted Count': weighted_count
    }).reset_index()

def create_activity_summary(df, group_columns):
    customers_summary = calculate_segment_summary(df[df['dSEGMENT'] == 1], group_columns)
    customers_summary.columns = ['market'] + group_columns + ['active customers', 'total weight customers', 'customers']

    non_customers_summary = calculate_segment_summary(df[df['dSEGMENT'] == 2], group_columns)
    non_customers_summary.columns = ['market'] + group_columns + ['active non-customers', 'total weight non-customers', 'non_customers']

    total_non_customers = df[df['dSEGMENT'] == 2].groupby(['market'] + group_columns)['WEIGHT'].sum().reset_index()
    total_non_customers.columns = ['market'] + group_columns + ['total non-customers']

    final_summary = pd.merge(customers_summary, non_customers_summary, on=['market'] + group_columns)
    final_summary = pd.merge(final_summary, total_non_customers, on=['market'] + group_columns)

    final_summary['change'] = final_summary['active customers'] - final_summary['active non-customers']
    final_summary['total count'] = final_summary['total weight customers'] + final_summary['total weight non-customers']

    final_summary['active customers'] = (final_summary['active customers']).round(5)
    final_summary['active non-customers'] = (final_summary['active non-customers']).round(5)
    final_summary['change'] = (final_summary['change']).round(5)

    final_summary['non-customers %'] = (final_summary['total non-customers'] / final_summary['total count']).round(1)

    output_columns = ['market'] + group_columns + ['active customers', 'active non-customers', 'change', 
                     'customers', 'non_customers', 'total count', 'non-customers %']
    return final_summary[output_columns]

# Spending Analysis Functions
def weighted_median(data, weights):
    data, weights = np.array(data).squeeze(), np.array(weights).squeeze()
    s_data, s_weights = map(np.array, zip(*sorted(zip(data, weights))))
    midpoint = 0.5 * sum(s_weights)
    if any(weights > midpoint):
        w_median = (data[weights == np.max(weights)])[0]
    else:
        cs_weights = np.cumsum(s_weights)
        idx = np.where(cs_weights <= midpoint)[0][-1]
        if cs_weights[idx] == midpoint:
            w_median = np.mean(s_data[idx:idx+2])
        else:
            w_median = s_data[idx+1]
    return w_median

def calculate_spending_summary(data, group_cols):
    def group_stats(group):
        local_median = weighted_median(group['Q2r1'], group['WEIGHT'])
        usd_median = local_median * group['currency_rate'].iloc[0]
        
        weighted_total = np.sum(group['WEIGHT'])
        weighted_local_avg = np.sum(group['Q2r1'] * group['WEIGHT']) / weighted_total
        weighted_usd_avg = weighted_local_avg * group['currency_rate'].iloc[0]

        return pd.Series({
            'median_spent_local': local_median,
            'median_spent_$': usd_median,
            'avg_spent_local': weighted_local_avg,
            'avg_spent_$': weighted_usd_avg,
            'weighted_total': weighted_total
        })

    data = data.copy()
    data['currency_rate'] = data['market'].map(CURRENCY_RATES)

    grouped = data.groupby(group_cols)
    summary = grouped.apply(group_stats, include_groups=False).reset_index()
    
    numeric_columns = ['median_spent_local', 'median_spent_$', 'avg_spent_local', 'avg_spent_$', 'weighted_total']
    summary[numeric_columns] = summary[numeric_columns].round(2)
    
    return summary

# Main Execution
if __name__ == "__main__":
    # Load and process data
    df = load_data()
    df = process_data(df)

    # Calculate and save activity summaries
    for group in ['gender', 'age_group', 'income_level']:
        summary = create_activity_summary(df, [group])
        summary.to_excel(f'data/outputs/activity_summarised_{group}.xlsx', index=False)

    # Calculate and save spending summaries
    customers_df = df[(df['dSEGMENT'] == 1) & (df['gender'].isin(['Male', 'Female']))].copy()
    
    CURRENCY_RATES = {
        "Australia": 0.64, "Canada": 0.73, "Germany": 1.05, "Ireland": 1.05, "Japan": 0.0067,
        "KSA (Saudi Arabia)": 0.27, "New Zealand": 0.59, "Singapore": 0.73, "Spain": 1.05,
        "USA (United States of America)": 1
    }

    for group in ['gender', 'age_group']:
        spending_summary = calculate_spending_summary(customers_df, ['market', group])
        spending_summary = spending_summary.sort_values(['market', group])
        spending_summary.to_excel(f'data/outputs/spending_summarised_{group}.xlsx', index=False)

    # Income level spending summary
    income_spending_summary = calculate_spending_summary(
        customers_df[customers_df['income_level'] != 'Prefer not to answer'], 
        ['market', 'income_level']
    )
    income_spending_summary = income_spending_summary.sort_values(['market', 'income_level'])
    income_spending_summary.to_excel('data/outputs/spending_summarised_income.xlsx', index=False)

    print("All summaries have been calculated and saved.")