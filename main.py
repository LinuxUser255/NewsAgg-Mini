#!/usr/bin/env python3
"""
NewsAgg-Mini: A simplified news aggregator
===========================================

This is a beginner-friendly, scaled-down version of NewsAggregator.
It fetches news from RSS feeds, classifies them into topics using keywords,
and generates simple text reports.

ARCHITECTURE OVERVIEW:
----------------------
1. RSS Fetching: Downloads news articles from RSS/Atom feeds
2. Classification: Groups articles into topics based on keywords  
3. Storage: Saves articles to JSON files (simple persistence)
4. Reporting: Generates markdown reports with top articles per topic

HOW TO BUILD IT OUT:
--------------------
1. Start Simple: Get RSS fetching working first
2. Add Topics: Implement keyword-based classification
3. Persist Data: Save articles to avoid re-fetching
4. Add Reports: Create markdown summaries
5. Extend: Add more sources, better classification, web scraping, etc.

DEPENDENCIES TO INSTALL:
------------------------
pip install feedparser requests pyyaml

USAGE:
------
python main.py --help
python main.py --config config.yaml
python main.py --topics tech,ai,security

"""

import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

# External dependencies
try:
    import feedparser
    import yaml
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install feedparser pyyaml")
    exit(1)


# ============================================================================
# DATA MODELS
# ============================================================================

class Article:
    """Simple article data model"""
    def __init__(self, title: str, url: str, source: str, 
                 summary: Optional[str] = None, published: Optional[str] = None):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary or ""
        self.published = published or datetime.now(timezone.utc).isoformat()
        self.topics: List[str] = []
        
        # Generate unique ID from content
        content = f"{source}|{url}|{title}"
        self.id = hashlib.md5(content.encode()).hexdigest()[:12]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'summary': self.summary,
            'published': self.published,
            'topics': self.topics
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        art = cls(
            title=data['title'],
            url=data['url'],
            source=data['source'],
            summary=data.get('summary'),
            published=data.get('published')
        )
        art.id = data.get('id', art.id)
        art.topics = data.get('topics', [])
        return art


class Topic:
    """Topic configuration with keywords"""
    def __init__(self, name: str, keywords: List[str], 
                 exclude_words: Optional[List[str]] = None):
        self.name = name
        self.keywords = [k.lower() for k in keywords]
        self.exclude_words = [k.lower() for k in (exclude_words or [])]
    
    def matches(self, text: str) -> bool:
        """Check if text matches this topic's keywords"""
        text_lower = text.lower()
        
        # Check exclude words first
        if any(word in text_lower for word in self.exclude_words):
            return False
        
        # Check include keywords
        return any(keyword in text_lower for keyword in self.keywords)


# ============================================================================
# RSS FETCHER
# ============================================================================

class RSSFetcher:
    """Fetches articles from RSS/Atom feeds"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, feed_url: str, source_name: Optional[str] = None) -> List[Article]:
        """
        Fetch articles from an RSS feed
        
        Args:
            feed_url: URL of the RSS/Atom feed
            source_name: Optional name for the source
            
        Returns:
            List of Article objects
        """
        if not source_name:
            # Extract domain as source name
            source_name = urlparse(feed_url).netloc
        
        self.logger.info(f"Fetching RSS: {source_name} ({feed_url})")
        
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            self.logger.error(f"Failed to fetch {feed_url}: {e}")
            return []
        
        articles = []
        for entry in feed.entries[:20]:  # Limit to 20 articles per feed
            try:
                # Extract basic info
                title = entry.get('title', 'No Title')
                url = entry.get('link', entry.get('id', ''))
                
                # Try to get summary/description
                summary = (entry.get('summary') or 
                          entry.get('description') or 
                          '')[:500]  # Limit summary length
                
                # Try to parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    published = dt.isoformat()
                
                article = Article(
                    title=title,
                    url=url,
                    source=source_name,
                    summary=summary,
                    published=published
                )
                articles.append(article)
                
            except Exception as e:
                self.logger.warning(f"Skipping article due to error: {e}")
                continue
        
        self.logger.info(f"Fetched {len(articles)} articles from {source_name}")
        return articles


# ============================================================================
# CLASSIFIER
# ============================================================================

class Classifier:
    """Classifies articles into topics based on keywords"""
    
    def __init__(self, topics: List[Topic]):
        self.topics = topics
        self.logger = logging.getLogger(__name__)
    
    def classify(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """
        Classify articles into topics
        
        Returns:
            Dictionary mapping topic names to lists of articles
        """
        result = {topic.name: [] for topic in self.topics}
        result['uncategorized'] = []
        
        for article in articles:
            # Create searchable text from title and summary
            search_text = f"{article.title} {article.summary}"
            
            matched = False
            for topic in self.topics:
                if topic.matches(search_text):
                    result[topic.name].append(article)
                    article.topics.append(topic.name)
                    matched = True
            
            if not matched:
                result['uncategorized'].append(article)
        
        # Remove empty topics
        result = {k: v for k, v in result.items() if v}
        
        # Log classification results
        for topic, arts in result.items():
            self.logger.info(f"Topic '{topic}': {len(arts)} articles")
        
        return result


# ============================================================================
# STORAGE
# ============================================================================

class Storage:
    """Simple JSON-based storage for articles"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_articles(self, articles: List[Article], topic: str = "all"):
        """Save articles to a JSON file"""
        file_path = self.data_dir / f"{topic}_articles.json"
        
        # Load existing articles if file exists
        existing_ids = set()
        existing_articles = []
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                    existing_articles = [Article.from_dict(d) for d in existing_data]
                    existing_ids = {a.id for a in existing_articles}
            except Exception as e:
                self.logger.warning(f"Could not load existing articles: {e}")
        
        # Add only new articles
        new_articles = [a for a in articles if a.id not in existing_ids]
        all_articles = existing_articles + new_articles
        
        # Keep only the most recent 100 articles
        all_articles.sort(key=lambda a: a.published or "", reverse=True)
        all_articles = all_articles[:100]
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump([a.to_dict() for a in all_articles], f, indent=2)
        
        self.logger.info(f"Saved {len(new_articles)} new articles to {file_path}")
        return len(new_articles)
    
    def load_articles(self, topic: str = "all") -> List[Article]:
        """Load articles from storage"""
        file_path = self.data_dir / f"{topic}_articles.json"
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [Article.from_dict(d) for d in data]
        except Exception as e:
            self.logger.error(f"Could not load articles: {e}")
            return []


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates markdown reports from classified articles"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def generate(self, classified: Dict[str, List[Article]], top_n: int = 10):
        """Generate markdown report for classified articles"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"news_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            # Write header
            f.write("# News Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write summary
            total = sum(len(arts) for arts in classified.values())
            f.write(f"**Total Articles:** {total}\n")
            f.write(f"**Topics:** {', '.join(classified.keys())}\n\n")
            
            # Write each topic
            for topic, articles in classified.items():
                f.write(f"## {topic.title()}\n")
                f.write(f"*{len(articles)} articles*\n\n")
                
                # Sort by date and take top N
                articles.sort(key=lambda a: a.published or "", reverse=True)
                
                for i, article in enumerate(articles[:top_n], 1):
                    f.write(f"### {i}. {article.title}\n")
                    f.write(f"**Source:** {article.source}\n")
                    f.write(f"**Link:** {article.url}\n")
                    
                    if article.published:
                        f.write(f"**Published:** {article.published[:10]}\n")
                    
                    if article.summary:
                        f.write(f"\n{article.summary[:200]}...\n")
                    
                    f.write("\n---\n\n")
        
        self.logger.info(f"Report generated: {report_path}")
        print(f"\n📄 Report saved to: {report_path}")
        return report_path


# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config(config_file: Optional[str] = None) -> dict:
    """Load configuration from YAML file or return defaults"""
    
    default_config = {
        'feeds': [
            {
                'url': 'https://hnrss.org/frontpage',
                'name': 'Hacker News'
            },
            {
                'url': 'https://feeds.arstechnica.com/arstechnica/index',
                'name': 'Ars Technica'
            }
        ],
        'topics': [
            {
                'name': 'AI',
                'keywords': ['ai', 'artificial intelligence', 'machine learning', 
                           'gpt', 'llm', 'neural', 'deep learning'],
                'exclude': []
            },
            {
                'name': 'Security',
                'keywords': ['security', 'vulnerability', 'breach', 'hack', 
                           'cyber', 'malware', 'ransomware'],
                'exclude': []
            },
            {
                'name': 'Programming',
                'keywords': ['python', 'javascript', 'rust', 'golang', 'java',
                           'programming', 'coding', 'developer', 'github'],
                'exclude': []
            }
        ]
    }
    
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.warning(f"Could not load config file: {e}")
    
    return default_config


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    return logging.getLogger(__name__)


def main():
    """Main application entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="NewsAgg-Mini: A simple news aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python main.py                    # Run with defaults
  python main.py --config my.yaml   # Use custom config
  python main.py --topics ai,tech   # Override topics
  python main.py --top-n 5          # Show only top 5 per topic
        """
    )
    
    parser.add_argument('--config', help='Config YAML file')
    parser.add_argument('--topics', help='Comma-separated topic names to track')
    parser.add_argument('--top-n', type=int, default=10, 
                       help='Number of articles per topic in report')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting NewsAgg-Mini")
    
    # Load configuration
    config = load_config(args.config)
    
    # Create topics from config or command line
    if args.topics:
        # Simple topic creation from command line
        topic_names = [t.strip() for t in args.topics.split(',')]
        topics = [Topic(name, [name.lower()]) for name in topic_names]
    else:
        topics = [
            Topic(
                name=t['name'],
                keywords=t['keywords'],
                exclude_words=t.get('exclude', [])
            )
            for t in config['topics']
        ]
    
    # Initialize components
    fetcher = RSSFetcher()
    classifier = Classifier(topics)
    storage = Storage()
    reporter = ReportGenerator()
    
    # Fetch articles from all feeds
    all_articles = []
    for feed in config['feeds']:
        articles = fetcher.fetch(feed['url'], feed.get('name'))
        all_articles.extend(articles)
    
    logger.info(f"Total articles fetched: {len(all_articles)}")
    
    if not all_articles:
        logger.warning("No articles fetched. Check your internet connection and feed URLs.")
        return 1
    
    # Classify articles
    classified = classifier.classify(all_articles)
    
    # Save articles
    storage.save_articles(all_articles, topic="all")
    for topic, articles in classified.items():
        if topic != 'uncategorized':
            storage.save_articles(articles, topic=topic)
    
    # Generate report
    reporter.generate(classified, top_n=args.top_n)
    
    # Print summary
    print("\n" + "="*50)
    print("📰 NEWS AGGREGATION COMPLETE")
    print("="*50)
    for topic, articles in classified.items():
        print(f"  {topic}: {len(articles)} articles")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    exit(main())


# ============================================================================
# EXTENSION IDEAS
# ============================================================================
"""
HOW TO EXTEND THIS PROJECT:
---------------------------

1. ADD MORE SOURCES:
   - Add web scraping with BeautifulSoup
   - Support JSON APIs (Reddit, NewsAPI, etc.)
   - Add social media feeds (Twitter, Mastodon)

2. IMPROVE CLASSIFICATION:
   - Use ML models (spaCy, transformers)
   - Add sentiment analysis
   - Implement source reputation scoring

3. BETTER STORAGE:
   - Use SQLite database instead of JSON
   - Add full-text search
   - Implement deduplication

4. ENHANCED REPORTS:
   - Generate HTML reports with CSS
   - Add charts and visualizations
   - Create daily/weekly digests

5. AUTOMATION:
   - Add scheduling with cron/Task Scheduler
   - Implement email notifications
   - Create a web dashboard

6. PUBLISHING:
   - Post to Telegram/Discord
   - Tweet summaries
   - Generate RSS feeds

SUGGESTED LEARNING PATH:
------------------------
1. Understand the current code flow
2. Add one new RSS feed and test
3. Create a custom topic with keywords
4. Modify the report format
5. Add a new feature from the list above

USEFUL RESOURCES:
----------------
- feedparser docs: https://feedparser.readthedocs.io/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- Python JSON: https://docs.python.org/3/library/json.html
- SQLite: https://docs.python.org/3/library/sqlite3.html
"""

