# RSS vs APIs for News Aggregation

You're absolutely right! Many news organizations do offer APIs. Let's explore both approaches, their tradeoffs, and when to use each.

---

## 📊 RSS vs APIs: Quick Comparison

| Factor | RSS | APIs |
|--------|-----|------|
| **Cost** | Free | Often paid (after free tier) |
| **Rate Limits** | None (usually) | Strict limits |
| **Authentication** | None | API keys required |
| **Data Structure** | Standardized XML | Varies by provider |
| **Historical Data** | Limited (recent only) | Often available |
| **Real-time** | Delayed (poll-based) | Can be real-time |
| **Reliability** | High | Depends on provider |
| **Search/Filter** | Limited | Powerful |
| **Setup Complexity** | Very simple | More complex |

---

## 🌐 Major News APIs

### 1. **NewsAPI** (Most Popular)
- **URL**: https://newsapi.org/
- **Free Tier**: 100 requests/day, 1 month history
- **Paid**: $449/month for production
- **Pros**: 80,000+ sources, powerful search, JSON
- **Cons**: Expensive, rate limits, requires attribution

```python
import requests

def fetch_from_newsapi(api_key, query="technology", page_size=20):
    """Fetch articles from NewsAPI"""
    url = "https://newsapi.org/v2/everything"
    
    params = {
        'q': query,
        'apiKey': api_key,
        'pageSize': page_size,
        'language': 'en',
        'sortBy': 'publishedAt'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    articles = []
    for item in data.get('articles', []):
        article = Article(
            title=item['title'],
            url=item['url'],
            source=item['source']['name'],
            summary=item.get('description', ''),
            published=item.get('publishedAt')
        )
        articles.append(article)
    
    return articles

# Usage
articles = fetch_from_newsapi(api_key="YOUR_API_KEY", query="AI")
```

### 2. **The Guardian API**
- **URL**: https://open-platform.theguardian.com/
- **Free Tier**: 5,000 requests/day, but only Guardian content
- **Pros**: Completely free, well-documented, high quality
- **Cons**: Single source only

```python
def fetch_from_guardian(api_key, query="technology"):
    """Fetch from The Guardian API"""
    url = "https://content.guardianapis.com/search"
    
    params = {
        'q': query,
        'api-key': api_key,
        'show-fields': 'headline,trailText,body',
        'page-size': 20
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    articles = []
    for item in data['response']['results']:
        article = Article(
            title=item['webTitle'],
            url=item['webUrl'],
            source='The Guardian',
            summary=item['fields'].get('trailText', ''),
            published=item['webPublicationDate']
        )
        articles.append(article)
    
    return articles
```

### 3. **New York Times API**
- **URL**: https://developer.nytimes.com/
- **Free Tier**: 500 requests/day, 1000/month
- **Pros**: Free, high quality, historical archive
- **Cons**: Single source, moderate limits

### 4. **Reddit API**
- **URL**: https://www.reddit.com/dev/api/
- **Free Tier**: 60 requests/minute
- **Pros**: Free, diverse sources, community-curated
- **Cons**: Not traditional news, requires OAuth

### 5. **Aggregator APIs**
- **Bing News API**: Microsoft, paid
- **Contextual Web News API**: $149/month
- **GNews API**: Free tier, 100 requests/day

---

## 🤔 When to Use RSS vs APIs

### Use RSS When:
✅ **Budget is tight** - RSS is completely free  
✅ **Simple needs** - Just want recent headlines  
✅ **Multiple diverse sources** - Every site has RSS  
✅ **No rate limits** - Can poll as often as needed  
✅ **Educational/personal projects** - No API key hassle  
✅ **Quick prototyping** - Get started in 5 minutes  

### Use APIs When:
✅ **Need search functionality** - Filter by keywords, date  
✅ **Need metadata** - Categories, sentiment, entities  
✅ **Historical data required** - Access past articles  
✅ **Single large source** - NYT, Guardian APIs are great  
✅ **Production application** - More reliable/structured  
✅ **Need filtering** - Language, country, domain filters  

---

## 🎯 Hybrid Approach (Best of Both Worlds)

**Strategy**: Use RSS as primary, APIs as supplements

```python
class MultiSourceFetcher:
    """Unified fetcher supporting both RSS and APIs"""
    
    def __init__(self):
        self.rss_fetcher = RSSFetcher()
        self.api_keys = {
            'newsapi': os.getenv('NEWSAPI_KEY'),
            'guardian': os.getenv('GUARDIAN_API_KEY'),
            'nyt': os.getenv('NYT_API_KEY')
        }
    
    def fetch(self, source_config):
        """Fetch from any source type"""
        source_type = source_config['type'].lower()
        
        if source_type == 'rss':
            return self.rss_fetcher.fetch(
                source_config['url'], 
                source_config['name']
            )
        
        elif source_type == 'newsapi':
            return self.fetch_newsapi(
                query=source_config.get('query', ''),
                sources=source_config.get('sources')
            )
        
        elif source_type == 'guardian':
            return self.fetch_guardian(
                query=source_config.get('query', '')
            )
        
        elif source_type == 'reddit':
            return self.fetch_reddit(
                subreddit=source_config['subreddit']
            )
        
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def fetch_newsapi(self, query, sources=None):
        """Fetch from NewsAPI"""
        if not self.api_keys['newsapi']:
            print("Warning: NewsAPI key not configured")
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': self.api_keys['newsapi'],
            'pageSize': 20,
            'language': 'en'
        }
        
        if sources:
            params['sources'] = ','.join(sources)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get('articles', []):
                articles.append(Article(
                    title=item['title'],
                    url=item['url'],
                    source=item['source']['name'],
                    summary=item.get('description', ''),
                    published=item.get('publishedAt')
                ))
            return articles
        
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
```

**Config Example:**
```yaml
sources:
  # RSS feeds (free, diverse)
  - id: hn
    name: Hacker News
    type: rss
    url: https://hnrss.org/frontpage
  
  - id: techcrunch
    name: TechCrunch
    type: rss
    url: https://techcrunch.com/feed/
  
  # APIs (when you need specific features)
  - id: guardian_tech
    name: Guardian Tech
    type: guardian
    query: technology
  
  - id: newsapi_ai
    name: AI News
    type: newsapi
    query: artificial intelligence
    sources: [techcrunch, wired, the-verge]
  
  - id: reddit_ml
    name: Reddit ML
    type: reddit
    subreddit: MachineLearning
```

---

## 💰 Cost Analysis

### Scenario: Fetching 1000 articles/day

#### RSS Approach:
- **Cost**: $0
- **Sources**: Unlimited
- **Effort**: Low (standard parsing)

#### API Approach:
- **NewsAPI**: $449/month ($5,388/year)
- **Multiple APIs**: $500-1000/month
- **Free tiers**: Severely limited

#### Hybrid Approach:
- **Cost**: $0 - $50/month (for premium sources)
- **Strategy**: RSS for bulk, APIs for premium/search

---

## 🔍 Real-World Use Cases

### Personal Project / Learning
**Use RSS** - Free, simple, plenty of sources
```yaml
sources:
  - Hacker News RSS
  - TechCrunch RSS
  - Ars Technica RSS
  - Reddit RSS (yes, it exists!)
```

### Startup / MVP
**Use Hybrid** - RSS + free API tiers
```yaml
sources:
  - RSS feeds (80% of content)
  - Guardian API (quality journalism)
  - Free NewsAPI tier (search capability)
```

### Production App
**Use APIs** - More reliable, better structure
```yaml
sources:
  - NewsAPI Pro ($449/mo)
  - Custom news partnerships
  - RSS as backup
```

---

## 🛠️ Practical Implementation

### Step 1: Add API Support to NewsAgg-Mini

```python
# Add to config.yaml
sources:
  - id: newsapi_tech
    name: Tech News
    type: newsapi
    query: technology
    enabled: true
  
  - id: guardian_politics
    name: Guardian Politics
    type: guardian
    query: politics
    enabled: true
```

### Step 2: Create Unified Fetcher

```python
class UnifiedFetcher:
    """Handles both RSS and API sources"""
    
    def __init__(self):
        self.handlers = {
            'rss': self.fetch_rss,
            'newsapi': self.fetch_newsapi,
            'guardian': self.fetch_guardian,
            'reddit': self.fetch_reddit
        }
    
    def fetch(self, source):
        """Dispatch to appropriate handler"""
        handler = self.handlers.get(source['type'])
        if not handler:
            print(f"Unknown source type: {source['type']}")
            return []
        
        return handler(source)
    
    def fetch_rss(self, source):
        # Existing RSS logic
        pass
    
    def fetch_newsapi(self, source):
        # NewsAPI logic
        pass
```

### Step 3: Handle Rate Limits

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    """Decorator to enforce rate limiting"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def fetch_from_newsapi(api_key, query):
    # API call here
    pass
```

---

## 📈 RSS Sources You Might Not Know About

### Reddit RSS (Free, Diverse)
```python
# Any subreddit has RSS!
feeds = [
    'https://www.reddit.com/r/technology/.rss',
    'https://www.reddit.com/r/programming/.rss',
    'https://www.reddit.com/r/machinelearning/.rss'
]
```

### Google News RSS
```python
# Topic-specific feeds
feeds = [
    'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en',
    # Tech news, customizable
]
```

### YouTube RSS
```python
# Channel feeds
'https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID'
```

### Many News Sites
```python
feeds = [
    'https://www.wired.com/feed/rss',
    'https://arstechnica.com/feed/',
    'https://www.theverge.com/rss/index.xml',
    'https://techcrunch.com/feed/',
    'https://news.ycombinator.com/rss',
    'https://www.reuters.com/rssFeed/technologyNews',
    'https://feeds.bbci.co.uk/news/technology/rss.xml'
]
```

---

## 🎯 Recommendation for NewsAgg-Mini

**Start with RSS, add APIs later:**

### Phase 1: RSS Only (What you have now)
- Zero cost
- Learn the basics
- Get 90% of functionality

### Phase 2: Add Free API Tiers
```yaml
sources:
  # Keep RSS feeds
  - type: rss
    ...
  
  # Add free APIs
  - type: guardian
    api_key: ${GUARDIAN_API_KEY}  # Free, 5000/day
    query: technology
```

### Phase 3: Paid APIs (If Needed)
Only when:
- RSS limitations hurt
- Need advanced search
- Building commercial product
- Have paying users

---

## 💡 Best Practices

### 1. **Always Cache API Results**
```python
def fetch_with_cache(source, cache_ttl=3600):
    cache_key = f"{source['type']}:{source['id']}"
    
    # Check cache first
    if cache_key in cache and not expired(cache[cache_key], cache_ttl):
        return cache[cache_key]
    
    # Fetch fresh
    articles = fetcher.fetch(source)
    cache[cache_key] = articles
    return articles
```

### 2. **Respect Rate Limits**
- Track API calls
- Implement backoff
- Monitor usage

### 3. **Handle API Failures Gracefully**
```python
def fetch_with_fallback(source):
    try:
        return api_fetch(source)
    except RateLimitError:
        # Fall back to RSS if available
        if source.get('rss_fallback'):
            return rss_fetch(source['rss_fallback'])
    except Exception as e:
        log_error(e)
        return []
```

### 4. **Monitor Costs**
```python
def track_api_usage():
    usage = {
        'newsapi': get_monthly_calls('newsapi'),
        'guardian': get_daily_calls('guardian')
    }
    
    if usage['newsapi'] > 8000:  # 80% of free tier
        alert("NewsAPI usage high!")
```

---

## 🚀 Next Steps

1. **Try it with RSS first** (what you have now works great!)
2. **Sign up for free API keys** (Guardian, NYT)
3. **Implement hybrid fetcher** (when you need it)
4. **Monitor usage** (don't hit limits)
5. **Upgrade only if needed** (when RSS isn't enough)

---

## 📚 Resources

- **NewsAPI**: https://newsapi.org/
- **Guardian API**: https://open-platform.theguardian.com/
- **NYT API**: https://developer.nytimes.com/
- **Reddit API**: https://www.reddit.com/dev/api/
- **RSS Directory**: https://feeder.co/

---

## ✅ TL;DR

**You're right that APIs exist, but:**
- Most require API keys and have rate limits
- Free tiers are restrictive (100-500 requests/day)
- Paid tiers are expensive ($50-500/month)
- RSS is free, unlimited, and works everywhere

**Best approach:**
1. Start with RSS (free, simple, plenty of sources)
2. Add free API tiers for specific features
3. Only pay for APIs when RSS limitations hurt

**For NewsAgg-Mini specifically:**
- RSS is perfect for learning and personal use
- You can add API support later in 30 minutes
- 90% of users will never need paid APIs

The beauty of the architecture is that it's **source-agnostic** - the fetcher abstraction makes it trivial to add new source types later! 🎯