# Building NewsAgg-Mini from Scratch: A Complete Walkthrough

This document walks through the **thinking process** and **step-by-step approach** to building a news aggregator from the ground up.

---

## 🎯 The Problem Statement

**Goal**: Build a tool that fetches news from multiple sources, organizes them by topic, and generates reports.

**Requirements**:
- Fetch articles from RSS feeds
- Classify articles into topics
- Store articles (avoid duplicates)
- Generate readable reports

---

## 🧠 The Thinking Process

### Phase 1: Understanding the Domain (Research)

**Questions to ask:**
1. How do RSS feeds work? (They're XML files with structured article data)
2. What information do we need from each article? (Title, URL, summary, date, source)
3. How should we organize the data? (By topic)
4. Where should we store it? (Files, database?)
5. What's the output format? (Markdown reports)

**Key insights:**
- RSS feeds are standardized → easy to parse with existing libraries
- Classification can start simple (keyword matching) → can be enhanced later
- JSON is good enough for storage → no need for a database initially
- Command-line tool is simplest → web interface can come later

---

## 📝 Step-by-Step Development Process

### STEP 1: Start with the Skeleton (5 minutes)

**What to write first**: The absolute minimum to make a runnable program.

```python
#!/usr/bin/env python3
"""
NewsAgg-Mini: A simple news aggregator
"""

def main():
    print("NewsAgg-Mini started")
    # TODO: Fetch articles
    # TODO: Classify articles
    # TODO: Save articles
    # TODO: Generate report
    print("Done!")
    return 0

if __name__ == "__main__":
    exit(main())
```

**Why this first?**
- Proves the script runs
- Gives a clear structure for what needs to be built
- Documents your thinking with TODOs

**Test it:**
```bash
chmod +x main.py
python3 main.py
```

---

### STEP 2: Define Your Data Models (10 minutes)

**Thinking**: "What data am I working with?"

**Core entities:**
1. **Article** - The main data unit
2. **Topic** - How articles are categorized

```python
class Article:
    """Represents a news article"""
    def __init__(self, title: str, url: str, source: str):
        self.title = title
        self.url = url
        self.source = source
        self.summary = ""
        self.published = None
        
        # Generate a unique ID (for deduplication later)
        import hashlib
        content = f"{source}|{url}|{title}"
        self.id = hashlib.md5(content.encode()).hexdigest()[:12]
```

**Why define models early?**
- Forces you to think about data structure
- Makes the rest of the code cleaner
- Easy to serialize/deserialize later

**Test it:**
```python
# Add to main()
test_article = Article("Test Title", "http://example.com", "Test Source")
print(f"Article ID: {test_article.id}")
print(f"Article Title: {test_article.title}")
```

---

### STEP 3: Implement the First Real Feature - RSS Fetching (30 minutes)

**Thinking**: "Let me get ONE article from ONE feed and print it."

**Why start with fetching?**
- It's the entry point - no data means no app
- Quick feedback loop - you see results immediately
- Tests your internet connection and feed URLs

```python
import feedparser

class RSSFetcher:
    def fetch(self, feed_url: str, source_name: str):
        """Fetch articles from an RSS feed"""
        print(f"Fetching from {source_name}...")
        
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:5]:  # Start with just 5 articles
            article = Article(
                title=entry.get('title', 'No Title'),
                url=entry.get('link', ''),
                source=source_name
            )
            articles.append(article)
            print(f"  - {article.title}")
        
        return articles

# In main():
fetcher = RSSFetcher()
articles = fetcher.fetch('https://hnrss.org/frontpage', 'Hacker News')
print(f"Fetched {len(articles)} articles")
```

**Test it immediately:**
```bash
python3 main.py
```

**Expected output:**
```
Fetching from Hacker News...
  - Article title 1
  - Article title 2
  ...
Fetched 5 articles
```

**Common issues to debug:**
- Import errors → Install feedparser: `pip install feedparser`
- No articles → Check internet connection
- Parse errors → Print the feed object to inspect

---

### STEP 4: Add More Feed Details (15 minutes)

**Thinking**: "Now that basic fetching works, let me extract more information."

```python
# Enhance the Article class
class Article:
    def __init__(self, title: str, url: str, source: str, 
                 summary: str = None, published: str = None):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary or ""
        self.published = published
        # ... ID generation

# Enhance the fetcher
for entry in feed.entries[:5]:
    # Get summary
    summary = entry.get('summary') or entry.get('description') or ''
    summary = summary[:200]  # Limit length
    
    # Get published date
    published = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        from datetime import datetime, timezone
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        published = dt.isoformat()
    
    article = Article(
        title=entry.get('title', 'No Title'),
        url=entry.get('link', ''),
        source=source_name,
        summary=summary,
        published=published
    )
```

**Test it:**
```python
# Print more details
for article in articles[:3]:
    print(f"\nTitle: {article.title}")
    print(f"URL: {article.url}")
    print(f"Summary: {article.summary[:50]}...")
    print(f"Published: {article.published}")
```

---

### STEP 5: Implement Classification (20 minutes)

**Thinking**: "How do I know which articles belong to which topics?"

**Simplest approach**: Keyword matching

```python
class Topic:
    """Represents a topic with keywords for matching"""
    def __init__(self, name: str, keywords: list):
        self.name = name
        self.keywords = [k.lower() for k in keywords]
    
    def matches(self, text: str) -> bool:
        """Check if text contains any of our keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

class Classifier:
    """Classifies articles into topics"""
    def __init__(self, topics: list):
        self.topics = topics
    
    def classify(self, articles: list):
        """Group articles by topic"""
        result = {topic.name: [] for topic in self.topics}
        result['uncategorized'] = []
        
        for article in articles:
            # Search in title + summary
            search_text = f"{article.title} {article.summary}"
            
            matched = False
            for topic in self.topics:
                if topic.matches(search_text):
                    result[topic.name].append(article)
                    matched = True
            
            if not matched:
                result['uncategorized'].append(article)
        
        return result

# In main():
topics = [
    Topic('AI', ['ai', 'machine learning', 'gpt']),
    Topic('Security', ['security', 'hack', 'breach']),
]

classifier = Classifier(topics)
classified = classifier.classify(articles)

for topic, arts in classified.items():
    print(f"\n{topic}: {len(arts)} articles")
```

**Test it:**
- You should see articles grouped by topic
- Check if classification makes sense
- Tweak keywords if needed

---

### STEP 6: Add Storage (25 minutes)

**Thinking**: "I don't want to re-fetch articles every time. Let me save them."

**Simple approach**: JSON files (one per topic)

```python
import json
from pathlib import Path

class Storage:
    """Saves and loads articles from JSON files"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_articles(self, articles: list, topic: str = "all"):
        """Save articles to a JSON file"""
        file_path = self.data_dir / f"{topic}_articles.json"
        
        # Convert articles to dictionaries
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'url': article.url,
                'source': article.source,
                'summary': article.summary,
                'published': article.published
            })
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(articles)} articles to {file_path}")

# In main():
storage = Storage()
storage.save_articles(articles, topic="all")
```

**Test it:**
```bash
python3 main.py
ls data/  # Should see all_articles.json
cat data/all_articles.json  # Should see JSON data
```

**Next: Add deduplication** (prevents saving the same article twice)

```python
def save_articles(self, articles: list, topic: str = "all"):
    file_path = self.data_dir / f"{topic}_articles.json"
    
    # Load existing articles
    existing_ids = set()
    existing_articles = []
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
            existing_ids = {a['id'] for a in existing_data}
            existing_articles = existing_data
    
    # Add only new articles
    new_count = 0
    for article in articles:
        if article.id not in existing_ids:
            existing_articles.append(self._article_to_dict(article))
            new_count += 1
    
    # Save everything
    with open(file_path, 'w') as f:
        json.dump(existing_articles, f, indent=2)
    
    print(f"Saved {new_count} new articles (total: {len(existing_articles)})")
```

---

### STEP 7: Generate Reports (20 minutes)

**Thinking**: "I have data. Now I need a human-readable summary."

**Format choice**: Markdown (readable in terminal and GitHub)

```python
from datetime import datetime

class ReportGenerator:
    """Generates markdown reports"""
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, classified: dict, top_n: int = 10):
        """Generate a markdown report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"news_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write("# News Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Write each topic
            for topic, articles in classified.items():
                if not articles:
                    continue
                
                f.write(f"## {topic}\n")
                f.write(f"*{len(articles)} articles*\n\n")
                
                # Show top N articles
                for i, article in enumerate(articles[:top_n], 1):
                    f.write(f"### {i}. {article.title}\n")
                    f.write(f"**Source:** {article.source}\n")
                    f.write(f"**Link:** {article.url}\n\n")
                    
                    if article.summary:
                        f.write(f"{article.summary[:150]}...\n\n")
                    
                    f.write("---\n\n")
        
        print(f"Report saved to: {report_path}")
        return report_path

# In main():
reporter = ReportGenerator()
reporter.generate(classified)
```

**Test it:**
```bash
python3 main.py
ls reports/  # Should see a new .md file
cat reports/news_report_*.md  # Should see formatted report
```

---

### STEP 8: Add Command-Line Interface (15 minutes)

**Thinking**: "Let users customize behavior without editing code."

```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="NewsAgg-Mini: A simple news aggregator"
    )
    
    parser.add_argument('--topics', 
                       help='Comma-separated topics to track')
    parser.add_argument('--top-n', type=int, default=10,
                       help='Number of articles per topic in report')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING'])
    
    args = parser.parse_args()
    
    # Use the arguments
    if args.topics:
        topic_names = args.topics.split(',')
        topics = [Topic(name, [name.lower()]) for name in topic_names]
    else:
        # Use defaults
        topics = [
            Topic('AI', ['ai', 'machine learning']),
            Topic('Security', ['security', 'hack']),
        ]
    
    # ... rest of the code
    reporter.generate(classified, top_n=args.top_n)
```

**Test it:**
```bash
python3 main.py --help
python3 main.py --topics ai,linux,security
python3 main.py --top-n 5
```

---

### STEP 9: Add Configuration File Support (20 minutes)

**Thinking**: "Managing multiple feeds/topics via command-line is tedious. Use a config file."

```python
import yaml

def load_config(config_file: str = None):
    """Load configuration from YAML file"""
    default_config = {
        'feeds': [
            {'url': 'https://hnrss.org/frontpage', 'name': 'Hacker News'}
        ],
        'topics': [
            {'name': 'AI', 'keywords': ['ai', 'machine learning']}
        ]
    }
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    return default_config

# In main():
config = load_config(args.config)

# Create topics from config
topics = [
    Topic(t['name'], t['keywords']) 
    for t in config['topics']
]

# Fetch from all configured feeds
all_articles = []
for feed in config['feeds']:
    articles = fetcher.fetch(feed['url'], feed['name'])
    all_articles.extend(articles)
```

**Create config.yaml:**
```yaml
feeds:
  - url: https://hnrss.org/frontpage
    name: Hacker News

topics:
  - name: AI
    keywords: [ai, machine learning, gpt]
  - name: Security
    keywords: [security, hack, breach]
```

---

### STEP 10: Add Logging (10 minutes)

**Thinking**: "I need to debug issues and see what's happening."

```python
import logging

def setup_logging(level: str = "INFO"):
    """Configure logging"""
    log_level = getattr(logging, level.upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    return logging.getLogger(__name__)

# In each class:
class RSSFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, feed_url, source_name):
        self.logger.info(f"Fetching RSS: {source_name}")
        # ...
        self.logger.info(f"Fetched {len(articles)} articles")

# In main():
logger = setup_logging(args.log_level)
logger.info("Starting NewsAgg-Mini")
```

**Test it:**
```bash
python3 main.py --log-level DEBUG
```

---

### STEP 11: Add Error Handling (15 minutes)

**Thinking**: "What if a feed is down? What if parsing fails?"

```python
class RSSFetcher:
    def fetch(self, feed_url, source_name):
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            self.logger.error(f"Failed to fetch {feed_url}: {e}")
            return []
        
        articles = []
        for entry in feed.entries[:20]:
            try:
                # Parse entry
                article = self._parse_entry(entry, source_name)
                articles.append(article)
            except Exception as e:
                self.logger.warning(f"Skipping article due to error: {e}")
                continue
        
        return articles
```

---

### STEP 12: Refactor and Organize (30 minutes)

**Thinking**: "The code works but it's getting messy. Clean it up."

**Actions:**
1. Group related functions into classes
2. Add docstrings to all functions
3. Separate concerns (fetching, classification, storage, reporting)
4. Add type hints
5. Extract magic numbers to constants
6. Add comments explaining WHY, not WHAT

**Example refactoring:**

```python
# Before:
summary = summary[:200]

# After:
MAX_SUMMARY_LENGTH = 200  # Prevent memory bloat for large feeds
summary = summary[:MAX_SUMMARY_LENGTH]
```

---

### STEP 13: Test Everything (20 minutes)

**Manual testing checklist:**
- ✅ Run with no arguments (default config)
- ✅ Run with custom topics via CLI
- ✅ Run with config file
- ✅ Run twice (test deduplication)
- ✅ Test with invalid feed URL
- ✅ Test with empty feed
- ✅ Test all log levels
- ✅ Check generated files (data/, reports/)

---

### STEP 14: Write Documentation (30 minutes)

**What to document:**
1. **README.md** - Quick start, usage examples
2. **Inline comments** - Explain complex logic
3. **Docstrings** - Describe functions and classes
4. **config.example.yaml** - Show all options
5. **Extension ideas** - Help others learn

---

## 🎓 Key Development Principles Used

### 1. **Start Simple, Build Incrementally**
- Don't try to build everything at once
- Each step adds one feature
- Test after each step

### 2. **Fail Fast, Fail Often**
- Run the code frequently
- See errors early
- Fix issues immediately

### 3. **Data First**
- Define data structures early
- Everything else flows from data

### 4. **Separation of Concerns**
- Each class has one job
- Makes code easier to test and modify

### 5. **Configuration Over Code**
- Use config files for things that change
- Don't hardcode URLs, keywords, etc.

### 6. **User Experience Matters**
- Add help text
- Provide examples
- Show progress

---

## 🔄 The Development Loop

For each feature:

```
1. Think: What do I need?
2. Research: How do others solve this?
3. Plan: What's the simplest approach?
4. Code: Write the minimum to test the idea
5. Test: Run it immediately
6. Debug: Fix issues
7. Refine: Improve based on learnings
8. Document: Explain what you built
9. Repeat: Move to next feature
```

---

## 🛠️ Tools That Help

1. **Interactive Python (REPL)**: Test ideas quickly
   ```bash
   python3
   >>> import feedparser
   >>> feed = feedparser.parse('https://hnrss.org/frontpage')
   >>> feed.entries[0].keys()
   ```

2. **Print debugging**: See what's happening
   ```python
   print(f"DEBUG: articles = {articles}")
   ```

3. **Online RSS viewers**: Understand feed structure
   - https://rssviewer.app/

4. **JSON viewers**: Inspect stored data
   ```bash
   cat data/all_articles.json | python3 -m json.tool
   ```

---

## 🚀 What Makes This Approach Work

1. **Immediate feedback** - You see results after each step
2. **Low risk** - Small changes are easy to undo
3. **Learning by doing** - You understand each piece as you build it
4. **Motivation** - Progress is visible and rewarding

---

## 📈 After Building the Basic Version

### What to add next (in order):

1. **More feeds** (easy, immediate value)
2. **Better keywords** (easy, improves quality)
3. **HTML reports** (medium, prettier output)
4. **Web scraping** (medium, more sources)
5. **Database storage** (medium, better performance)
6. **ML classification** (hard, more accurate)
7. **Web dashboard** (hard, better UX)
8. **Publishing to social media** (hard, automation)

### How to learn from the code:

1. **Modify small things**: Change report format, add a keyword
2. **Break it intentionally**: See what error messages teach you
3. **Add logging everywhere**: Understand the flow
4. **Rewrite a class**: Practice different approaches
5. **Extend it**: Add a feature you want

---

## 💡 Common Pitfalls to Avoid

1. **Overengineering early** - Keep it simple at first
2. **Not testing frequently** - Test after every change
3. **Ignoring errors** - Handle exceptions properly
4. **Hardcoding values** - Use configuration
5. **No documentation** - Future you will thank present you
6. **Perfect code obsession** - Working code > perfect code

---

## 🎯 Final Wisdom

> "Make it work, make it right, make it fast." - Kent Beck

1. **Make it work** - Get a working prototype (Steps 1-8)
2. **Make it right** - Refactor and clean up (Steps 9-12)
3. **Make it fast** - Optimize if needed (later)

The key is to always have working code. Never make so many changes that you can't get back to a working state.

---

## 📚 Further Reading

- **"The Pragmatic Programmer"** - Best practices
- **"Clean Code"** by Robert Martin - Writing readable code
- **"Design Patterns"** - Common solutions to common problems
- **Real Python tutorials** - Practical Python guides

---

**Remember**: Every expert was once a beginner. The difference is they kept building, kept learning, and kept improving. Start small, stay curious, and have fun! 🚀