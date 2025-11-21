# NewsAgg-Mini: Quick Start Guide

## 📚 Documentation Files

- **README.md** - Overview, features, and usage
- **WALKTHROUGH.md** - Detailed thinking process and step-by-step guide
- **INCREMENTAL_BUILD.md** - Code snapshots at each development stage
- **QUICK_START.md** - This file (summary)

---

## ⚡ 5-Minute Setup

```bash
# Install dependencies
pip install feedparser pyyaml

# Run with defaults
python3 main.py

# View report
ls reports/
```

---

## 🧠 Development Philosophy

### The Build Order (What to Write First)

1. **Skeleton** (5 min) - Empty main() function
2. **Data Models** (10 min) - Article and Topic classes
3. **RSS Fetcher** (30 min) - Fetch from one feed
4. **Classifier** (20 min) - Keyword matching
5. **Storage** (25 min) - Save to JSON
6. **Reports** (20 min) - Generate markdown
7. **CLI** (15 min) - Command-line arguments
8. **Config** (20 min) - YAML configuration
9. **Polish** (40 min) - Logging, errors, docs

**Total: ~3 hours**

---

## 🎯 Core Concepts

### 1. Data First
Always start by defining your data structures:
```python
class Article:
    def __init__(self, title, url, source):
        self.title = title
        self.url = url
        self.source = source
```

### 2. Test Immediately
Run code after every small change:
```python
# Write this
article = Article("Test", "http://...", "Source")

# Run it
python3 main.py

# See if it works
print(article.title)
```

### 3. Incremental Development
Add ONE feature at a time:
- ✅ Fetch articles → TEST
- ✅ Classify articles → TEST
- ✅ Save articles → TEST

### 4. Keep It Simple
Start with the simplest solution:
- JSON files (not database)
- Keyword matching (not ML)
- Markdown reports (not HTML)

---

## 🔄 The Development Loop

```
Think → Code → Test → Debug → Refine → Repeat
  ↓       ↓       ↓       ↓        ↓        ↓
"What?"  5 min   Run    Fix     Clean   Next
```

For EVERY feature:
1. **Think:** What do I need?
2. **Code:** Write minimal code
3. **Test:** Run it immediately
4. **Debug:** Fix any issues
5. **Refine:** Clean up the code
6. **Repeat:** Move to next feature

---

## 💡 Key Insights

### Why RSS Fetching First?
- It's the entry point (no data = no app)
- Quick visual feedback (you see articles)
- Tests your setup (internet, dependencies)

### Why JSON Storage?
- No database setup needed
- Human-readable
- Easy to debug (just open the file)
- Good enough for 10,000+ articles

### Why Keyword Classification?
- Simple to implement
- Fast to run
- Good enough for 80% of use cases
- Easy to understand and debug

### Why Markdown Reports?
- Readable in terminal and browser
- Easy to generate
- Looks professional
- Portable (works everywhere)

---

## 🚀 Extending the Project

### Beginner (No new concepts)
1. Add more RSS feeds
2. Create new topics with keywords
3. Change report format
4. Adjust article limits

### Intermediate (New libraries)
1. Add web scraping (BeautifulSoup)
2. Generate HTML reports (Jinja2)
3. Schedule with cron
4. Email reports (smtplib)

### Advanced (New paradigms)
1. Use SQLite database
2. Add ML classification (spaCy)
3. Build web API (FastAPI)
4. Create dashboard (Streamlit)

---

## 🛠️ Debugging Tips

### No articles fetched?
```python
# Add debug prints
feed = feedparser.parse(url)
print(f"Feed entries: {len(feed.entries)}")
print(f"First entry keys: {feed.entries[0].keys()}")
```

### Classification not working?
```python
# Log the matching process
text = f"{article.title} {article.summary}"
print(f"Searching in: {text[:100]}")
for keyword in keywords:
    if keyword in text.lower():
        print(f"  ✓ Matched: {keyword}")
```

### Storage issues?
```python
# Check file contents
import json
with open('data/all_articles.json') as f:
    data = json.load(f)
    print(f"Stored articles: {len(data)}")
```

---

## 📊 Architecture at a Glance

```
main.py
  ├─ load_config() → feeds, topics
  ├─ RSSFetcher().fetch() → articles
  ├─ Classifier().classify() → grouped by topic
  ├─ Storage().save_articles() → data/*.json
  └─ ReportGenerator().generate() → reports/*.md
```

---

## 🎓 Learning Path

### Week 1: Understand
- Read the full code
- Run with different options
- Check the generated files

### Week 2: Modify
- Add a new RSS feed
- Create custom topics
- Change report format

### Week 3: Extend
- Add a new feature from extension ideas
- Handle edge cases
- Improve error messages

### Week 4: Build Your Own
- Start from scratch following INCREMENTAL_BUILD.md
- Compare your solution to the provided one
- Understand the design decisions

---

## 🔍 Code Reading Guide

**Read in this order:**

1. **Data Models** (lines 60-120)
   - Article class
   - Topic class

2. **RSS Fetcher** (lines 126-188)
   - How feeds are parsed
   - How articles are created

3. **Classifier** (lines 194-233)
   - Keyword matching logic
   - Topic assignment

4. **Storage** (lines 239-293)
   - Deduplication
   - JSON serialization

5. **Report Generator** (lines 299-347)
   - Markdown formatting
   - File writing

6. **Configuration** (lines 353-397)
   - YAML loading
   - Defaults

7. **Main Function** (lines 416-502)
   - How everything connects
   - Program flow

---

## 🎯 Success Metrics

After building this, you should understand:

- ✅ How to parse RSS feeds
- ✅ How to structure a Python project
- ✅ How to persist data in JSON
- ✅ How to use command-line arguments
- ✅ How to load configuration files
- ✅ How to handle errors gracefully
- ✅ How to generate reports
- ✅ How to build incrementally

---

## 💬 Common Questions

**Q: Why not use a database?**
A: JSON is simpler to start with. Migrate to SQLite when you hit performance issues.

**Q: Why not use ML for classification?**
A: Keywords work well for most cases. Add ML when you have training data and need better accuracy.

**Q: Should I split this into multiple files?**
A: Not initially. Single file is easier to understand. Refactor into modules when it grows past 1000 lines.

**Q: How do I add more feeds?**
A: Edit `config.yaml` and add to the `feeds` list.

**Q: Can I classify the same article into multiple topics?**
A: Yes! The classifier already supports this - one article can match multiple topics.

---

## 🚦 Next Steps

1. **Run the code** - See it in action
2. **Read WALKTHROUGH.md** - Understand the thinking
3. **Follow INCREMENTAL_BUILD.md** - Build it yourself
4. **Modify something small** - Practice
5. **Add a feature** - Extend it

---

## 📚 Resources

- **feedparser docs**: https://feedparser.readthedocs.io/
- **Python argparse**: https://docs.python.org/3/library/argparse.html
- **YAML syntax**: https://yaml.org/
- **JSON in Python**: https://realpython.com/python-json/

---

**Remember:** The best way to learn is by doing. Start small, test often, and have fun! 🚀