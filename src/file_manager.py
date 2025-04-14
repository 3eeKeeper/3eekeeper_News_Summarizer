"""
Module for managing summary files.
"""
import os
import re
import logging
from datetime import datetime
import hashlib

class FileManager:
    """Class to handle file operations for news summaries."""
    
    def __init__(self, summaries_dir="summaries"):
        """
        Initialize the FileManager with summaries directory.
        
        Args:
            summaries_dir (str): Path to the summaries directory
        """
        self.summaries_dir = summaries_dir
        
        # Create the summaries directory if it doesn't exist
        if not os.path.exists(self.summaries_dir):
            os.makedirs(self.summaries_dir)
    
    def generate_filename(self, article):
        """
        Generate a unique filename for an article.
        
        Args:
            article (dict): Article data including title, source, and date
            
        Returns:
            str: A unique filename for the article
        """
        # Generate a unique hash from the article URL
        url_hash = hashlib.md5(article['link'].encode()).hexdigest()[:8]
        
        # Clean the title to make it filename-friendly
        title = re.sub(r'[^\w\s-]', '', article['title'])
        title = re.sub(r'[\s]+', '_', title).strip().lower()
        title = title[:50]  # Limit title length in filename
        
        # Format the date part
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Create the filename
        filename = f"{date_str}_{title}_{url_hash}.txt"
        
        return filename
    
    def summary_exists(self, article):
        """
        Check if a summary for this article already exists.
        
        Args:
            article (dict): Article data including link
            
        Returns:
            tuple: (bool indicating if summary exists, filename if it exists)
        """
        # Get all summary filenames
        all_files = os.listdir(self.summaries_dir)
        
        # Generate URL hash for the article
        url_hash = hashlib.md5(article['link'].encode()).hexdigest()[:8]
        
        # Check if any filename contains this hash
        for filename in all_files:
            if url_hash in filename and filename.endswith('.txt'):
                return True, filename
        
        return False, self.generate_filename(article)
    
    def save_summary(self, article_with_summary):
        """
        Save an article summary to a file.
        
        Args:
            article_with_summary (dict): Article data with summary
            
        Returns:
            str: The path to the saved summary file
        """
        exists, filename = self.summary_exists(article_with_summary)
        
        if exists:
            logging.info(f"Summary already exists: {filename}")
            return os.path.join(self.summaries_dir, filename)
        
        filepath = os.path.join(self.summaries_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write a nicely formatted summary file
                f.write(f"Title: {article_with_summary['title']}\n")
                f.write(f"Source: {article_with_summary['source']}\n")
                f.write(f"Date: {article_with_summary.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n")
                f.write(f"URL: {article_with_summary['link']}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write("SUMMARY:\n\n")
                f.write(article_with_summary['summary'])
                f.write("\n\n" + "="*50 + "\n")
                f.write("\nSummarized using Claude 3 Haiku on ")
                f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            logging.info(f"Summary saved: {filename}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving summary: {str(e)}")
            return None
    
    def get_summary(self, article):
        """
        Retrieve an existing summary if available.
        
        Args:
            article (dict): Article data including link
            
        Returns:
            dict or None: The article data with summary if found, otherwise None
        """
        exists, filename = self.summary_exists(article)
        
        if not exists:
            return None
        
        filepath = os.path.join(self.summaries_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract the summary part between the markers
                summary_match = re.search(r'SUMMARY:\n\n(.*?)(?:\n\n={50})', content, re.DOTALL)
                
                if summary_match:
                    summary = summary_match.group(1).strip()
                    return {**article, 'summary': summary}
                else:
                    return None
                    
        except Exception as e:
            logging.error(f"Error reading summary: {str(e)}")
            return None
    
    def list_recent_summaries(self, limit=10):
        """
        List the most recent summary files.
        
        Args:
            limit (int): Maximum number of summaries to return
            
        Returns:
            list: List of summary filenames sorted by date
        """
        try:
            all_files = os.listdir(self.summaries_dir)
            
            # Filter for .txt files
            summary_files = [f for f in all_files if f.endswith('.txt')]
            
            # Sort by date (assuming filename starts with date in format YYYYMMDD)
            sorted_files = sorted(summary_files, reverse=True)
            
            return sorted_files[:limit]
            
        except Exception as e:
            logging.error(f"Error listing summaries: {str(e)}")
            return []