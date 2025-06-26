import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import pandas as pd
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By     
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleNewsVolumeAnalyzer:
    """
    Classe para analisar o volume de notícias no Google News para tópicos específicos.
    Mantém uma única instância do driver para reutilização.
    """
    
    def __init__(self, debug=False):
        """Inicializa o analisador com configurações do driver."""
        self.driver = None
        self._setup_driver()
        self.debug = debug  # Ativar modo de depuração se necessário
    
    def _setup_driver(self):
        """Configura e inicializa o driver Chrome."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def get_results_count(self, search_url):
        """
        Extrai o número de resultados de uma busca no Google News.
        
        Args:
            search_url (str): URL da busca no Google News
            
        Returns:
            int: Número de resultados encontrados, ou 0 se não conseguir extrair
        """
        try:
            self.driver.get(search_url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "result-stats"))
            )
            
            # Tentar extrair número de resultados
            results_info = self.driver.find_element(By.ID, "result-stats")
            results_text = results_info.text
            
            # Extrair apenas números do texto (ex: "Cerca de 1.234 resultados")
            numbers = re.findall(r'[\d,\.]+', results_text)
            if numbers:
                # Remover pontos/vírgulas e converter para int
                count = int(numbers[0].replace(',', '').replace('.', ''))
                return count
            
            return 0
            
        except Exception as e:
            print(f"Erro ao extrair contagem: {e}")
            if self.debug:
                self.driver.save_screenshot('googlenews_debug.png')
            return 0
    
    def get_daily_results_count(self, topic, start_date, end_date):
        """
        Coleta a quantidade de resultados dia a dia para um tópico específico.
        
        Args:
            topic (str): Tópico a ser pesquisado
            start_date (str): Data inicial no formato 'MM/DD/YYYY'
            end_date (str): Data final no formato 'MM/DD/YYYY'
            
        Returns:
            dict: Dicionário com data como chave e contagem como valor
        """
        # Converter strings de data para objetos datetime
        start = datetime.strptime(start_date, '%m/%d/%Y')
        end = datetime.strptime(end_date, '%m/%d/%Y')
        
        results = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime('%m/%d/%Y')
            
            # Criar URL para busca específica do dia
            #sbd:0 = permite usar resultados repetidos
            search_url = f"https://www.google.com/search?q={topic}&sca_esv=996e5555f717663f&tbs=cdr:1,cd_min:{date_str},cd_max:{date_str},sbd:0&tbm=nws&sxsrf=AE3TifOkB74DjbLFJS9M0T87LgrPvDvXKA:1750394179061&source=lnt&sa=X&ved=2ahUKEwim7om6lv-NAxX8pZUCHcD9AQ8QpwV6BAgDEBk&biw=1536&bih=756&dpr=1.25"
            
            # Obter contagem de resultados para o dia
            count = self.get_results_count(search_url)
            results.append({'date': date_str, 'count': count})
            
            print(f"Data: {date_str} - Resultados: {count}")
            
            # Avançar para o próximo dia
            current_date += timedelta(days=1)
            
            # Pequena pausa para evitar sobrecarga
            time.sleep(1)
        
        return results
    
    def close(self):
        """Fecha o driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Destrutor para garantir que o driver seja fechado."""
        self.close()

class GoogleNewsCollector:
    def __init__(self, language="en-US", country="US", debug=False):
        """
        Initialize the Google News collector with language and country preferences.
        
        Args:
            language (str): Language code (e.g., "en-US", "pt-BR")
            country (str): Country code (e.g., "US", "BR")  
            debug (bool): Whether to enable debug mode for verbose logging

        """
        self.debug = debug
        self.language = language
        self.country = country
        
        # Set language parameters based on inputs
        if language == "pt-BR" and country == "BR":
            self.lang_param = "hl=pt-BR&gl=BR&ceid=BR%3Apt-419"
        else:
            self.lang_param = f"hl={language}&gl={country}&ceid={country}:en"
            
        self.googlenews_analyzer = GoogleNewsVolumeAnalyzer()  # Initialize the volume analyzer
    
    def count_news_by_date(self, topic, start_date, end_date, max_results=None, topic_type=None):
        """
        Count the number of news articles about a specific topic from Google News within a date range.
        
        Args:
            topic (str): The topic to search for
            start_date (str): Start date in the format 'YYYY-MM-DD'
            end_date (str): End date in the format 'YYYY-MM-DD'
            max_results (int, optional): Maximum number of results to return
            
        Returns:
            int: Number of news articles found
        """
        # Validate date format
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') 
        # If topic_type is provided, prepend it to the topic
        if topic_type:
            topic = f"{topic_type} {topic}"
        topic_results = self.googlenews_analyzer.get_daily_results_count(topic, start_dt.strftime('%m/%d/%Y') , end_dt.strftime('%m/%d/%Y'))
        
        return pd.DataFrame(topic_results)
        
    def collect_news_by_date(self, topic, start_date, end_date, max_results=None, topic_type=None):
        """
        Collect news about a specific topic from Google News within a date range.
        Args:
            topic (str): The topic to search for
            start_date (str): Start date in the format 'YYYY-MM-DD'
            end_date (str): End date in the format 'YYYY-MM-DD'
            max_results (int, optional): Maximum number of results to return
        Returns:
            pandas.DataFrame: DataFrame containing news articles
        """
        # Validate date format
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') 

        # If topic_type is provided, prepend it to the topic
        if topic_type:
            topic = f"{topic_type} {topic}"
        # Encode the topic for URL
        encoded_topic = topic.replace(" ", "%20")

        # Initialize an empty DataFrame to store all results
        all_news = []
        
        # Loop through each date in the range 
        for date in pd.date_range(start=start_dt, end=end_dt):
            # Prepare the URL with the topic and language parameters
            # Get 2 days of news for each date
            before_dt = date + timedelta(days=1)  # Add one day to include the end date
            url = f"https://news.google.com/rss/search?q='{encoded_topic}'+after:{date.strftime('%Y-%m-%d')}+before:{before_dt.strftime('%Y-%m-%d')}&{self.lang_param}"
            # Make the request
            response = requests.get(url)
            response.raise_for_status()
            df = self.parse_news(response.content, max_results=max_results)
            logger.info(f"Collected #{len(df)} Google News for topic: {topic} on date range: {date.strftime('%Y-%m-%d')} to {before_dt.strftime('%Y-%m-%d')}")
            all_news.extend(df.to_dict(orient='records'))
            
        
        return pd.DataFrame(all_news)
        
    def collect_news(self, topic, max_results=None):
        """
        Collect news about a specific topic from Google News.
        
        Args:
            topic (str): The topic to search for
            max_results (int, optional): Maximum number of results to return
            
        Returns:
            pandas.DataFrame: DataFrame containing news articles
        """
        logger.info(f"Accessing Google News for topic: {topic} in {self.language} ({self.country})")
        # Prepare the URL with the topic and language parameters
        encoded_topic = topic.replace(" ", "%20")
        url = f"https://news.google.com/rss/search?q='{encoded_topic}'&{self.lang_param}"
        
        # Make the request
        response = requests.get(url)
        response.raise_for_status()
        
        return self.parse_news(response.content, max_results=max_results)
    
    def parse_news(self, content, max_results=None):
        """
        Parse the XML response from Google News and extract relevant information.
        Args:
            response (requests.Response): The response object from the request
            max_results (int, optional): Maximum number of results to return
        Returns:
            pandas.DataFrame: DataFrame containing news articles
        """
        # Parse the XML content
        root = ET.parse(BytesIO(content)).getroot()
        
        # Create lists to store the data
        titles = []
        links = []
        pub_dates = []
        sources = []
        descriptions = []
        
        # Find all item elements (news articles)
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else None
            link = item.find('link').text if item.find('link') is not None else None
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else None
            source = item.find('source').text if item.find('source') is not None else None
            description = item.find('description').text if item.find('description') is not None else None
            
            titles.append(title)
            links.append(link)
            pub_dates.append(pub_date)
            sources.append(source)
            descriptions.append(description)
            
            if max_results and len(titles) >= max_results:
                break
        
        # Create a DataFrame
        news_df = pd.DataFrame({
            'Title': titles,
            'Link': links,
            'Publication Date': pub_dates,
            'Source': sources,
            'Description': descriptions
        })
        
        # Convert 'Publication Date' column to datetime format
        news_df['Publication Date'] = pd.to_datetime(news_df['Publication Date'], 
                                                    format='%a, %d %b %Y %H:%M:%S %Z')
        
        # Sort by publication date (newest first)
        news_df.sort_values(by='Publication Date', ascending=False, inplace=True)
        
        return news_df
    
    def save_to_csv(self, df, filename="google_news_results.csv"):
        """
        Save the news DataFrame to a CSV file.
        
        Args:
            df (pandas.DataFrame): DataFrame to save
            filename (str): Name of the output file
        """
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Results saved to {filename}")
        
        
