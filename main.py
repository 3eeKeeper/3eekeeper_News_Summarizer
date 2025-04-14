#!/usr/bin/env python3
"""
Main module for the News Summarizer application.
"""
import os
import logging
import sys
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_summarizer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import application modules
from src.scraper import NewsScraper
from src.summarizer import ArticleSummarizer
from src.file_manager import FileManager
from src.console import ConsoleInterface

def save_api_key(api_key):
    """Save the API key to the .env file."""
    try:
        # Get the absolute path to the .env file for better logging
        env_path = os.path.abspath('.env')
        logging.info(f"Saving API key to {env_path}")
        
        with open('.env', 'w') as f:
            f.write(f"CLAUDE_API_KEY={api_key}")
            
        # Verify the key was saved correctly
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
                # More secure verification that doesn't potentially expose the key in logs
                if env_content.startswith("CLAUDE_API_KEY=") and len(env_content) > 15:
                    logging.info("API key was saved successfully to .env file")
                    return True
                else:
                    logging.warning("API key may not have been saved correctly to .env file")
                    return False
        else:
            logging.error(".env file was not created")
            return False
    except Exception as e:
        logging.error(f"Failed to save API key: {str(e)}")
        return False

def main():
    """Main function to run the news summarizer application."""
    # Check if .env file exists
    env_exists = os.path.exists('.env')
    
    # Force reload environment variables if .env exists
    if env_exists:
        logging.info("Loading environment variables from .env file")
        with open('.env', 'r') as f:
            env_content = f.read()
            logging.info(f"Env file content length: {len(env_content)} characters")
    else:
        logging.warning(".env file does not exist. Will prompt for API key.")
    
    # Load environment variables (will be empty if .env doesn't exist)
    load_dotenv(override=True)
    
    # Verify API key is loaded
    api_key = os.getenv('CLAUDE_API_KEY')
    if api_key:
        logging.info("Claude API key found in environment")
    else:
        logging.warning("API key not found in environment")
    
    # Initialize components
    console = ConsoleInterface()
    file_manager = FileManager()
    summarizer = ArticleSummarizer()
    scraper = NewsScraper()
    
    # Check if Claude API key is set or .env file is missing
    if not env_exists or not summarizer.is_api_key_set():
        console.display_header()
        print("Claude API key not found." if env_exists else "No .env file found.")
        api_key = console.prompt_api_key()
        if api_key:
            if save_api_key(api_key):
                console.display_success("API key saved successfully!")
                # Reinitialize summarizer with the new API key
                load_dotenv(override=True)
                summarizer = ArticleSummarizer()
            else:
                console.display_error("Failed to save API key.")
    
    # Display welcome message
    console.display_welcome()
    
    # Main application loop
    running = True
    while running:
        console.display_header()
        
        # Main menu
        main_options = [
            "Browse Canada News",
            "Browse US News",
            "Browse World News",
            "Exit"
        ]
        
        main_choice = console.display_menu(main_options)
        
        if main_choice == 3:  # Exit
            if console.confirm_exit():
                running = False
                console.display_success("Thank you for using 3eekeeper News Summarizer!")
                continue
            else:
                continue
        
        # Map menu choice to category
        categories = ["canada", "us", "world"]
        selected_category = categories[main_choice]
        
        # Fetch articles for the selected category
        console.display_loading(f"Fetching {selected_category.capitalize()} news... ")
        articles = scraper.get_feed(selected_category)
        console.finish_loading(f"Found {len(articles)} articles.")
        
        # Display articles
        page = 0
        browsing_articles = True
        
        while browsing_articles:
            article_choice = console.display_articles(articles, page)
            
            if article_choice == -1:  # Previous page
                page = max(0, page - 1)
            elif article_choice == -2:  # Next page
                page = page + 1
            elif article_choice == -3:  # Back to main menu
                browsing_articles = False
            else:  # Selected an article
                selected_article = articles[article_choice]
                
                # Check if summary already exists
                existing_summary = file_manager.get_summary(selected_article)
                
                if existing_summary:
                    # Display existing summary
                    console.display_summary(existing_summary)
                else:
                    # Generate and save summary
                    console.display_loading("Generating summary... ")
                    article_with_summary = summarizer.summarize(selected_article)
                    console.finish_loading("Summary generated!")
                    
                    # Save to file only if there's a valid summary (not an error)
                    summary = article_with_summary.get('summary', '')
                    if 'summary' in article_with_summary and not summary.startswith('Error') and not summary.startswith('Cannot summarize:'):
                        file_path = file_manager.save_summary(article_with_summary)
                        if file_path:
                            logging.info(f"Summary saved to {file_path}")
                    else:
                        logging.warning(f"No valid summary generated for article: {selected_article['title']}")
                    
                    # Display summary
                    console.display_summary(article_with_summary)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)