# HFA SROI Impact Model:

This repository contains scripts that calculate the Social Return on Investment (SROI) for the HFA project. The model uses survey data: containing activity level and pricing scenarios, to calculate social, economic and health outcomes.

## Script 1a: Physical Activity Calculation
**Purpose**: Calculate weekly physical activity minutes from survey data and classifies them as active or inactive as per WHOs guidelines.

- Processes survey data to compute total weekly physical activity.
- Formula: `total minutes = frequency x duration x intensity (based on heart rate)`.
- Classifies respondents as active or inactive based on WHO guidelines (150+ minutes of moderate activity or equivalent).
- **Output**: Flags respondents as active or inactive for use in subsequent analyses.

---

## Script 1b: Scenario Breakdown (Gender, Age, Income)
**Purpose**: Process survey and activity data to create scenario breakdowns by gender, age group, and income level.

- Loads and merges survey and activity data.
- Maps demographic variables (gender, age group, and income).
- Calculates activity and spending behavior summaries, segmented by gender, age, and income.
- Computes weighted averages and medians for spending behavior.
- **Output**: Saves results in separate Excel files for different demographic segments (gender, age, income).

---

## Script 2a, 2b: Price Elasticity Model (Non-Customers)
**Purpose**: Analyze price elasticity for non-customers across 5 pricing tiers in 10 markets.

- Focuses on non-customers (`dSEGMENT == 2`).
- Uses 5 pricing scenarios from survey: 10%, 20%, 40%, 60%, 80% discounts.
- Applies cumulative response logic: a "Yes" at a lower price implies "Yes" for all higher prices.
- Calculates weighted "Yes" responses for each pricing scenario, segmented by market and gender.
- Merges with urban population data to estimate potential new customers - this market penetration data is loaded as input, uses penetration levels from different studies.
- Formula: 
        `New customers = % yes (survey) x % non-customers (survey) x % price as barrier (survey) x urban non-customers (using new penetration levels provided by consulting team)`
        `Newly active customers = New customers x % Change in activity levels (% Active customers - % Active non-customers: survey)`
- **Output**: Saves scenario results and new customer estimates in Excel files.

---

## Script 3: Business Outcome Calculation
**Purpose**: Estimate total spending for new customers by gender, age group, and income level.

- Merges elasticity scenario data with spending data by market and demographic group.
- Calculates median and average spending (in local and USD currencies) for new customers.
- Segments results by gender, age, and income.
- **Output**: Saves business outcomes for each segment in Excel files.

---

## Script 4: Social Outcome Calculation
**Purpose**: Measure the social impact of converting non-customers into customers.

- Calculates social outcomes based on survey responses to life satisfaction (S6) and community trust (S7) questions.
- **Output**: Saves results segmented by gender in Excel files for further analysis.

---

## Script 5: Health Impact Calculation
**Purpose**: Calculate health outcomes and cost savings resulting from increased physical activity.

- Uses activity levels, population risk, population dalys, cost per case and relative risk data to estimate health outcomes.
- Calculates cases prevented, deaths averted, DALYs saved, and healthcare cost savings (direct and indirect).
- Segments results by gender and geography.
- **Output**: Health outcomes segmented by gender and geography are saved in Excel files.

---

## Additional Scripts and Inputs

### Market Penetration and Healthcare Expenditure Calculations
1. **Market Penetration Calculation**:
   - Uses previous studies to calculate market penetration levels, segmented by gender, income, and age.

2. **Healthcare Expenditure Predictor**:
   - Predicts healthcare expenditure for two markets using the UK as the baseline.

3. **Adjusted Cost Calculator**:
   - Converts UK healthcare costs to updated costs for 10 other markets.
   - Uses inflation rates and healthcare expenditure data to adjust for local conditions.
   - **Output**: Differentiated healthcare costs across markets are saved in Excel files.

---

## Inputs
- **CPI Levels**: Consumer Price Index data used for market price adjustments.
- **Healthcare Expenditure Data**: Used for calculating healthcare costs across 10 markets, with the UK as the baseline.

---

This repository is structured to support modular execution of scripts, with results saved in structured formats (Excel) for further analysis. Each script builds upon the outputs of others to provide a comprehensive SROI analysis for the HFA project.
