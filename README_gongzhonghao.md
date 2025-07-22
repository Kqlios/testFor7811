# WeChat Official Accounts (公众号) Crawler

A specialized Python web crawler designed specifically for WeChat Official Accounts (公众号) posts and articles. This crawler focuses on extracting content from WeChat's public accounts ecosystem.

## 🎯 Features

### Core Functionality
- **🔍 Official Account Search**: Find WeChat Official Accounts by keywords
- **📄 Article Search**: Search for articles across all official accounts
- **📚 Content Extraction**: Extract full article content, metadata, and statistics
- **📊 Data Export**: Save results in CSV and JSON formats
- **🔄 Batch Processing**: Process multiple accounts and articles in batches

### WeChat-Specific Features
- **🛡️ Anti-Detection**: Optimized for WeChat's anti-bot measures
- **📱 Mobile Simulation**: Simulates WeChat mobile client access
- **⏱️ Smart Rate Limiting**: Respects WeChat's request limits
- **🏷️ Category Support**: Built-in support for different account categories
- **📈 Trending Topics**: Monitor hot topics across official accounts
- **✅ Verification Status**: Track verified vs unverified accounts

## 🚀 Quick Start

### Basic Usage

```python
from wechat_gongzhonghao_crawler import WeChatOfficialAccountsCrawler

# Initialize crawler
with WeChatOfficialAccountsCrawler(headless=True) as crawler:
    # Search for tech-related official accounts
    accounts = crawler.search_official_accounts("人工智能")
    print(f"Found {len(accounts)} accounts")
    
    # Search for articles about AI
    articles = crawler.search_account_articles("机器学习")
    print(f"Found {len(articles)} articles")
    
    # Get recent posts from an account
    if accounts:
        posts = crawler.get_account_recent_posts(accounts[0]['profile_link'])
        
        # Get detailed content
        if posts:
            content = crawler.get_article_content(posts[0]['url'])
            print(f"Article: {content['title']}")
            print(f"Read count: {content['read_count']}")
    
    # Save results
    crawler.save_to_csv(accounts, "tech_accounts.csv")
    crawler.save_to_json(articles, "ai_articles.json")
```

### Search by Categories

```python
from gongzhonghao_config import ACCOUNT_CATEGORIES

with WeChatOfficialAccountsCrawler() as crawler:
    # Get technology accounts
    tech_keywords = ACCOUNT_CATEGORIES['technology']['keywords']
    
    all_accounts = []
    for keyword in tech_keywords[:3]:  # Top 3 keywords
        accounts = crawler.search_official_accounts(keyword)
        all_accounts.extend(accounts)
    
    crawler.save_to_csv(all_accounts, "technology_accounts.csv")
```

### Monitor Trending Topics

```python
from gongzhonghao_config import HOT_TOPICS

with WeChatOfficialAccountsCrawler() as crawler:
    trending_data = []
    
    for topic in HOT_TOPICS[:10]:  # Top 10 hot topics
        articles = crawler.search_account_articles(topic)
        trending_data.append({
            'topic': topic,
            'article_count': len(articles),
            'articles': articles
        })
    
    crawler.save_to_json(trending_data, "trending_analysis.json")
```

## 📋 Installation

### Prerequisites
- Python 3.8+
- Chrome browser
- Stable internet connection

### Setup

1. **Clone and install**:
```bash
git clone <repository-url>
cd wechat-gongzhonghao-crawler
pip install -r requirements.txt
```

2. **Run setup**:
```bash
python gongzhonghao_config.py  # Setup directories and validate config
```

3. **Test the crawler**:
```bash
python gongzhonghao_examples.py
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file:
```bash
# Browser settings
WECHAT_GZH_HEADLESS=true
WECHAT_GZH_DATA_DIR=./gongzhonghao_data

# Proxy (optional)
WECHAT_GZH_PROXY=http://your-proxy:port

# Rate limiting
WECHAT_GZH_MAX_POSTS=20
```

### Configuration File

Edit `gongzhonghao_config.py` to customize:

```python
GONGZHONGHAO_CONFIG = {
    'headless': True,
    'random_delay_min': 2,      # Minimum delay between requests
    'random_delay_max': 5,      # Maximum delay between requests
    'max_posts_per_account': 20, # Posts to crawl per account
    'max_accounts_per_search': 10, # Accounts per search
}
```

## 📊 Supported Account Categories

| Category | Description | Keywords |
|----------|-------------|----------|
| 🔬 **Technology** | Tech, AI, Programming | 人工智能, 科技, 编程, 互联网 |
| 💼 **Business** | Finance, Startups, Investment | 商业, 创业, 投资, 金融 |
| 🎓 **Education** | Learning, Training, Skills | 教育, 学习, 培训, 技能 |
| 🏥 **Health** | Medical, Wellness, Fitness | 健康, 医疗, 养生, 运动 |
| 🌟 **Lifestyle** | Travel, Food, Culture | 生活, 旅行, 美食, 文化 |
| 📰 **News** | Current Events, Politics | 新闻, 时事, 政治, 社会 |
| 💰 **Finance** | Investment, Banking, Trading | 理财, 股票, 基金, 投资 |

## 🔥 Hot Topics Monitoring

The crawler includes built-in support for monitoring trending topics:

**Technology**: ChatGPT, OpenAI, 人工智能, 自动驾驶, 区块链, 元宇宙  
**Economics**: 新能源, 芯片, 房地产, 股市, 通胀  
**Social**: 疫情, 教育改革, 就业, 养老  
**International**: 中美关系, 俄乌冲突, 一带一路  

## 📈 Advanced Usage

### Custom Search Strategies

```python
from gongzhonghao_config import SEARCH_STRATEGIES

# Use different search strategies
strategies = ['broad_search', 'focused_search', 'deep_search']

for strategy in strategies:
    config = SEARCH_STRATEGIES[strategy]
    print(f"Using {config['description']}")
    
    # Apply strategy settings to crawler
    # (implementation details in the crawler class)
```

### Account Quality Analysis

```python
def analyze_account_quality(accounts):
    """Analyze account quality based on various metrics"""
    from gongzhonghao_config import ACCOUNT_QUALITY_METRICS
    
    for account in accounts:
        score = 0
        
        if account.get('authentication'):
            score += ACCOUNT_QUALITY_METRICS['has_verification']
        
        if account.get('description'):
            score += ACCOUNT_QUALITY_METRICS['has_description']
            score += len(account['description']) * ACCOUNT_QUALITY_METRICS['description_length_bonus']
        
        if account.get('wechat_id'):
            score += ACCOUNT_QUALITY_METRICS['has_wechat_id']
        
        account['quality_score'] = score
    
    return sorted(accounts, key=lambda x: x['quality_score'], reverse=True)
```

### Batch Industry Analysis

```python
def analyze_industries():
    """Analyze multiple industries in batch"""
    with WeChatOfficialAccountsCrawler() as crawler:
        results = {}
        
        for industry, data in ACCOUNT_CATEGORIES.items():
            print(f"Analyzing {industry}...")
            
            industry_accounts = []
            industry_articles = []
            
            for keyword in data['keywords'][:3]:  # Top 3 keywords per industry
                accounts = crawler.search_official_accounts(keyword)
                articles = crawler.search_account_articles(keyword)
                
                industry_accounts.extend(accounts)
                industry_articles.extend(articles)
                
                time.sleep(2)  # Be respectful
            
            results[industry] = {
                'accounts': len(industry_accounts),
                'articles': len(industry_articles),
                'data': {
                    'accounts': industry_accounts,
                    'articles': industry_articles
                }
            }
            
            # Save industry-specific data
            crawler.save_to_csv(industry_accounts, f"{industry}_accounts.csv")
            crawler.save_to_csv(industry_articles, f"{industry}_articles.csv")
        
        return results

# Run analysis
industry_results = analyze_industries()
print("Industry Analysis Results:")
for industry, stats in industry_results.items():
    print(f"{industry}: {stats['accounts']} accounts, {stats['articles']} articles")
```

## 📂 Output Structure

```
gongzhonghao_data/
├── accounts/           # Account information
├── articles/           # Article content and metadata
├── images/            # Downloaded images (if enabled)
├── logs/              # Crawler logs
└── backups/           # Automatic backups
```

### CSV Output Format

**Accounts CSV**:
```csv
account_name,wechat_id,description,profile_link,authentication,crawled_at
AI科技大本营,aitechcamp,专注AI技术分享,https://...,verified,2024-01-15T10:30:00
```

**Articles CSV**:
```csv
title,url,account_name,publish_date,summary,read_count,like_count,crawled_at
ChatGPT最新进展,https://mp.weixin.qq.com/s/...,AI前沿,2024-01-15,介绍ChatGPT...,1200,89,2024-01-15T10:30:00
```

## ⚡ Performance Tips

1. **Use Appropriate Delays**: WeChat has strict rate limiting
   ```python
   GONGZHONGHAO_CONFIG['random_delay_min'] = 3  # Increase for stability
   ```

2. **Batch Processing**: Process multiple items efficiently
   ```python
   # Process in small batches
   for batch in chunks(keywords, 5):
       process_batch(batch)
       time.sleep(10)  # Rest between batches
   ```

3. **Proxy Rotation**: Use proxies for large-scale crawling
   ```python
   proxies = ['proxy1:port', 'proxy2:port', 'proxy3:port']
   crawler = WeChatOfficialAccountsCrawler(proxy=random.choice(proxies))
   ```

4. **Content Filtering**: Filter out low-quality content
   ```python
   # Filter by read count
   quality_articles = [a for a in articles if int(a.get('read_count', 0)) > 100]
   ```

## 🚫 Rate Limiting & Best Practices

### Recommended Limits
- **Requests per minute**: 20 (conservative)
- **Requests per hour**: 500
- **Delay between requests**: 2-5 seconds
- **Concurrent requests**: 3 maximum

### Anti-Detection Measures
- Random user agents
- Variable request delays
- Mobile browser simulation
- Proxy rotation support
- Request pattern randomization

### Respectful Crawling
```python
# Good practices
crawler = WeChatOfficialAccountsCrawler(
    headless=True,              # Less resource intensive
    proxy="http://proxy:port"   # Use proxy if needed
)

# Add delays between batches
time.sleep(random.uniform(5, 10))

# Monitor success rate
success_rate = successful_requests / total_requests
if success_rate < 0.8:
    print("Consider slowing down or using different approach")
```

## ⚖️ Legal & Ethical Considerations

### Important Guidelines

1. **Respect robots.txt**: Check WeChat's robots.txt policy
2. **Rate Limiting**: Use conservative request rates
3. **Terms of Service**: Comply with WeChat's ToS
4. **Data Privacy**: Handle personal data responsibly
5. **Fair Use**: Use for research, analysis, or personal purposes only

### Best Practices
- Start with small-scale testing
- Monitor for rate limiting or blocking
- Use appropriate delays between requests
- Respect copyright and intellectual property
- Don't overwhelm servers with requests

## 🔧 Troubleshooting

### Common Issues

1. **Search Returns No Results**:
   ```python
   # Try different keywords or broader search terms
   broader_keywords = ["科技", "技术", "AI"]
   for keyword in broader_keywords:
       accounts = crawler.search_official_accounts(keyword)
       if accounts:
           break
   ```

2. **Rate Limited**:
   ```python
   # Increase delays
   GONGZHONGHAO_CONFIG['random_delay_min'] = 5
   GONGZHONGHAO_CONFIG['random_delay_max'] = 10
   ```

3. **Browser Issues**:
   ```bash
   # Update Chrome driver
   pip install --upgrade webdriver-manager
   ```

4. **Content Not Loading**:
   ```python
   # Increase timeout
   GONGZHONGHAO_CONFIG['timeout'] = 60
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose logging
crawler = WeChatOfficialAccountsCrawler(headless=False)  # See browser
```

## 📊 Examples

See `gongzhonghao_examples.py` for comprehensive examples:

- **Search tech accounts**: Find AI and technology related accounts
- **Monitor trends**: Track hot topics across accounts  
- **Industry analysis**: Compare different industry sectors
- **Content extraction**: Get full article content and statistics
- **Batch processing**: Process multiple accounts efficiently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is for educational and research purposes only. Users are responsible for ensuring compliance with applicable laws, regulations, and terms of service.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `gongzhonghao_data/logs/`
3. Open an issue with detailed error information

---

**Disclaimer**: This tool is provided for educational and research purposes only. Users must ensure their use complies with WeChat's Terms of Service and applicable laws. The authors are not responsible for any misuse of this software.