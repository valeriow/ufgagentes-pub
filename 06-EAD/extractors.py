from googlenews_collector import GoogleNewsCollector
import collect_justwatch
import pandas as pd
import glob


def extract_googlenews_mentions(df_justwatch_ranks):
    """
    Extract Google News mentions for titles in df_justwatch_ranks.
    This function checks if the Google News mentions data already exists. If it does, it performs an incremental load
    by fetching only the new data since the last date in the existing data. If it does not exist, it performs a full load
    starting from 7 days before the earliest date in df_justwatch_ranks to the current date minus one day.  
    
    The results are saved to a CSV file named 'googlenews_mentions_count.csv' in the 'data' directory.
    
    
    Parameters:
    df_justwatch_ranks (DataFrame): DataFrame containing JustWatch ranks with 'title' and 'type' columns.

    Returns:
    None: Saves the Google News mentions to a CSV file.
    """
    gnc = GoogleNewsCollector()
        
    try:
        df_googlenews_mentions = pd.read_csv("data/googlenews_mentions_count.csv")
    except Exception:
        df_googlenews_mentions = pd.DataFrame(columns=["date", "count", "title"])
    
    # Verify if is the first load or incremental load
    if df_googlenews_mentions.empty:
        last_date = df_justwatch_ranks['collect_date'].min()
        # start_date = last_date - 7 days 
        last_date = pd.to_datetime(last_date)
        start_date = last_date - pd.Timedelta(days=7) # 7 days before last date
        end_date = pd.to_datetime("today") - pd.Timedelta(days=1)
        print(f"First load of Google News mentions data. Starting from {start_date} to {end_date}")
    else: # incremental load. Only load new data
        start_date =  pd.to_datetime(df_googlenews_mentions['date']).max()
        start_date = start_date + pd.Timedelta(days=1)  # next day after the last date in the data
        end_date = pd.to_datetime("today") - pd.Timedelta(days=1)
        print(f"Incremental load of Google News mentions data. Starting from {start_date} to {end_date}")


    if start_date > end_date:
        print("No new data to load for Google News mentions. The last date is today or in the future.")
    else:    
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d') # yesterday
        all_data = []
        df_justwatch_ranks_unique = df_justwatch_ranks.groupby(['type', 'title']).size().reset_index(name='count')
        for _ , row in df_justwatch_ranks_unique.iterrows():
            print(row['title'], row['type'])    
            topic = row['title']
            df = gnc.count_news_by_date(start_date=start_date, end_date=end_date, topic=topic)
            df['title'] = topic
            df['type'] = row['type']
            all_data.extend(df.to_dict(orient='records'))
            
        # Concatenate df_googlenews_mentions with the new data
        if not all_data:
            print("No new data found for Google News mentions.")
        else:
            print(f"Found {len(all_data)} new records for Google News mentions.")
            df_googlenews_mentions = pd.concat([df_googlenews_mentions, pd.DataFrame(all_data)], ignore_index=True) 
            df_googlenews_mentions.to_csv("data/googlenews_mentions_count.csv", index=False)
            print("Google News mentions data saved to data/googlenews_mentions_count.csv")  
            

def daily_pipeline(extract_justwatch=True):
    """
    Run the daily pipeline to extract Google News mentions.
    
    This function loads the JustWatch ranks data, extracts Google News mentions, and saves the results to a CSV file.
    
    Returns:
    None
    """
    
    # Collect JustWatch ranks data
    if extract_justwatch:
        print("Collecting JustWatch ranks data...")
        movies_df = collect_justwatch.collect_just_watch_ranking()
    else:
        print("ignoring JustWatch ranks extraction...") 
        
    # Load JustWatch ranks data
    files = glob.glob("data/justwatch_rank_*.csv")
    if not files:
        print("No JustWatch ranks data found.")
        return
    
    
    df_justwatch_ranks = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    
    # Extract Google News mentions
    extract_googlenews_mentions(df_justwatch_ranks)

