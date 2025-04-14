"""
Module for summarizing news articles using Claude 3 Haiku API.
"""
import os
import logging
import requests
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Try importing Anthropic for API type definitions only
try:
    from anthropic import AuthenticationError, APIError, APIConnectionError
except ImportError:
    # Define fallback exception classes if Anthropic can't be imported
    class AuthenticationError(Exception): pass
    class APIError(Exception): pass
    class APIConnectionError(Exception): pass

class ArticleSummarizer:
    """Class to handle article summarization using Claude 3 Haiku."""
    
    def __init__(self):
        """Initialize the ArticleSummarizer with Claude API."""
        # Get API key from environment variables
        self.api_key = os.getenv('CLAUDE_API_KEY')
        
        if not self.api_key:
            logging.warning("Claude API key not found in environment variables.")
        else:
            # Just log that the API key is set, without revealing any part of it
            logging.info("Claude API key is set")
        
        # No client initialization - we'll use direct API calls only
        self.client_initialized = bool(self.api_key)
        self.max_tokens = 1000
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def summarize(self, article_data):
        """
        Summarize an article using Claude 3 Haiku via direct API calls.
        
        Args:
            article_data (dict): A dictionary containing article information
                                 (title, link, description, etc.)
            
        Returns:
            dict: The original article data with an added 'summary' field
        """
        if not self.client_initialized:
            return {**article_data, 'summary': "Cannot summarize: Claude API key not set."}
        
        try:
            # Fetch the full article content
            content = self.fetch_article_content(article_data['link'])
            
            # If content is too short, it's likely we failed to extract it properly
            if len(content) < 100:
                content = article_data.get('description', 'No content available.')
                
            # Create the prompt for Claude
            prompt = f"""
            Please summarize the following news article in 3-4 concise paragraphs. Maintain the factual accuracy and important details.
            
            Title: {article_data['title']}
            Source: {article_data['source']}
            
            Article Content:
            {content}
            
            Summary:
            """
            
            # Make direct API call to Claude
            logging.info("Making direct API call to Claude...")
            
            # Define headers for direct API call
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # Request body
            request_data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": self.max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Make direct API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_data,
                timeout=15
            )
            
            logging.info(f"API response status: {response.status_code}")
            
            # If successful, parse and return the response
            if response.status_code == 200:
                response_data = response.json()
                if "content" in response_data and len(response_data["content"]) > 0:
                    summary = response_data["content"][0]["text"]
                    logging.info(f"Successfully generated summary via direct API call")
                    return {**article_data, 'summary': summary}
                else:
                    error_msg = "No content in response"
                    logging.error(error_msg)
                    return {**article_data, 'summary': f"Error generating summary: {error_msg}"}
            else:
                # Try with alternative auth header format
                logging.info("Trying alternative authentication format...")
                alt_headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                
                alt_response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=alt_headers,
                    json=request_data,
                    timeout=15
                )
                
                logging.info(f"Alternative API response status: {alt_response.status_code}")
                
                if alt_response.status_code == 200:
                    alt_response_data = alt_response.json()
                    if "content" in alt_response_data and len(alt_response_data["content"]) > 0:
                        summary = alt_response_data["content"][0]["text"]
                        logging.info(f"Successfully generated summary via alternative auth method")
                        return {**article_data, 'summary': summary}
                
                # Both attempts failed
                error_detail = response.text[:200] if hasattr(response, 'text') else "Unknown error"
                error_msg = f"API request failed: {response.status_code} - {error_detail}"
                logging.error(error_msg)
                return {**article_data, 'summary': f"Error generating summary: {error_msg}"}
                
        except Exception as e:
            error_msg = f"Error summarizing article: {str(e)}"
            logging.error(error_msg)
            return {**article_data, 'summary': f"Error generating summary: {error_msg}"}
    
    def fetch_article_content(self, url):
        """
        Fetch the content of an article from its URL.
        
        Args:
            url (str): The URL of the article to fetch
            
        Returns:
            str: The text content of the article
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                script.extract()
            
            # Extract text from paragraphs and headings
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'section', 'div.content'])
            
            # If no paragraphs found, try to extract text from the body
            if not paragraphs:
                return soup.get_text(separator='\n\n', strip=True)
            
            # Combine paragraphs
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            return content
            
        except requests.RequestException as e:
            logging.error(f"Error fetching article content: {str(e)}")
            return f"Error fetching article content: {str(e)}"
    
    def is_api_key_set(self):
        """Check if the API key is set."""
        return bool(self.api_key)