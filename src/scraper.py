"""
Module for scraping news feeds from various sources.
"""
import requests
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import time

class NewsScraper:
    """Class to handle scraping news from various RSS feeds."""
    
    def __init__(self):
        """Initialize the NewsScraper with predefined news sources."""
        # Selected reliable news sources based on research
        self.sources = {
            "canada": [
                {"name": "CBC News Canada", "url": "https://www.cbc.ca/cmlink/rss-canada"},
                {"name": "CTV News Canada", "url": "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822284"},
                {"name": "Global News Canada", "url": "https://globalnews.ca/canada/feed/"}
            ],
            "us": [
                {"name": "NPR News", "url": "https://feeds.npr.org/1001/rss.xml"},
                {"name": "CNN US", "url": "http://rss.cnn.com/rss/cnn_us.rss"},
                {"name": "Reuters US", "url": "https://www.reuters.com/rssfeed/us/"}
            ],
            "world": [
                {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
                {"name": "Reuters World", "url": "https://www.reuters.com/rssfeed/world/"},
                {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"}
            ]
        }
        self.timeout = 10  # Request timeout in seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_feed(self, category, source_index=None):
        """
        Fetch news from a specific category and source.
        
        Args:
            category (str): News category ('canada', 'us', or 'world')
            source_index (int, optional): Index of the source to fetch. If None, fetch from all sources.
            
        Returns:
            list: List of articles with title, description, link, and source
        """
        if category not in self.sources:
            logging.error(f"Invalid category: {category}")
            return []
        
        articles = []
        sources_to_fetch = [self.sources[category][source_index]] if source_index is not None else self.sources[category]
        
        for source in sources_to_fetch:
            try:
                response = requests.get(source["url"], headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse the RSS feed
                feed_articles = self._parse_rss(response.content, source["name"])
                articles.extend(feed_articles)
                
                # Add a small delay to be respectful to the servers
                time.sleep(0.5)
                
            except requests.RequestException as e:
                logging.error(f"Error fetching {source['name']}: {str(e)}")
                continue
        
        return articles
    
    def _parse_rss(self, content, source_name):
        """
        Parse RSS content into a list of articles.
        
        Args:
            content (bytes): RSS feed content
            source_name (str): Name of the news source
            
        Returns:
            list: List of article dictionaries
        """
        articles = []
        
        try:
            # First try to parse as XML using ElementTree
            root = ET.fromstring(content)
            
            # Handle different RSS formats
            if root.tag == 'rss':
                # Standard RSS format
                for item in root.findall('.//item'):
                    article = {
                        'title': self._safe_find_text(item, 'title'),
                        'description': self._clean_description(self._safe_find_text(item, 'description')),
                        'link': self._safe_find_text(item, 'link'),
                        'date': self._parse_date(self._safe_find_text(item, 'pubDate')),
                        'source': source_name
                    }
                    articles.append(article)
            elif root.tag.endswith('feed'):
                # Atom feed format
                for entry in root.findall('.//{*}entry'):
                    link = entry.find('.//{*}link')
                    article = {
                        'title': self._safe_find_text(entry, '{*}title'),
                        'description': self._clean_description(self._safe_find_text(entry, '{*}summary')),
                        'link': link.get('href') if link is not None else '',
                        'date': self._parse_date(self._safe_find_text(entry, '{*}updated')),
                        'source': source_name
                    }
                    articles.append(article)
                    
        except ET.ParseError:
            # If XML parsing fails, try with BeautifulSoup
            try:
                soup = BeautifulSoup(content, 'xml')
                
                # Try standard RSS format first
                items = soup.find_all('item')
                if items:
                    for item in items:
                        article = {
                            'title': item.title.text if item.title else 'No title',
                            'description': self._clean_description(item.description.text if item.description else ''),
                            'link': item.link.text if item.link else '',
                            'date': self._parse_date(item.pubDate.text if item.pubDate else ''),
                            'source': source_name
                        }
                        articles.append(article)
                else:
                    # Try Atom format
                    entries = soup.find_all('entry')
                    for entry in entries:
                        link_tag = entry.find('link')
                        link = link_tag.get('href') if link_tag else ''
                        
                        article = {
                            'title': entry.title.text if entry.title else 'No title',
                            'description': self._clean_description(
                                entry.summary.text if entry.summary else (
                                entry.content.text if entry.content else '')
                            ),
                            'link': link,
                            'date': self._parse_date(
                                entry.updated.text if entry.updated else (
                                entry.published.text if entry.published else '')
                            ),
                            'source': source_name
                        }
                        articles.append(article)
            
            except Exception as e:
                logging.error(f"Error parsing feed content for {source_name}: {str(e)}")
        
        return articles
    
    def _safe_find_text(self, element, tag):
        """Safely extract text from an XML element."""
        found = element.find(tag)
        return found.text if found is not None else ''
    
    def _clean_description(self, description):
        """Clean HTML from description and limit length."""
        if not description:
            return ''
            
        # Use BeautifulSoup to remove HTML tags
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Limit description length
        max_length = 200
        if len(text) > max_length:
            return text[:max_length] + '...'
        return text
    
    def _parse_date(self, date_str):
        """Parse date string into a standardized format."""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        try:
            # Try various date formats commonly found in RSS feeds
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 822: Wed, 02 Oct 2002 13:00:00 GMT
                '%a, %d %b %Y %H:%M:%S %Z',  # Wed, 02 Oct 2002 13:00:00 GMT
                '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601: 2002-10-02T13:00:00Z
                '%Y-%m-%dT%H:%M:%SZ',        # 2002-10-02T13:00:00Z
                '%Y-%m-%d %H:%M:%S',         # 2002-10-02 13:00:00
                '%Y-%m-%d',                  # 2002-10-02
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
                    
            # If none of the formats match, return the original string
            return date_str
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_categories(self):
        """Get available news categories."""
        return list(self.sources.keys())
    
    def get_sources_for_category(self, category):
        """Get available sources for a specific category."""
        if category in self.sources:
            return [source["name"] for source in self.sources[category]]
        return []