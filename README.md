# 3eekeeper News Summarizer

A console-based news application that scrapes news feeds from reliable sources, summarizes articles using Claude 3 Haiku, and manages article summaries.

## Features

- Scrapes news from reliable Canadian, US, and World news sources
- Summarizes articles using Claude 3 Haiku AI
- Attractive and colorful console interface
- Saves summaries for offline reading
- Error handling for network issues and API failures

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd news-summarizer
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your Claude API key:
   - Copy the `.env.template` file to a new file named `.env`
   ```
   cp .env.template .env
   ```
   - Edit the `.env` file and add your Claude API key: `CLAUDE_API_KEY=your_api_key_here`
   - You can obtain an API key from [Anthropic's Console](https://console.anthropic.com/)
   - Alternatively, you can enter your API key when prompted by the application

## Usage

Run the application:
```
python main.py
```

The application will:
1. Display a welcome screen with instructions
2. Present a menu of news categories (Canada, US, World)
3. Show a list of articles for the selected category
4. Allow you to select an article to see its summary
5. Display the summary with a link to the original article

## News Sources

The application scrapes news from the following reliable sources:

### Canada News:
- CBC News Canada
- CTV News Canada
- Global News Canada

### US News:
- NPR News
- CNN US
- Reuters US

### World News:
- BBC World
- Reuters World
- Al Jazeera

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- colorama
- python-dotenv
- anthropic

## Security Note

This application requires an API key for Claude AI. Never share your API key publicly or commit it to version control. The `.env` file containing your API key is included in `.gitignore` to prevent accidental exposure.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.