"""
This Python script processes healthcare cost data for various global markets, 
adjusting costs based on inflation and currency exchange rates. 
The script requires three main inputs: healthcare cost per case data (.csv), 
CPI data for inflation adjustment (.csv), 
and predicted normalised healthcare expenditure data (.xlsx) - PPP, with UK as baseline)
"""



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
        
        base_date = datetime(int(row['base_year']), 7, 1)
        exchange_rate = fetch_exchange_rate(currency_pair, base_date)
        if exchange_rate is not None:
            local_cost = row['cost_per_case_unflated'] * exchange_rate
            return pd.Series([local_cost, exchange_rate], index=['cost_per_case', 'forex_rate'])
        return pd.Series([np.nan, np.nan], index=['cost_per_case', 'forex_rate'])
    
    return df.apply(convert_cost, axis=1)

def calculate_inflated_costs(df, cpi_data):
    def calculate_inflation(row):
        if pd.isna(row['base_year']):
            return pd.Series([np.nan, np.nan], index=['cost_inflated', 'inflation_rate'])
        
        inflation_factor = get_inflation_adjustment(cpi_data, row['Country'], int(row['base_year']))
        if pd.isna(inflation_factor):
            return pd.Series([np.nan, np.nan], index=['cost_inflated', 'inflation_rate'])
        cost_inflated = row['cost_per_case'] * inflation_factor
        return pd.Series([cost_inflated, inflation_factor], index=['cost_inflated', 'inflation_rate'])

    return df.apply(calculate_inflation, axis=1)

def process_market_data(df, markets, cpi_data, healthcare_expenditure):
    consolidated_data = []

    for market, currency_pair in markets.items():
        market_df = df.copy()
        market_df = market_df[(market_df['age_group'] == 'adult') & (market_df['category'] == 'health')]

        market_df[['cost_per_case', 'forex_rate']] = convert_cost_to_local_currency(market_df, currency_pair)
        market_df['Country'] = market
        market_df[['cost_inflated', 'inflation_rate']] = calculate_inflated_costs(market_df, cpi_data)

        # Ensure 'Country Name' is correctly matched, and the healthcare expenditure for 2024 is accessed
        try:
            healthcare_expenditure_2024 = healthcare_expenditure.loc[healthcare_expenditure['Country Name'] == market, '2024'].values[0]
        except IndexError:
            healthcare_expenditure_2024 = np.nan  # Handle missing data gracefully
        
        # Add adjusted cost based on 2024 healthcare expenditure
        market_df['adjusted_cost_with_healthcare_expenditure'] = market_df['cost_inflated'] * healthcare_expenditure_2024
        
        consolidated_data.append(market_df[['Country', 'factor', 'age_group', 'gender', 'direct', 
                                            'cost_per_case', 'cost_inflated', 'forex_rate', 'inflation_rate', 
                                            'adjusted_cost_with_healthcare_expenditure', 'base_year']])

    return pd.concat(consolidated_data, ignore_index=True)


def save_to_csv(df, file_path):
    df.to_csv(file_path, index=False)

def main():
    input_file = 'data/inputs/cost_per_case.csv'
    cpi_file = 'data/inputs/cpi.csv'
    expenditure_file = 'data/inputs/predicted_healthcare_expenditure.xlsx'
    output_file = 'data/inputs/cost_per_case_adjusted.csv'
    
    markets = {
        'Australia': 'GBPAUD=X', 'Canada': 'GBPCAD=X', 'Germany': 'GBPEUR=X', 'Ireland': 'GBPEUR=X',
        'KSA': 'GBPSAR=X', 'Newzealand': 'GBPNZD=X', 'Singapore': 'GBPSGD=X', 'Spain': 'GBPEUR=X',
        'America': 'GBPUSD=X', 'Japan': 'GBPJPY=X'
    }

    df = read_data(input_file)
    cpi_data = read_cpi_data(cpi_file)
    healthcare_expenditure = read_healthcare_expenditure_data(expenditure_file)
    
    processed_data = process_market_data(df, markets, cpi_data, healthcare_expenditure)
    save_to_csv(processed_data, output_file)

if __name__ == "__main__":
    main()