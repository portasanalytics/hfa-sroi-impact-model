

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def read_data(file_path):
    return pd.read_csv(file_path)

def read_cpi_data(file_path):
    return pd.read_csv(file_path, index_col='country')

def read_healthcare_expenditure_data(file_path):
    return pd.read_excel(file_path)

def read_income_adjustment_factor(file_path):
    """Read income adjustment factors from both UK and USA sheets"""

    # Read UK sheet for non-osteoporosis factors
    uk_df = pd.read_excel(file_path, sheet_name='UK')
    uk_df = uk_df[['Country Name', 'factor']].rename(columns={'factor': 'income_adjustment_factor'})
    uk_df['source'] = 'UK'

    # Read USA sheet for osteoporosis factors
    usa_df = pd.read_excel(file_path, sheet_name='USA')
    usa_df = usa_df[['Country Name', 'factor']].rename(columns={'factor': 'income_adjustment_factor'})
    usa_df['source'] = 'USA'

    return uk_df, usa_df

def get_inflation_adjustment(cpi_data, country, base_year):
    try:
        start_cpi = cpi_data.loc[country, str(base_year)]
        end_cpi = cpi_data.loc[country, '2024']
        inflation_factor = end_cpi / start_cpi
        return inflation_factor
    except KeyError:
        return np.nan

def fetch_exchange_rate(currency_pair, date, max_attempts=4):
    for i in range(max_attempts):
        adjusted_date = date + timedelta(days=i)
        data = yf.download(currency_pair, start=adjusted_date, end=adjusted_date + timedelta(days=1))
        if not data.empty:
            return data['Close'].iloc[0]
    return None

def convert_cost_to_local_currency(df, currency_pair):
    def convert_cost(row):
        if pd.isna(row['base_year']):
            return pd.Series([np.nan, np.nan], index=['cost_per_case', 'forex_rate'])
        
        base_date = datetime(int(row['base_year']), 10, 17)
        exchange_rate = fetch_exchange_rate(currency_pair, base_date)
        if exchange_rate is not None:
            local_cost = row['cost_per_case_unflated'] * exchange_rate
            return pd.Series([local_cost, exchange_rate], index=['cost_per_case', 'forex_rate'])
        return pd.Series([np.nan, np.nan], index=['cost_per_case', 'forex_rate'])
    
    return df.apply(convert_cost, axis=1)

def calculate_inflated_costs(df, cpi_data):
    def calculate_inflation(row):
        if pd.isna(row['base_year']):
            return pd.Series([np.nan, np.nan], index=['inflation_rate','cost_inflated'])
        
        inflation_factor = get_inflation_adjustment(cpi_data, row['geography'], int(row['base_year']))
        if pd.isna(inflation_factor):
            return pd.Series([np.nan, np.nan], index=['inflation_rate','cost_inflated'])
        cost_inflated = row['cost_per_case'] * inflation_factor
        return pd.Series([inflation_factor, cost_inflated], index=['inflation_rate','cost_inflated'])

    return df.apply(calculate_inflation, axis=1)

def get_income_adjustment_factor(uk_data, usa_data, market, factor):
    """Get income adjustment factor based on the market and factor type"""
    try:
        # Use USA data for osteoporosis, UK data for all other factors
        if factor == 'osteoporosis':
            return usa_data.loc[usa_data['Country Name'] == market, 'income_adjustment_factor'].iloc[0]
        else:
            return uk_data.loc[uk_data['Country Name'] == market, 'income_adjustment_factor'].iloc[0]
    except (KeyError, IndexError):
        return np.nan

# [Previous imports and functions remain the same until process_market_data]

def process_market_data(df, markets, cpi_data, healthcare_expenditure, uk_adjustment_data, usa_adjustment_data):
    consolidated_data = []

    for market, currency_pair in markets.items():
        market_df = df.copy()
        market_df = market_df[(market_df['age_group'] == 'adult') & (market_df['category'] == 'health')]

        market_df[['cost_per_case', 'forex_rate']] = convert_cost_to_local_currency(market_df, currency_pair)
        market_df['geography'] = market
        market_df[['inflation_rate','cost_inflated']] = calculate_inflated_costs(market_df, cpi_data)

        try:
            healthcare_expenditure_2024 = healthcare_expenditure.loc[healthcare_expenditure['Country Name'] == market, '2024'].values[0]
        except IndexError:
            healthcare_expenditure_2024 = np.nan

        # Set adjustment_factor to 0 if direct is True; otherwise use income adjustment factor
        market_df['income_adjustment_factor'] = market_df.apply(
            lambda row: 0 if row['direct'] else get_income_adjustment_factor(uk_adjustment_data, usa_adjustment_data, market, row['factor']),
            axis=1
        )

        # Set healthcare expenditure to 0 if direct is False
        market_df['healthcare_expenditure_factor'] = market_df.apply(
            lambda row: healthcare_expenditure_2024 if row['direct'] else 0,
            axis=1
        )
        
        # Adjust costs based on the updated adjustment factor
        def adjust_costs(row):
            adjustment_factor = row['healthcare_expenditure_factor'] if row['direct'] else row['income_adjustment_factor']
            return row['cost_inflated'] * adjustment_factor

        market_df['cost_per_case_uk'] = market_df['cost_per_case_unflated']
        market_df['cost_per_case_local'] = market_df['cost_per_case']
        
        market_df['cost_per_case_adjusted'] = market_df.apply(adjust_costs, axis=1)

        # Include these columns in the final output
        consolidated_data.append(market_df[['geography', 'factor', 'age_group', 'gender', 'direct',
                                          'cost_per_case_uk', 'forex_rate', 'cost_per_case_local',
                                          'inflation_rate', 'cost_inflated',
                                          'healthcare_expenditure_factor', 'income_adjustment_factor',
                                          'cost_per_case_adjusted']])

    return pd.concat(consolidated_data, ignore_index=True)


def save_to_csv(df, file_path):
    df.to_csv(file_path, index=False)

def main():
    input_file = 'data/inputs/cost_per_case.csv'
    cpi_file = 'data/inputs/cpi.csv'
    expenditure_file = 'data/inputs/predicted_healthcare_expenditure.xlsx'
    income_adjustment_file = 'data/inputs/income_adjustment_factor.xlsx'
    output_file = 'data/health_data/cost_per_case_adjusted.csv'
    
    markets = {
        'Australia': 'GBPAUD=X', 'Canada': 'GBPCAD=X', 'Germany': 'GBPEUR=X', 'Ireland': 'GBPEUR=X',
        'KSA': 'GBPSAR=X', 'Newzealand': 'GBPNZD=X', 'Singapore': 'GBPSGD=X', 'Spain': 'GBPEUR=X',
        'America': 'GBPUSD=X', 'Japan': 'GBPJPY=X'
    }

    # Read all required data
    df = read_data(input_file)
    cpi_data = read_cpi_data(cpi_file)
    healthcare_expenditure = read_healthcare_expenditure_data(expenditure_file)
    
    # Read income adjustment data from both sheets
    uk_adjustment_data, usa_adjustment_data = read_income_adjustment_factor(income_adjustment_file)

    # Process market data with both UK and USA adjustment factors
    processed_data = process_market_data(df, markets, cpi_data, healthcare_expenditure, 
                                       uk_adjustment_data, usa_adjustment_data)
    save_to_csv(processed_data, output_file)

if __name__ == "__main__":
    main()