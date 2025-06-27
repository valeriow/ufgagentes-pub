import pandas as pd
from justwatch_collector import JustWatchCollector
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def collect_just_watch_ranking(max_titles=10, headless=True):
    """Collect titles from JustWatch for movies and TV shows.
    This function uses the JustWatchCollector to scrape titles from JustWatch,
    scrolls down the page to load more titles, and saves the
    collected data to a CSV file.
    Args:
        max_titles (int): Maximum number of titles to collect.
    Returns:
        pd.DataFrame: DataFrame containing the collected titles and their details.
    Raises:
        Exception: If there is an error during the collection process.
    Example:
        collect_just_watch_ranking(max_titles=100)
    """
    # Create data directory if it doesn't exist
    data_directory = 'data'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        logger.info(f"Created directory: {data_directory}")
        
    # Get today's date in YYYY-MM-DD format for use in filenames
    today = time.strftime("%Y-%m-%d")

    # Define the content types to collect
    content_types = ["tv-shows", "movies"]
    #content_types = ["movies"] #TODO: remover

    # Collecting movies ranking from justwatch.com. Using Selenium to scroll down the page and collect more titles.
    all_justwatch_data = []
    for content_type in content_types:
        just_watch_collector = JustWatchCollector(country="us", content_type=content_type, headless=headless)
        just_watch_df = just_watch_collector.collect_ranking(content_type, rank_freq="daily", max_titles=max_titles) 
        just_watch_df['type'] = content_type  # Add content type column : series or movies
        all_justwatch_data.extend(just_watch_df.to_dict(orient='records'))

    #just_watch_df.to_csv(f'justwatch_{content_type}_{today}.csv')
    just_watch_csv_filename = f'{data_directory}/justwatch_rank_{today}.csv'
    df = pd.DataFrame(all_justwatch_data)
    df.to_csv(just_watch_csv_filename, index=False)
    logger.info(f"Collected JustWatch Ranking for {content_types} saved to CSV.")
    return df


def collect_just_watch(max_titles=50, max_scrolls=20, headless=True):
    """Collect titles from JustWatch for movies and TV shows.
    This function uses the JustWatchCollector to scrape titles from JustWatch,
    scrolls down the page to load more titles, and saves the                
    collected data to a CSV file.
    Args:
        max_titles (int): Maximum number of titles to collect.
        max_scrolls (int): Number of times to scroll down the page to load more titles.
        headless (bool): Whether to run the browser in headless mode.
    Returns:
        pd.DataFrame: DataFrame containing the collected titles and their details.
    Raises:
        Exception: If there is an error during the collection process.
    Example:
        collect_just_watch(max_titles=100, max_scrolls=10, headless=False)
    Raises:
        Exception: If there is an error during the collection process.
    Example:
        collect_just_watch(max_titles=100, max_scrolls=10, headless=False)
    """
    
    # Create data directory if it doesn't exist
    data_directory = 'data'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        logger.info(f"Created directory: {data_directory}")
        
    # Get today's date in YYYY-MM-DD format for use in filenames
    today = time.strftime("%Y-%m-%d")

    # Define the content types to collect
    content_types = ["tv-shows", "movies"]
    #content_types = ["movies"] #TODO: remover

    # Collecting movies ranking from justwatch.com. Using Selenium to scroll down the page and collect more titles.
    all_justwatch_data = []
    for content_type in content_types:
        just_watch_collector = JustWatchCollector(country="us", content_type=content_type, headless=headless)
        just_watch_df = just_watch_collector.collect_titles(max_titles=max_titles, max_scrolls=max_scrolls)
        just_watch_df['type'] = content_type  # Add content type column : series or movies
        all_justwatch_data.extend(just_watch_df.to_dict(orient='records'))

    #just_watch_df.to_csv(f'justwatch_{content_type}_{today}.csv')
    just_watch_csv_filename = f'{data_directory}/justwatch_{today}.csv'
    df = pd.DataFrame(all_justwatch_data).to_csv(just_watch_csv_filename, index=False)
    logger.info(f"Collected JustWatch {content_type} data and saved to CSV.")
    return df
