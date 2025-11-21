# Incremental Build Example

This shows what the code looks like at each major step of development.

---

## Version 0.1: Hello World (5 min)

```python
#!/usr/bin/env python3

def main():
    print("NewsAgg v0.1 - Hello World")
    return 0

if __name__ == "__main__":
    exit(main())
```

**Test:** `python3 main.py` → Should print "Hello World"

---

## Version 0.2: Data Models (15 min)

```python
#!/usr/bin/env python3
import hashlib

class Article:
    def __init__(self, title, url, source):
        self.title = title
        self.url = url
        self.source = source
        self.id = hashlib.md5(f"{source}|{url}|{title}".encode()).hexdigest()[:12]

def main():
    # Test the model
    article = Article("Test News", "http://example.com", "Example")
    print(f"Created article: {article.title}")
    print(f"Article ID: {article.id}")
    return 0

if __name__ == "__main__":
    exit(main())
```

**Test:** Should print article info with generated ID

---

## Version 0.3: Basic RSS Fetching (45 min)

```python
#!/usr/bin/env python3
import hashlib
import feedparser

class Article:
    def __init__(self, title, url, source):
        self.title = title
        self.url = url
        self.source = source
        self.id = hashlib.md5(f"{source}|{url}|{title}".encode()).hexdigest()[:12]

class RSSFetcher:
    def fetch(self, feed_url, source_name):
        print(f"Fetching from {source_name}...")
        feed = feedparser.parse(feed_url)
        
        articles = []
        for entry in feed.entries[:5]:
            article = Article(
                title=entry.get('title', 'No Title'),
                url=entry.get('link', ''),
                source=source_name
            )
            articles.append(article)
        
        print(f"Fetched {len(articles)} articles")
        return articles

def main():
    fetcher = RSSFetcher()
    articles = fetcher.fetch('https://hnrss.org/frontpage', 'Hacker News')
    
    # Show first 3
    for article in articles[:3]:
        print(f"\n- {article.title}")
        print(f"  {article.url}")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

**Test:** Should fetch and display 5 articles from Hacker News

---

## Version 0.4: Classification (60 min)

```python
#!/usr/bin/env python3
import hashlib
import feedparser

class Article:
    def __init__(self, title, url, source, summary=""):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary
        self.id = hashlib.md5(f"{source}|{url}|{title}".encode()).hexdigest()[:12]

class Topic:
    def __init__(self, name, keywords):
        self.name = name
        self.keywords = [k.lower() for k in keywords]
    
    def matches(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.keywords)

class RSSFetcher:
    def fetch(self, feed_url, source_name):
        print(f"Fetching from {source_name}...")
        feed = feedparser.parse(feed_url)
        
        articles = []
        for entry in feed.entries[:20]:
            article = Article(
                title=entry.get('title', 'No Title'),
                url=entry.get('link', ''),
                source=source_name,
                summary=entry.get('summary', '')[:200]
            )
            articles.append(article)
        
        return articles

class Classifier:
    def __init__(self, topics):
        self.topics = topics
    
    def classify(self, articles):
        result = {t.name: [] for t in self.topics}
        result['uncategorized'] = []
        
        for article in articles:
            text = f"{article.title} {article.summary}"
            matched = False
            
            for topic in self.topics:
                if topic.matches(text):
                    result[topic.name].append(article)
                    matched = True
            
            if not matched:
                result['uncategorized'].append(article)
        
        return result

def main():
    # Setup
    fetcher = RSSFetcher()
    topics = [
        Topic('AI', ['ai', 'machine learning', 'gpt', 'llm']),
        Topic('Security', ['security', 'hack', 'vulnerability']),
    ]
    classifier = Classifier(topics)
    
    # Fetch and classify
    articles = fetcher.fetch('https://hnrss.org/frontpage', 'Hacker News')
    classified = classifier.classify(articles)
    
    # Show results
    for topic, arts in classified.items():
        if arts:
            print(f"\n{topic.upper()}: {len(arts)} articles")
            for art in arts[:2]:
                print(f"  - {art.title}")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

**Test:** Should group articles by topic and display counts

---

## Version 0.5: Storage (90 min)

```python
#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import feedparser

class Article:
    def __init__(self, title, url, source, summary=""):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary
        self.id = hashlib.md5(f"{source}|{url}|{title}".encode()).hexdigest()[:12]
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'summary': self.summary
        }
    
    @classmethod
    def from_dict(cls, data):
        art = cls(
            title=data['title'],
            url=data['url'],
            source=data['source'],
            summary=data.get('summary', '')
        )
        art.id = data['id']
        return art

class Topic:
    def __init__(self, name, keywords):
        self.name = name
        self.keywords = [k.lower() for k in keywords]
    
    def matches(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.keywords)

class RSSFetcher:
    def fetch(self, feed_url, source_name):
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:20]:
            article = Article(
                title=entry.get('title', 'No Title'),
                url=entry.get('link', ''),
                source=source_name,
                summary=entry.get('summary', '')[:200]
            )
            articles.append(article)
        
        return articles

class Classifier:
    def __init__(self, topics):
        self.topics = topics
    
    def classify(self, articles):
        result = {t.name: [] for t in self.topics}
        
        for article in articles:
            text = f"{article.title} {article.summary}"
            
            for topic in self.topics:
                if topic.matches(text):
                    result[topic.name].append(article)
        
        return {k: v for k, v in result.items() if v}  # Remove empty

class Storage:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_articles(self, articles, topic="all"):
        file_path = self.data_dir / f"{topic}_articles.json"
        
        # Load existing
        existing_ids = set()
        existing_articles = []
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
                existing_articles = existing_data
                existing_ids = {a['id'] for a in existing_data}
        
        # Add new ones
        new_count = 0
        for article in articles:
            if article.id not in existing_ids:
                existing_articles.append(article.to_dict())
                new_count += 1
        
        # Save
        with open(file_path, 'w') as f:
            json.dump(existing_articles, f, indent=2)
        
        print(f"Saved {new_count} new articles to {topic}")
        return new_count

def main():
    fetcher = RSSFetcher()
    topics = [
        Topic('AI', ['ai', 'machine learning', 'gpt']),
        Topic('Security', ['security', 'hack']),
    ]
    classifier = Classifier(topics)
    storage = Storage()
    
    # Fetch, classify, save
    articles = fetcher.fetch('https://hnrss.org/frontpage', 'Hacker News')
    classified = classifier.classify(articles)
    
    storage.save_articles(articles, "all")
    for topic, arts in classified.items():
        storage.save_articles(arts, topic)
    
    print("\nDone! Check the data/ directory")
    return 0

if __name__ == "__main__":
    exit(main())
```

**Test:** 
- Run once → Should save articles
- Run twice → Should only add new articles (deduplication)
- Check `data/` directory

---

## Version 0.6: Reports (110 min)

Add to previous version:

```python
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, classified, top_n=10):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"news_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write("# News Report\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            for topic, articles in classified.items():
                f.write(f"## {topic}\n")
                f.write(f"*{len(articles)} articles*\n\n")
                
                for i, article in enumerate(articles[:top_n], 1):
                    f.write(f"### {i}. {article.title}\n")
                    f.write(f"**Link:** {article.url}\n\n")
                    f.write("---\n\n")
        
        print(f"Report saved: {report_path}")
        return report_path

# In main(), add:
reporter = ReportGenerator()
reporter.generate(classified)
```

**Test:** Check `reports/` directory for markdown file

---

## Version 0.7: Command-Line Arguments (125 min)

Add to previous:

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="NewsAgg-Mini")
    parser.add_argument('--topics', help='Comma-separated topics')
    parser.add_argument('--top-n', type=int, default=10)
    args = parser.parse_args()
    
    # Create topics
    if args.topics:
        topic_names = args.topics.split(',')
        topics = [Topic(name, [name.lower()]) for name in topic_names]
    else:
        topics = [
            Topic('AI', ['ai', 'machine learning']),
            Topic('Security', ['security', 'hack']),
        ]
    
    # ... rest of code
    reporter.generate(classified, top_n=args.top_n)
```

**Test:**
```bash
python3 main.py --help
python3 main.py --topics ai,linux
python3 main.py --top-n 5
```

---

## Version 0.8: Configuration File (150 min)

Add:

```python
import yaml

def load_config(config_file=None):
    default = {
        'feeds': [
            {'url': 'https://hnrss.org/frontpage', 'name': 'HN'}
        ],
        'topics': [
            {'name': 'AI', 'keywords': ['ai', 'ml']}
        ]
    }
    
    if config_file and Path(config_file).exists():
        with open(config_file) as f:
            return yaml.safe_load(f)
    return default

# In main():
config = load_config(args.config)
topics = [Topic(t['name'], t['keywords']) for t in config['topics']]

all_articles = []
for feed in config['feeds']:
    arts = fetcher.fetch(feed['url'], feed['name'])
    all_articles.extend(arts)
```

---

## Version 0.9: Logging (160 min)

Add:

```python
import logging

def setup_logging(level="INFO"):
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, feed_url, source_name):
        self.logger.info(f"Fetching {source_name}...")
        # ... rest of code
        self.logger.info(f"Fetched {len(articles)} articles")
```

---

## Version 1.0: Complete (180 min)

The full version in `main.py` with:
- Error handling
- Type hints
- Comprehensive docstrings
- All features integrated

---

## 🔑 Key Takeaways

1. **Each version is runnable** - You can test at every step
2. **Incremental complexity** - Each version adds ONE major feature
3. **Quick feedback** - See results immediately
4. **Easy to debug** - Small changes = easy to find bugs
5. **Learning by doing** - Understand each piece as you build it

---

## 💡 Development Strategy

```
Version 0.1 (5 min)   → Skeleton
Version 0.2 (10 min)  → Data models
Version 0.3 (30 min)  → Core feature (RSS)
Version 0.4 (15 min)  → Classification
Version 0.5 (30 min)  → Storage
Version 0.6 (20 min)  → Reports
Version 0.7 (15 min)  → CLI
Version 0.8 (25 min)  → Config files
Version 0.9 (10 min)  → Logging
Version 1.0 (20 min)  → Polish & docs
```

**Total: ~3 hours for a complete, working news aggregator!**

---

## 🎯 Practice Exercise

Try building it yourself following this progression:

1. Start with v0.1 - get "Hello World" working
2. Add v0.2 - create the Article class
3. Add v0.3 - fetch from ONE feed
4. **Stop and test** - make sure it works
5. Continue incrementally

**Pro tip:** Save each version as `main_v01.py`, `main_v02.py`, etc. so you can always go back!