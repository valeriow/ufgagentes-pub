import pandas as pd
import glob
    
    
def get_justwatch_ranks():
    """Collect JustWatch ranking data from multiple CSV files in the 'data' directory.
    
    This function reads all CSV files that match the pattern 'justwatch_rank*.csv',
    extracts the collection date from the filename, and combines all data into a single DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame containing the collected JustWatch ranking data.
    """    
        
    # get all csv files in the directory that match the pattern
    files = sorted(glob.glob('data/justwatch_rank*.csv'))
    all_data = []
    for file in files:
        df = pd.read_csv(file)
        df['collect_date'] = file.split('_')[-1].replace('.csv', '')
        # concatenate all dataframes into one
        all_data.extend(df.to_dict(orient='records'))   
        
    # create a new dataframe from the list of dictionaries
    df_justwatch_ranks = pd.DataFrame(all_data)
    return df_justwatch_ranks
