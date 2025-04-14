"""
Module for handling the console interface of the news application.
"""
import os
import sys
import time
import logging
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class ConsoleInterface:
    """Class to handle the console interface for the news application."""
    
    def __init__(self):
        """Initialize the ConsoleInterface."""
        # Define color schemes
        self.colors = {
            'title': Fore.CYAN + Style.BRIGHT,
            'menu_header': Fore.GREEN + Style.BRIGHT,
            'menu_item': Fore.WHITE,
            'selected': Fore.BLACK + Back.WHITE,
            'error': Fore.RED + Style.BRIGHT,
            'success': Fore.GREEN,
            'info': Fore.BLUE,
            'highlight': Fore.YELLOW + Style.BRIGHT,
            'link': Fore.MAGENTA + Style.BRIGHT,
            'prompt': Fore.CYAN,
            'separator': Fore.WHITE + Style.DIM
        }
        
        # Screen dimensions
        self.width = 80
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display the application header."""
        self.clear_screen()
        print(self.colors['title'] + "╔" + "═" * (self.width - 2) + "╗")
        print(self.colors['title'] + "║" + " " * (self.width - 2) + "║")
        print(self.colors['title'] + "║" + " 3EEKEEPER NEWS SUMMARIZER ".center(self.width - 2) + "║")
        print(self.colors['title'] + "║" + " Powered by Claude 3 Haiku ".center(self.width - 2) + "║")
        print(self.colors['title'] + "║" + " " * (self.width - 2) + "║")
        print(self.colors['title'] + "╚" + "═" * (self.width - 2) + "╝")
        print()
    
    def display_menu(self, options):
        """
        Display a menu with options.
        
        Args:
            options (list): List of menu options
            
        Returns:
            int: The selected option index
        """
        print(self.colors['menu_header'] + "Select an option:")
        
        for i, option in enumerate(options, 1):
            print(f"{self.colors['menu_item']}{i}. {option}")
        
        print()
        
        while True:
            try:
                choice = input(self.colors['prompt'] + "Enter your choice (1-" + str(len(options)) + "): ")
                choice = int(choice)
                
                if 1 <= choice <= len(options):
                    return choice - 1
                else:
                    print(self.colors['error'] + "Invalid choice. Please enter a number between 1 and " + str(len(options)) + ".")
            except ValueError:
                print(self.colors['error'] + "Please enter a valid number.")
    
    def display_articles(self, articles, page=0, per_page=10):
        """
        Display a list of articles with pagination.
        
        Args:
            articles (list): List of article dictionaries
            page (int): Current page number (0-indexed)
            per_page (int): Number of articles per page
            
        Returns:
            int: Selected article index or -1 for previous page, -2 for next page, -3 for back to menu
        """
        total_articles = len(articles)
        total_pages = max(1, (total_articles + per_page - 1) // per_page)
        
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, total_articles)
        
        self.clear_screen()
        self.display_header()
        
        if total_articles == 0:
            print(self.colors['error'] + "No articles found.")
            input(self.colors['prompt'] + "Press Enter to return to the main menu...")
            return -3
        
        print(self.colors['menu_header'] + f"Articles - Page {page + 1} of {total_pages}")
        print(self.colors['separator'] + "─" * self.width)
        
        for i, article in enumerate(articles[start_idx:end_idx], 1):
            print(f"{self.colors['menu_item']}{i}. {article['title']}")
            print(f"   {self.colors['info']}{article['source']} - {article.get('date', 'No date')}")
            print(f"   {self.colors['info']}{article.get('description', '')}")
            print(self.colors['separator'] + "─" * self.width)
        
        print()
        options = []
        
        if page > 0:
            options.append("Previous page")
        
        if page < total_pages - 1:
            options.append("Next page")
            
        options.append("Back to main menu")
        
        print(self.colors['menu_header'] + "Options:")
        option_offset = 0
        
        for i, option in enumerate(options, 1):
            print(f"{self.colors['menu_item']}{i + end_idx - start_idx}. {option}")
            
        print()
        
        while True:
            try:
                choice = input(self.colors['prompt'] + f"Select an article or option (1-{end_idx - start_idx + len(options)}): ")
                choice = int(choice)
                
                if 1 <= choice <= end_idx - start_idx:
                    # Selected an article
                    return start_idx + choice - 1
                elif choice == end_idx - start_idx + 1 and page > 0:
                    # Previous page
                    return -1
                elif choice == end_idx - start_idx + 1 and page == 0 and page < total_pages - 1:
                    # Next page (when on first page and no previous page option)
                    return -2
                elif choice == end_idx - start_idx + 2 and page > 0 and page < total_pages - 1:
                    # Next page (when not on first page)
                    return -2
                elif choice == end_idx - start_idx + 1 + len(options) - 1:
                    # Back to main menu (always the last option)
                    return -3
                else:
                    print(self.colors['error'] + f"Invalid choice. Please enter a number between 1 and {end_idx - start_idx + len(options)}.")
            except ValueError:
                print(self.colors['error'] + "Please enter a valid number.")
    
    def display_summary(self, article_with_summary):
        """
        Display an article summary.
        
        Args:
            article_with_summary (dict): Article data with summary
        """
        self.clear_screen()
        self.display_header()
        
        if 'summary' not in article_with_summary:
            print(self.colors['error'] + "No summary available for this article.")
            input(self.colors['prompt'] + "Press Enter to return...")
            return
        
        # Display article metadata with improved spacing and formatting
        print(self.colors['highlight'] + "╔" + "═" * (self.width - 2) + "╗")
        print(self.colors['highlight'] + "║" + article_with_summary['title'].center(self.width - 2) + "║")
        print(self.colors['highlight'] + "╚" + "═" * (self.width - 2) + "╝")
        print()
        print(self.colors['info'] + f"Source: {article_with_summary['source']}")
        print(self.colors['info'] + f"Date: {article_with_summary.get('date', 'No date')}")
        print(self.colors['link'] + f"Link: {article_with_summary['link']}")
        print()
        
        # Display summary with improved formatting
        print(self.colors['menu_header'] + "╔" + "═" * (self.width - 2) + "╗")
        print(self.colors['menu_header'] + "║" + " SUMMARY ".center(self.width - 2) + "║")
        print(self.colors['menu_header'] + "╚" + "═" * (self.width - 2) + "╝")
        print()
        
        # Process the summary text
        summary = article_with_summary['summary']
        
        # Split into paragraphs (assuming paragraphs are separated with blank lines or start with "Paragraph")
        if "Paragraph" in summary:
            paragraphs = []
            current_paragraph = ""
            for line in summary.split('\n'):
                if line.strip().startswith("Paragraph"):
                    if current_paragraph:
                        paragraphs.append(current_paragraph.strip())
                    current_paragraph = line.split(":", 1)[1] if ":" in line else line
                else:
                    current_paragraph += " " + line.strip() if current_paragraph and line.strip() else line.strip()
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
        else:
            # Try to split by empty lines or other common paragraph separators
            paragraphs = [p.strip() for p in summary.split('\n\n') if p.strip()]
            if len(paragraphs) == 1:
                # Maybe it's just one big paragraph, try to split it more intelligently
                text = paragraphs[0]
                if "Here is a" in text and "paragraph summary" in text.lower():
                    # Remove the introductory text
                    text = text.split(":", 1)[1].strip() if ":" in text else text
                # If we just have one paragraph, try to identify logical breaks
                paragraphs = []
                current_paragraph = ""
                for sentence in text.split('. '):
                    if len(current_paragraph) > 250:  # arbitrary length for paragraph break
                        paragraphs.append(current_paragraph.strip() + '.')
                        current_paragraph = sentence
                    else:
                        current_paragraph += '. ' + sentence if current_paragraph else sentence
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
        
        # Display each paragraph with wrapping, spacing, and numbering
        for i, paragraph in enumerate(paragraphs, 1):
            # Display paragraph number and divider
            print(f"{self.colors['menu_header']}■ Paragraph {i} {self.colors['separator']}" + "─" * (self.width - 15))
            print()
            
            # Word wrap the paragraph
            words = paragraph.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= self.width:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Print lines with a slight indent
            for line in lines:
                print("  " + line)
            
            # Add space between paragraphs
            print()
            print()
        
        print(self.colors['separator'] + "═" * self.width)
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.colors['info']}Summarized using Claude 3 Haiku on {currentTime}")
        print(self.colors['separator'] + "═" * self.width)
        print()
        input(self.colors['prompt'] + "Press Enter to return...")
    
    def display_error(self, message):
        """
        Display an error message.
        
        Args:
            message (str): The error message to display
        """
        print(self.colors['error'] + f"ERROR: {message}")
        time.sleep(2)
    
    def display_loading(self, message="Loading..."):
        """
        Display a loading message.
        
        Args:
            message (str): The loading message to display
        """
        print(self.colors['info'] + message, end='', flush=True)
    
    def update_loading(self, message=""):
        """
        Update the loading message.
        
        Args:
            message (str): The loading message to display
        """
        print(self.colors['info'] + message, end='', flush=True)
    
    def finish_loading(self, message="Done!"):
        """
        Finish the loading display.
        
        Args:
            message (str): The completion message to display
        """
        print(self.colors['success'] + message)
        time.sleep(0.5)
    
    def display_success(self, message):
        """
        Display a success message.
        
        Args:
            message (str): The success message to display
        """
        print(self.colors['success'] + message)
        time.sleep(1)
    
    def display_welcome(self):
        """Display a welcome message and basic instructions."""
        self.display_header()
        print(self.colors['menu_header'] + "Welcome to the 3eekeeper News Summarizer!")
        print()
        print("This application allows you to browse and summarize news articles from various sources.")
        print("Articles are summarized using Claude 3 Haiku when you first view them.")
        print("Summaries are saved locally for faster access in the future.")
        print()
        print(self.colors['highlight'] + "How to use:")
        print("1. Select a news category (Canada, US, or World)")
        print("2. Browse the list of articles")
        print("3. Select an article to see its summary")
        print("4. Follow the link to read the full article if interested")
        print()
        input(self.colors['prompt'] + "Press Enter to continue...")
    
    def confirm_exit(self):
        """
        Confirm if the user wants to exit.
        
        Returns:
            bool: True if the user confirms exit, False otherwise
        """
        while True:
            choice = input(self.colors['prompt'] + "Are you sure you want to exit? (y/n): ").lower()
            if choice in ('y', 'yes'):
                return True
            elif choice in ('n', 'no'):
                return False
            else:
                print(self.colors['error'] + "Please enter 'y' or 'n'.")
    
    def prompt_api_key(self):
        """
        Prompt the user to enter their Claude API key.
        
        Returns:
            str: The entered API key
        """
        print(self.colors['highlight'] + "Claude API Key Required")
        print("To summarize articles, you need to provide a Claude API key.")
        print("You can get one from https://console.anthropic.com/")
        print()
        print(self.colors['info'] + "Your API key will be saved to a local .env file for future use.")
        print(self.colors['info'] + "This key will not be shared or uploaded to any external service.")
        print()
        api_key = input(self.colors['prompt'] + "Enter your Claude API key: ").strip()
        
        # Validate that the input isn't empty
        while not api_key:
            print(self.colors['error'] + "API key cannot be empty.")
            api_key = input(self.colors['prompt'] + "Please enter your Claude API key: ").strip()
            
        return api_key