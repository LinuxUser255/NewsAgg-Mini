# NewsAgg-Mini 📰

A simplified, beginner-friendly news aggregator that fetches RSS feeds, classifies articles by topic, and generates markdown reports.

## Quick Start

### 1. Install Dependencies
```bash
pip install feedparser pyyaml
```

### 2. Run with Defaults
```bash
python main.py
```

This will:
- Fetch news from Hacker News and Ars Technica
- Classify into AI, Security, and Programming topics
- Save articles to `data/` directory
- Generate a report in `reports/` directory

### 3. Use Custom Configuration
```bash
cp config.example.yaml config.yaml
# Edit config.yaml to add your feeds and topics
python main.py --config config.yaml
```

## Architecture Overview

```
main.py
   │
   ├── RSS Fetcher
   │     └── Fetches articles from RSS/Atom feeds
   │
   ├── Classifier
   │     └── Groups articles by topic using keywords
   │
   ├── Storage
   │     └── Saves articles to JSON files
   │
   └── Report Generator
         └── Creates markdown reports
```

### Core Components

1. **Article Model** - Simple data class for news articles
2. **Topic Model** - Defines topics with include/exclude keywords
3. **RSSFetcher** - Downloads and parses RSS feeds
4. **Classifier** - Matches articles to topics based on keywords
5. **Storage** - Persists articles to JSON (with deduplication)
6. **ReportGenerator** - Creates markdown summaries

## Usage Examples

```bash
# Show help
python main.py --help

# Use custom topics from command line
python main.py --topics ai,linux,security

# Limit articles per topic in report
python main.py --top-n 5

# Debug mode
python main.py --log-level DEBUG
```

## Project Structure

```
NewsAgg-Mini/
├── main.py              # All code in one file (simplified)
├── config.example.yaml  # Example configuration
├── README.md           # This file
├── data/               # Stored articles (created automatically)
│   ├── all_articles.json
│   ├── AI_articles.json
│   └── Security_articles.json
└── reports/            # Generated reports (created automatically)
    └── news_report_YYYYMMDD_HHMMSS.md
```

## How It Works

### 1. Fetching
The fetcher downloads RSS feeds and extracts:
- Title
- URL
- Summary/Description
- Published date
- Source name

### 2. Classification
Articles are classified by:
- Searching title + summary for keywords
- Excluding articles with exclude words
- Supporting multiple topics per article

### 3. Storage
JSON files store:
- Up to 100 most recent articles per topic
- Deduplication by article ID (hash of source+url+title)
- Persistent storage between runs

### 4. Reporting
Markdown reports include:
- Summary statistics
- Top N articles per topic
- Links and summaries
- Publication dates

## Extending the Project

### Beginner Level
1. **Add a new RSS feed** - Edit config.yaml
2. **Create custom topics** - Add keywords for your interests
3. **Modify report format** - Edit the ReportGenerator class
4. **Change storage limits** - Adjust the 100 article limit

### Intermediate Level
1. **Add web scraping** - Use BeautifulSoup for non-RSS sites
2. **Implement scheduling** - Run automatically with cron
3. **Add HTML reports** - Generate styled HTML instead of markdown
4. **Create a simple GUI** - Use tkinter or streamlit

### Advanced Level
1. **Use a database** - Replace JSON with SQLite
2. **Add ML classification** - Use spaCy or transformers
3. **Build a web API** - Flask/FastAPI service
4. **Add publishing** - Post to Telegram, Discord, or Twitter

## Learning Path

1. **Understand the flow**: Read main.py from top to bottom
2. **Experiment**: Try different feeds and topics
3. **Debug**: Use `--log-level DEBUG` to see what's happening
4. **Modify**: Start with small changes (report format, new topics)
5. **Extend**: Pick one feature from the extension ideas

## Key Concepts to Learn

- **RSS/Atom parsing** - How feed readers work
- **Text classification** - Keyword matching basics
- **Data persistence** - JSON file storage
- **Command-line interfaces** - argparse module
- **Logging** - Debugging and monitoring
- **Object-oriented design** - Classes and methods

## Differences from Full NewsAggregator

| Feature | NewsAgg-Mini | Full NewsAggregator |
|---------|--------------|-------------------|
| Code Organization | Single file | Multiple modules |
| Dependencies | Minimal (2) | Many (8+) |
| Storage | JSON files | Multiple formats |
| Classification | Keywords only | Advanced matching |
| Publishing | None | Telegram, X/Twitter |
| Configuration | Simple YAML | Complex nested config |
| Error Handling | Basic | Comprehensive |
| Testing | None | Full test suite |

## Tips for Beginners

1. **Start small** - Get it working before adding features
2. **Use logging** - Add logger.debug() to understand flow
3. **Test incrementally** - Test each change as you make it
4. **Read the errors** - Python errors are usually helpful
5. **Keep backups** - Copy working code before major changes

## Resources

- [feedparser documentation](https://feedparser.readthedocs.io/)
- [Python JSON tutorial](https://realpython.com/python-json/)
- [Python logging guide](https://docs.python.org/3/howto/logging.html)
- [RSS specification](https://www.rssboard.org/rss-specification)

## License

Educational project - feel free to modify and extend!