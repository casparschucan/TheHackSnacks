import numpy as np
import pandas as pd

def read_esg_data(filename: str) -> pd.DataFrame:
    """
    read_esg_data reads the esg data from the csv file and returns a pandas dataframe.
    """


    current_isin = None

    esg_factors = []

    # Read the csv file line by line
    for i, line in enumerate(open(filename, 'r')):
        # Split the line by comma
        fields = line.split(',')

        # get field names from first line
        if i == 0:
            field_names = fields
            # create a map from name to index
            ni_map = {name: i for i, name in enumerate(field_names)}
            on_map = {i: name for i, name in enumerate(field_names)}
            continue

        # generic data  (up to ESGDeliveryDate)
        last_generic_data = ni_map['ESGDeliveryDate']
    
        # get all generic data
        generic_data = fields[:last_generic_data + 1]

        isin = generic_data[ni_map['ISIN']]
        companyLongName = generic_data[ni_map['companyLongName']]

        # ESG data
        esg_data = fields[last_generic_data + 1:]

        # get all esg types (ESGFactor)
        esg_factors.append(esg_data[ni_map['ESGFactor']])


    # create dataframe with isin , esgfactor1, esgfactor2, ....
    
    # read through the data again


    return generic_data


read_esg_data('EUESGMANUFACTURER-LIGHT.csv')
