import pandas as pd 
import numpy as np
import plotly.express as px

curr_folder = "/".join(__file__.split("/")[:-1])

# Load the data
def load_data() -> pd.DataFrame:
    """Loads the ESG data from the csv file provided by SIX"""
    return pd.read_csv(f"{curr_folder}/../ESG/EUESGMANUFACTURER.csv")

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
    emitters = emitters.drop(columns=["30020_GHG_Emissions_Scope_1_Value", "30060_GHG_Emissions_Scope_2_Value", "30100_GHG_Emissions_Scope_3_Value", "total"]);
    emitters = emitters[emitters["CarbonFootprint"] < -threshold];
    print(len(emitters))
    return emitters;

def prune_big_wage_gaps(data, threshold=15):
    """Removes companies with a high wage gap from dataframe"""
    #Get entries for which all 3 scope entries are available
    wage_gap = data['31050_Unadjusted_Gender_Pay_Gap_Value']
    wage_gap = pd.concat([wage_gap], axis=1).dropna();
    wage_gap["WageGap"] = (wage_gap["31050_Unadjusted_Gender_Pay_Gap_Value"]*100)
    wage_gap = wage_gap.drop(columns=["31050_Unadjusted_Gender_Pay_Gap_Value"])
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
        if not c in portfolio.columns:
            continue
        portfolio = rebalance(portfolio, c, v, n)
    # Normalize weights to sum up to 1
    portfolio = portfolio.sort_values(by='weight', ascending=False)
    portfolio = portfolio[:30]
    portfolio['weight'] /= portfolio['weight'].sum()
    return portfolio

def rebalance(df: pd.DataFrame, c: str, v: int, n: int):
    decay_rate = 1.1  # Determines the rate of exponential decay for weights
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


def generate_flying_miles(portfolio: pd.DataFrame, value):
    """Generates the flying miles for each company"""
    e_eco_gain = portfolio["CarbonFootprint"].mul(portfolio["weight"]).sum();
    flying_miles = -e_eco_gain * value/42420/6315;
    return f"you saved enough emissions to have an airbus a380 fly {flying_miles}x times from Zürich to New York!";

def generate_wage_gap(portfolio: pd.DataFrame):
    """Generates the wage gap for each company"""
    wage_gap = portfolio["WageGap"].mul(portfolio["weight"]).sum();
    return f"The unadjusted wage gap in your portfolio {wage_gap}% is far better than the 18% here in Switzerland!";

def generate_portfolio(criteria: dict[str, int], value):
    portfolio = portfolio_optimization(criteria)
    portfolio["CarbonFootprint"] = (portfolio["CarbonFootprint"] + 52814)/1000;
    htmlplots = dict()
    funfacts = dict()
    portfolio["scatter_size"] = (portfolio["weight"]  + 0.2)*2
    portfolio["colors"] = 1-portfolio["weight"]
    for c in criteria:
        if c == "CarbonFootprint":
            funfacts[c] = (generate_flying_miles(portfolio, value))
            carbonfig = px.scatter(portfolio, y="weight", x="CarbonFootprint", size='scatter_size', color="colors", color_continuous_scale="Bluered_r", title="Carbon Footprint")
            carbonfig.update_layout(yaxis_title="Proportion of money invested", xaxis_title="Carbon Footprint (kgCO2e/€ invested)")
            htmlplots[c] = carbonfig.to_html(full_html=False, include_plotlyjs='cdn')
        if c == "WageGap":
            funfacts[c] = generate_wage_gap(portfolio)
            wagefig = px.scatter(portfolio, y="weight", x="WageGap", size="scatter_size", color="colors", color_continuous_scale="Bluered_r", title="Wage Gap")
            wagefig.update_layout(yaxis_title="Proportion of money invested", xaxis_title="Wage Gap (%)")
            htmlplots[c] = wagefig.to_html(full_html=False, include_plotlyjs='cdn')
    return funfacts, htmlplots, portfolio
