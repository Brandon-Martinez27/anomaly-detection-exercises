import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import os
from env import host, user, password


###################### Acquire Zillow Data ######################

def get_connection(db, user=user, host=host, password=password):
    '''
    This function uses my info from my env file to
    create a connection url to access the Codeup db.
    '''
    return f'mysql+pymysql://{user}:{password}@{host}/{db}'
    
def new_zillow_data():
    '''
    This function reads the zillow data from the Codeup db into a df,
    write it to a csv file, and returns the df.
    '''
    sql_query = '''
            SELECT *
            FROM properties_2017 as prop 
            INNER JOIN (
                    SELECT id, p.parcelid, logerror, transactiondate
                    FROM predictions_2017 AS p
                    INNER JOIN (
                            SELECT parcelid,  MAX(transactiondate) AS max_date
                            FROM predictions_2017 
                            GROUP BY (parcelid)
                    ) AS sub
                        ON p.parcelid = sub.parcelid
                    WHERE p.transactiondate = sub.max_date
            ) AS subq
                ON prop.id = subq.id;
                 '''
    df = pd.read_sql(sql_query, get_connection('zillow'))
    df.to_csv('zillow.csv')
    return df

def get_zillow_data(cached=False):
    '''
    This function reads in titanic data from Codeup database if cached == False 
    or if cached == True reads in zillow df from a csv file, returns df
    '''
    if cached or os.path.isfile('zillow_df.csv') == False:
        df = new_zillow_data()
    else:
        df = pd.read_csv('zillow_df.csv', index_col=0)
    return df

###################### Prepare Zillow Data ######################

def missing_rows_df(df):
    '''Takes in a dataframe of observations and attributes 
    and returns a dataframe where each row is an attribute name, 
    the first column is the number of rows with missing values 
    for that attribute, and the second column is percent of total 
    rows that have missing values for that attribute'''
    d = {'num_rows_missing': df.isna().sum(), 
         'pct_rows_missing': df.isna().sum()/len(df)}
    new_df = pd.DataFrame(data=d)
    return new_df

def missing_cols_df(df):
    '''takes in a dataframe and returns a dataframe 
    with 3 columns: the number of columns missing, 
    percent of columns missing, and number of rows 
    with n columns missing'''
    d = {'num_cols_missing': df.isna().sum(axis=1), 
         'pct_cols_missing': df.isna().sum(axis=1)/len(df.columns),
         'num_rows': 'fill'}
    new_df = pd.DataFrame(data=d)
    return new_df

def handle_missing_values(df, prop_required_column, prop_required_row):
    threshold = int(round(prop_required_column*len(df.index),0))
    df.dropna(axis=1, thresh=threshold, inplace=True)
    threshold = int(round(prop_required_row*len(df.columns),0))
    df.dropna(axis=0, thresh=threshold, inplace=True)
    return df

def wrangle_zillow():
    # acquire zillow data
    df = get_zillow_data()
    
    # use only determined single unit properties
    prop = pd.Series([260, 261, 263, 273, 275, 279, 276])
    df_su = df[(df.propertylandusetypeid.isin(prop))]

    # use handle_missing_values to filter data based on 
    # 85% of rows and 75% of columns
    df1 = handle_missing_values(df_su, .85, .75)

    # drop the rest of the missing values
    df2 = df1.dropna()
    df2.isna().sum()
    return df2