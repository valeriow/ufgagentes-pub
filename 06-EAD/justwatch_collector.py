from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

class JustWatchCollector:
    def __init__(self, country="br", content_type="series", headless=True):
        """
        Initialize the JustWatch collector.
        
        Args:
            country (str): Country code (e.g., "br", "us")
            content_type (str): Type of content ("series" or "movies")
        """
        
        self.__TIME2SLEEP__ = 0.5
        self.country = country
        self.content_type = content_type
        self.url = f"https://www.justwatch.com/{country}/{content_type}"
        
        # Setup Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-default-browser-check')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_argument('--disable-default-apps')
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
        self.chrome_options.add_argument(f"user-agent={headers['User-Agent']}")
        
        
        # Define CSS selectors for data extraction
        self.css_selectors = {
            'title': 'h1.title-detail-hero__details__title',
            'original_title': '.original-title',
            'year': 'h1.title-detail-hero__details__title .release-year',
            'rank': '.title-detail-hero-details__item__rank',
            'rank_change': '.hidden-horizontal-scrollbar__items .arrow-container p',
            'imdb_score': '.imdb-score'
        }

    def get_data(self, driver, css_selector, attribute='text'):
        """Helper function to extract data using CSS selectors."""
        data = [""]
        try:
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )
            if attribute != 'text':
                data = [element.get_attribute(attribute) for element in elements]
            else:
                data = [element.text for element in elements]
        except:
            print(f"No element found for css selector: {css_selector}")
        
        return data

    def scroll_down(self, driver):
        """Helper function to scroll down the page."""
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(self.__TIME2SLEEP__)

    def collect_titles(self, max_titles=100, max_scrolls=20):
        """
        Collect titles from JustWatch.
        
        Args:
            max_titles (int): Maximum number of titles to collect
            max_scrolls (int): Maximum number of scrolls to attempt
            
        Returns:
            pandas.DataFrame: DataFrame containing collected titles
        """
        # Initialize WebDrivers
        driver = webdriver.Chrome(options=self.chrome_options)
        driver_detail = webdriver.Chrome(options=self.chrome_options)
        
        data_result = {}
        titles = []
        scroll_count = 0

        try:
            # Navigate to JustWatch
            print(f"Accessing JustWatch {self.content_type} for {self.country}...")
            driver.get(self.url)
            
            # Wait for initial page load
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".title-list-grid__item"))
            )
            
            while len(titles) < max_titles and scroll_count < max_scrolls:
                # Find all title elements
                title_elements = driver.find_elements(By.CSS_SELECTOR, 'div.title-list-grid__item')
                current_count = len(titles)
                
                for element in title_elements[current_count:]:
                    try:
                        # Get title link
                        link_element = WebDriverWait(element, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.title-list-grid__item--link'))
                        )
                        link = link_element.get_attribute('href')
                        
                        # Navigate to title detail page
                        driver_detail.get(link)
                        time.sleep(self.__TIME2SLEEP__)
                        
                        # Extract data
                        for item, css_selector in self.css_selectors.items():
                            if item not in data_result:
                                data_result[item] = []
                            data_result[item].append(",".join(
                                self.get_data(driver_detail, css_selector, attribute='text')
                            ))
                        
                        titles = data_result['title']
                        print(f"Extracted data for title #{len(titles)}: {link}")
                        
                        if len(titles) >= max_titles:
                            break
                            
                    except Exception as e:
                        print(f"Error processing item: {str(e)}")
                
                # Handle scrolling
                if len(titles) == current_count:
                    self.scroll_down(driver)
                    scroll_count += 1
                elif len(titles) < max_titles:
                    self.scroll_down(driver)
                    scroll_count += 1
                
                print(f"Collected {len(titles)} items so far.")
                
            # Create DataFrame
            results_df = pd.DataFrame(data_result)
            self.adjust_data(results_df)
            return results_df
            
        except Exception as e:
            print(f"An error occurred: {e}")
            driver.save_screenshot('justwatch_error.png')
            return pd.DataFrame()
            
        finally:
            driver.quit()
            driver_detail.quit()

    def collect_ranking(self, type, rank_freq="weekly", max_titles=20):
        """
        Collect ranking data from JustWatch.
        
        Args:
            type (str): Type of content to collect rankings for ('movies' or 'tv-shows')
            max_titles (int): Maximum number of titles to collect
            rank_freq (str): Frequency of ranking ('weekly' or 'monthly')
        Raises:
            ValueError: If type is not 'movies' or 'tv-shows'   
            
        Returns:
            pandas.DataFrame: DataFrame containing collected rankings
        """
        driver = webdriver.Chrome(options=self.chrome_options)
        data_result = {
            'title': [],
            'rank': [],
            'rank_change': [],
            'top_rank': [],
            'platforms': [] 
        }
        
        try:
            # Navigate to JustWatch ranking page
            print(f"Accessing JustWatch {type} ranking for {self.country}...")
            
            # Construct the appropriate URL based on content type
            if type == "movies":
                url = f"https://www.justwatch.com/{self.country}/streaming-charts?c={self.country}&ct={rank_freq}"
            elif type == "tv-shows":
                url = f"https://www.justwatch.com/{self.country}/streaming-charts?c={self.country}&ct={rank_freq}&t=shows"
            else:
                raise ValueError("Type must be either 'movies' or 'tv-shows'")
                
            driver.get(url)
            time.sleep(10)
            print(f"Accessing URL: {url}")
            driver.get_screenshot_as_file("screenshot.png")
            # Wait for the page to load
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.list"))
            )
            
            # Collect titles and ranks
            title_elements = driver.find_elements(By.CSS_SELECTOR, "table.list .list__row")
            for element in title_elements[:max_titles]:
                try:
                    rank = self.get_data(element, ".title-ranking-list__rank.title-ranking-list__rank--condensed") or ""
                    rank_change = self.get_data(element, ".arrow-container p") or ""
                    title = self.get_data(element, ".list__row__item__content__title>span") or ""
                    top_rank = self.get_data(element, "td.top-rank") or ""
                    platforms = self.get_data(element, ".offers-display img",  attribute='title')
                    
                    data_result['title'].append(title[0])
                    data_result['rank'].append(rank[0])
                    data_result['rank_change'].append(rank_change[0])
                    data_result['top_rank'].append(top_rank[0])
                    data_result['platforms'].append(platforms)
                    
                except Exception as e:
                    print(f"Error processing element: {str(e)}")
            # Scroll down to load more titles if necessary
            self.scroll_down(driver)
            time.sleep(self.__TIME2SLEEP__)
            # Create DataFrame
            results_df = pd.DataFrame(data_result)
            results_df = self.adjust_data_ranking(results_df)
            return results_df
            
                            
               
        except Exception as e:
            print(f"An error occurred: {e.__class__}.\n {str(e)}")
            driver.save_screenshot('justwatch_ranking_error.png')
            return pd.DataFrame()
        finally:
            driver.quit()
            
    
    def adjust_data(self, df):
        """
        Adjust the DataFrame to ensure data consistency and format.
        Args:
            df (pandas.DataFrame): DataFrame to adjust
        """
        
        # Adjust the DataFrame as needed (e.g., rename columns, change dtypes)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['imdb_score'] = pd.to_numeric(df['imdb_score'], errors='coerce')
        df['title'] = df['title'].str.strip()
        # Use title as original_title if original_title doesn't exist or is empty
        df['original_title'] = df['original_title'].fillna(df['title'])
        df.dropna(subset=['title'], inplace=True)
        df.reset_index(drop=True, inplace=True)

    def adjust_data_ranking(self, df):
        """
        Adjust the ranking DataFrame to ensure data consistency and format.
        
        Args:
            df (pandas.DataFrame): DataFrame to adjust
        """
        # Adjust the DataFrame as needed (e.g., rename columns, change dtypes)
        #df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        df['top_rank'] = pd.to_numeric(df['top_rank'], errors='coerce')
        df['rank_change'] =pd.to_numeric(df['rank_change'], errors='coerce')
        df['rank_change'] = df['rank_change'].fillna(0)
        df['platforms'] = df['platforms'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        df['title'] = df['title'].str.strip()
        df.dropna(subset=['title'])
        df.reset_index(drop=True)
        return df
    
    def save_to_csv(self, df, filename=None):
        """
        Save the collected data to a CSV file.
        
        Args:
            df (pandas.DataFrame): DataFrame to save
            filename (str): Name of the output file
        """
        if filename is None:
            filename = f"justwatch_{self.country}_{self.content_type}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")

#movies_collector = JustWatchCollector(country="us", content_type="movies", headless=False)
#movies_df = movies_collector.collect_ranking(type="movies", rank_freq="weekly", max_titles=20 )
#print(movies_df.head())