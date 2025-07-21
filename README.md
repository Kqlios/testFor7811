# WeChat Posts Crawler

A comprehensive Python web crawler for WeChat public account posts with anti-detection measures and multiple crawling strategies.

## Features

- 🔍 **Multiple Search Methods**: Search WeChat accounts via Sogou and direct post crawling
- 🛡️ **Anti-Detection**: Randomized delays, rotating user agents, and stealth browsing
- ⚡ **Async Support**: Concurrent crawling for better performance
- 📊 **Data Export**: Save results to CSV and JSON formats
- 🔧 **Configurable**: Extensive configuration options
- 📈 **Statistics**: Built-in analytics and reporting
- 🗃️ **Data Management**: Automatic backups and file compression
- 🌐 **Proxy Support**: Built-in proxy rotation support

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd wechat-crawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up environment variables:
```bash
export WECHAT_HEADLESS=true
export WECHAT_OUTPUT_DIR=./data
export WECHAT_PROXY=http://your-proxy:port
```

## Quick Start

### Basic Usage

```python
from wechat_crawler import WeChatCrawler

# Initialize crawler
crawler = WeChatCrawler(headless=True)

try:
    # Search for WeChat accounts
    accounts = crawler.search_wechat_accounts("人工智能", page=1)
    print(f"Found {len(accounts)} accounts")
    
    # Get posts from first account
    if accounts:
        posts = crawler.get_account_posts(accounts[0]['profile_link'], max_posts=5)
        
        # Get detailed content for posts
        for post in posts:
            content = crawler.get_post_content(post['link'])
            if content:
                print(f"Title: {content['title']}")
                print(f"Read count: {content['read_count']}")
        
        # Save data
        crawler.save_to_csv(posts, "wechat_posts.csv")
        crawler.save_to_json(posts, "wechat_posts.json")

finally:
    crawler.close()
```

### Context Manager Usage

```python
from wechat_crawler import WeChatCrawler

with WeChatCrawler(headless=True) as crawler:
    accounts = crawler.search_wechat_accounts("科技新闻")
    posts = crawler.get_account_posts(accounts[0]['profile_link'])
    crawler.save_to_csv(posts, "tech_news.csv")
```

### Async Crawling

```python
import asyncio
from wechat_crawler import AsyncWeChatCrawler

async def async_crawl():
    async_crawler = AsyncWeChatCrawler(max_concurrent=5)
    
    post_urls = [
        "https://mp.weixin.qq.com/s/url1",
        "https://mp.weixin.qq.com/s/url2",
        "https://mp.weixin.qq.com/s/url3",
    ]
    
    posts = await async_crawler.batch_crawl_posts(post_urls)
    return posts

# Run async crawling
posts = asyncio.run(async_crawl())
```

## Advanced Usage

### Batch Crawling

```python
keywords = ["机器学习", "深度学习", "自然语言处理"]
all_posts = []

with WeChatCrawler() as crawler:
    for keyword in keywords:
        accounts = crawler.search_wechat_accounts(keyword)
        
        for account in accounts[:3]:  # Top 3 accounts per keyword
            posts = crawler.get_account_posts(account['profile_link'], max_posts=5)
            
            # Tag posts with search keyword
            for post in posts:
                post['search_keyword'] = keyword
            
            all_posts.extend(posts)
    
    # Save all collected data
    crawler.save_to_csv(all_posts, "ai_research_posts.csv")
```

### Custom Configuration

```python
from wechat_crawler import WeChatCrawler
from config import CRAWLER_CONFIG

# Customize settings
config = CRAWLER_CONFIG.copy()
config.update({
    'max_posts_per_account': 20,
    'random_delay_min': 2,
    'random_delay_max': 5,
})

crawler = WeChatCrawler(
    headless=False,  # Show browser for debugging
    proxy="http://proxy-server:8080"  # Use proxy
)
```

### Using Utilities

```python
from utils import (
    filter_duplicate_posts,
    validate_post_data,
    create_summary_report,
    calculate_crawling_stats
)

# Remove duplicates
unique_posts = filter_duplicate_posts(posts, key='link')

# Validate data
valid_posts = [post for post in posts if validate_post_data(post)]

# Generate report
report = create_summary_report(posts, "crawling_report.txt")
print(report)

# Get statistics
stats = calculate_crawling_stats(posts)
print(f"Total posts: {stats['total_posts']}")
print(f"Date range: {stats['date_range']}")
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WECHAT_HEADLESS` | Run browser in headless mode | `true` |
| `WECHAT_OUTPUT_DIR` | Output directory for files | `./` |
| `WECHAT_PROXY` | Proxy server URL | None |

### Configuration File

Edit `config.py` to customize:

- Browser settings (headless mode, window size)
- Anti-detection measures (delays, retry attempts)
- Rate limiting and concurrent requests
- Output formats and file handling
- Proxy configuration
- Content filtering rules

### Key Configuration Options

```python
CRAWLER_CONFIG = {
    'headless': True,                    # Headless browser mode
    'timeout': 30,                       # Request timeout
    'random_delay_min': 1,               # Min delay between requests
    'random_delay_max': 3,               # Max delay between requests
    'max_concurrent_requests': 5,        # Concurrent requests limit
    'max_posts_per_account': 10,         # Posts per account
    'retry_attempts': 3,                 # Retry failed requests
}
```

## Output Formats

### CSV Output

Posts are saved with the following columns:
- `title`: Post title
- `link`: Post URL
- `author`: Account name
- `publish_date`: Publication date
- `description`: Post summary
- `content`: Full post content
- `read_count`: Number of reads
- `like_count`: Number of likes
- `images`: List of image URLs
- `crawled_at`: Timestamp when crawled

### JSON Output

Structured JSON with the same fields as CSV, preserving data types and nested structures.

## Error Handling

The crawler includes comprehensive error handling:

- **Rate Limiting**: Automatic delays and retry mechanisms
- **Anti-Detection**: Multiple strategies to avoid blocking
- **Network Errors**: Retry failed requests with exponential backoff
- **Data Validation**: Ensure data quality and completeness
- **Logging**: Detailed logs for debugging and monitoring

## Legal and Ethical Considerations

⚠️ **Important Notice**:

1. **Respect robots.txt**: Always check and respect the target site's robots.txt
2. **Rate Limiting**: Use appropriate delays to avoid overwhelming servers
3. **Terms of Service**: Ensure compliance with WeChat's Terms of Service
4. **Data Privacy**: Handle crawled data responsibly and in compliance with privacy laws
5. **Fair Use**: Use crawled data for legitimate research, analysis, or personal use only

### Best Practices

- Start with small-scale testing
- Use reasonable request intervals (1-3 seconds)
- Monitor for rate limiting or blocking
- Implement proper error handling
- Respect copyright and intellectual property rights

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   ```bash
   # Update Chrome driver
   pip install --upgrade webdriver-manager
   ```

2. **Permission Errors**:
   ```bash
   # Linux: Install Chrome
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

3. **Rate Limiting**:
   - Increase delays in configuration
   - Use proxy rotation
   - Reduce concurrent requests

4. **Element Not Found**:
   - WeChat may update their HTML structure
   - Check and update CSS selectors in `config.py`

### Debug Mode

Run with debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your crawler code here
```

## Performance Tips

1. **Use Async Crawling**: For multiple posts simultaneously
2. **Optimize Browser Settings**: Disable images and JavaScript when not needed
3. **Batch Processing**: Process multiple accounts in batches
4. **Caching**: Avoid re-crawling the same content
5. **Memory Management**: Close browser instances properly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes only. Please ensure compliance with applicable laws and regulations.

## Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs in `wechat_crawler.log`
3. Open an issue with detailed error information
4. Provide your configuration and environment details

## Changelog

### v1.0.0 (Current)
- Initial release with basic crawling functionality
- Support for account search and post extraction
- Async crawling capabilities
- Comprehensive configuration system
- Data export in multiple formats
- Anti-detection measures

---

**Disclaimer**: This tool is provided for educational and research purposes only. Users are responsible for ensuring their use complies with applicable laws, regulations, and terms of service. The authors are not responsible for any misuse of this software.
