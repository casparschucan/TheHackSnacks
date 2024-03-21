import pandas as pd 

# Load the data
def load_data():
    """Loads the ESG data from the csv file provided by SIX"""
    return pd.read_csv("../ESG/EUESGMANUFACTURER.csv")

def pivot_data(data):
    # Reshape the data
    reshaped_data = data.copy().pivot_table(index='ISIN', columns='ESGFactor', values='ESGFactorAmountLastYear', aggfunc='first')
    reshaped_data_units = data.copy().pivot_table(index='ISIN', columns='ESGFactor', values='ESGFactorAmountLastYearUnit', aggfunc='first')

def prune_bad_emitters(data, threshold=2500):
    """Removes companies with a high carbon footprint from dataframe"""
    #Get entries for which all 3 scope entries are available
    scope1 = data['30020_GHG_Emissions_Scope_1_Value']
    scope2 = data['30060_GHG_Emissions_Scope_2_Value']
    scope3 = data['30100_GHG_Emissions_Scope_3_Value']

    #Join the scopes by ISIN and drop zeros, they are in tCO2e/M€ invested
    emitters = pd.concat([scope1,scope2,scope3], axis=1).dropna()
    emitters["total"] = emitters.sum(axis=1)
    emitters.drop(emitters.loc[emitters['total']==0].index, inplace=True)

    emitters["CarbonFootprint"] = (emitters["total"] - 52814)
    return emitters[emitters["savings_vs_index"] < 3000]




def get_viable_funds(criteria):
    """Returns a dataframe of funds that meet the criteria"""
    data = pivot_data(load_data())
    viable_funds = data.copy()

    for crit in criteria:
        if crit == 'CarbonFootprint':
            viable_funds = prune_bad_emitters(viable_funds)
            
    return viable_funds
