"""
Utility functions for web scraping and API interactions.
"""
import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_webpage(url: str) -> str:
    """
    Fetch the content of a webpage.
    
    Args:
        url: The URL to fetch
        
    Returns:
        The HTML content of the webpage
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return ""

def extract_trending_topics_from_google_trends(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract trending topics from Google Trends HTML.
    
    Args:
        html_content: HTML content from Google Trends
        
    Returns:
        List of trending topics with title and description
    """
    topics = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        trend_items = soup.select('.feed-item-header')
        
        for item in trend_items[:10]:  # Get top 10 trends
            title_elem = item.select_one('.title')
            description_elem = item.select_one('.summary-text')
            
            if title_elem:
                topic = {
                    "title": title_elem.get_text().strip(),
                    "description": description_elem.get_text().strip() if description_elem else "",
                }
                topics.append(topic)
    except Exception as e:
        logger.error(f"Error parsing Google Trends: {e}")
    
    return topics

def search_web_for_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Search the web for information about a topic.
    
    Args:
        topic: The topic to search for
        
    Returns:
        List of search results with title, url, and snippet
    """
    try:
        # This is a simplified example. In a real application, you would use a search API
        # such as Google Custom Search, Bing Search, or similar.
        search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}"
        html_content = fetch_webpage(search_url)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        search_results = []
        
        # Extract search results (simplified)
        result_elements = soup.select('.g')
        for element in result_elements[:5]:  # Get top 5 results
            title_elem = element.select_one('h3')
            link_elem = element.select_one('a')
            snippet_elem = element.select_one('.VwiC3b')
            
            if title_elem and link_elem and snippet_elem:
                result = {
                    "title": title_elem.get_text().strip(),
                    "url": link_elem.get('href', ''),
                    "snippet": snippet_elem.get_text().strip(),
                }
                search_results.append(result)
                
        return search_results
    except Exception as e:
        logger.error(f"Error searching for {topic}: {e}")
        return []
