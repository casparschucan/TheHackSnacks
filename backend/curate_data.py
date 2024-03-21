import pandas as pd 
import numpy as np



# Load the data
def load_data() -> pd.DataFrame:
    """Loads the ESG data from the csv file provided by SIX"""
    return pd.read_csv("../ESG/EUESGMANUFACTURER.csv")

def pivot_data(data: pd.DataFrame) -> pd.DataFrame:
    # Reshape the data
    reshaped_data = data.copy().pivot_table(index='companyLongName', columns='ESGFactor', values='ESGFactorAmountLastYear', aggfunc='first')
    return reshaped_data

def prune_bad_emitters(data: pd.DataFrame, threshold=2500):
    """Removes companies with a high carbon footprint from dataframe"""
    #Get entries for which all 3 scope entries are available
    scope1 = data['30020_GHG_Emissions_Scope_1_Value']
    scope2 = data['30060_GHG_Emissions_Scope_2_Value']
    scope3 = data['30100_GHG_Emissions_Scope_3_Value']

    #Join the scopes by ISIN and drop zeros, they are in tCO2e/M€ invested
    emitters = pd.concat([scope1,scope2,scope3], axis=1).dropna();
    emitters["total"] = emitters.sum(axis=1);
    emitters.drop(emitters.loc[emitters['total']==0].index, inplace=True);

    emitters["CarbonFootprint"] = (emitters["total"] - 52814);
    emitters.head();
    emitters = emitters[emitters["CarbonFootprint"] < -threshold];
    print(len(emitters))
    return emitters;

def prune_big_wage_gaps(data, threshold=15):
    """Removes companies with a high wage gap from dataframe"""
    #Get entries for which all 3 scope entries are available
    wage_gap = data['31050_Unadjusted_Gender_Pay_Gap_Value']
    wage_gap = pd.concat([wage_gap], axis=1).dropna();
    wage_gap["WageGap"] = (wage_gap["31050_Unadjusted_Gender_Pay_Gap_Value"]*100)
    wage_gap = wage_gap[wage_gap["WageGap"] < threshold]
    print(len(wage_gap))
    return wage_gap
        


def get_viable_funds(criteria):
    """Returns a dataframe of funds that meet the criteria"""
    data : pd.DataFrame = pivot_data(load_data());
    viable_funds = data.copy();
    pruned_columns = list();

    for crit in criteria:
        if crit == "CarbonFootprint":
            pruned_columns.append(prune_bad_emitters(data));

        if crit == 'WageGap':
            pruned_columns.append(prune_big_wage_gaps(data));

    viable_funds = pd.concat(pruned_columns, axis=1, join='inner').dropna();
            
    return viable_funds

def portfolio_optimization(criteria: dict[str, int]):
    portfolio = get_viable_funds(criteria)
    n = portfolio.shape[0]
    portfolio['weight'] = 1 / n  # Initialize equal weights
    for c, v in criteria.items():
        portfolio = rebalance(portfolio, c, v, n)
    # Normalize weights to sum up to 1
    portfolio = portfolio.sort_values(by='weight', ascending=False)
    portfolio = portfolio[:30]
    portfolio['weight'] /= portfolio['weight'].sum()
    return portfolio

def rebalance(df: pd.DataFrame, c: str, v: int, n: int):
    decay_rate = 2  # Determines the rate of exponential decay for weights
    print(n)
    # Sorts the dataframe rows from "best" to "worst" based on the criterion
    df = df.sort_values(by=c, ascending=True)

    if v == 1:  # High importance: exponential decay
        weights = np.array([np.exp(-decay_rate * i) for i in range(n)])
        df['weight'] *= weights
    elif v == 0:  # Moderate importance: linear decay
        weights = np.linspace(1, 0, n)  # Linearly decreases from 1 to 0
        df['weight'] *= weights
    else:  # Indifference: no change in weights
        pass  # Weights remain unchanged
    return df

# Testing dataframe
#data = pd.DataFrame({'isin': ['a', 'b', 'c', 'd', 'e'], 'environmental': [1, 2, 3, 4, 5], 'social': [5, 4, 3, 2, 1], 'governance': [4, 2, 1, 5, 3]}).set_index('isin')

#display(portfolio_optimization(data, {'e': 0, 's': -1, 'g': -1}))
