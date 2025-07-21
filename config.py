#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Crawler Configuration
============================

Configuration settings for the WeChat crawler.
Modify these settings according to your needs.
"""

import os
from typing import Dict, List, Optional

# Crawler Settings
CRAWLER_CONFIG = {
    # Browser settings
    'headless': True,  # Run browser in headless mode
    'window_size': '1920,1080',  # Browser window size
    'timeout': 30,  # Request timeout in seconds
    
    # Anti-detection settings
    'random_delay_min': 1,  # Minimum delay between requests (seconds)
    'random_delay_max': 3,  # Maximum delay between requests (seconds)
    'retry_attempts': 3,  # Number of retry attempts for failed requests
    'retry_delay': 2,  # Delay between retry attempts (seconds)
    
    # Concurrent processing
    'max_concurrent_requests': 5,  # Max concurrent async requests
    'max_posts_per_account': 10,  # Default max posts to crawl per account
    'max_accounts_per_search': 20,  # Max accounts to process per search
    
    # Output settings
    'save_images': True,  # Whether to save image URLs
    'save_full_content': True,  # Whether to save full post content
    'output_format': 'both',  # 'csv', 'json', or 'both'
    'timestamp_format': '%Y%m%d_%H%M%S',  # Timestamp format for filenames
}

# User Agent Pool
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# WeChat API Endpoints
API_ENDPOINTS = {
    'sogou_search': 'https://weixin.sogou.com/weixin',
    'wechat_article': 'https://mp.weixin.qq.com/s/',
    'wechat_profile': 'https://mp.weixin.qq.com/profile',
    'wechat_search': 'https://mp.weixin.qq.com/cgi-bin/searchbiz',
}

# Search Keywords for Different Categories
SEARCH_KEYWORDS = {
    'technology': ['人工智能', '机器学习', '深度学习', '区块链', '物联网', '5G', '云计算'],
    'business': ['创业', '投资', '商业', '经济', '金融', '股票', '基金'],
    'education': ['教育', '学习', '考试', '培训', '技能', '知识'],
    'health': ['健康', '医疗', '养生', '运动', '营养', '心理'],
    'lifestyle': ['生活', '旅行', '美食', '时尚', '娱乐', '文化'],
    'news': ['新闻', '时事', '政治', '社会', '国际', '军事'],
}

# CSS Selectors for Different Elements
CSS_SELECTORS = {
    'account_search': {
        'results': '.results',
        'account_name': 'h3',
        'wechat_id': '.sp-wx',
        'description': '.sp-desc',
        'profile_link': 'a',
    },
    'post_list': {
        'post_cards': '.weui_msg_card',
        'title': '.weui_media_title, h4',
        'link': 'a',
        'date': '.weui_media_extra_info, .publish_time',
        'description': '.weui_media_desc, .digest',
    },
    'post_content': {
        'title': '#activity-name, h2.rich_media_title',
        'author': '#js_name, .rich_media_meta_text',
        'publish_time': '#publish_time, .rich_media_meta_text',
        'content': '#js_content',
        'read_count': '#readNum3, .read_num, [id*="read"], .media_tool_meta',
        'like_count': '#likeNum3, .like_num, [id*="like"], .praise_num',
        'images': '#js_content img',
    }
}

# Chrome Options for Different Scenarios
CHROME_OPTIONS = {
    'stealth': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--disable-javascript',  # Can be enabled if needed
    ],
    'performance': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--memory-pressure-off',
        '--disk-cache-size=0',
    ],
    'mobile': [
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
        '--window-size=375,812',
    ]
}

# Proxy Configuration
PROXY_CONFIG = {
    'enabled': False,  # Set to True to enable proxy
    'proxy_list': [
        # Add your proxy servers here
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ],
    'rotation': True,  # Rotate proxies for each request
    'timeout': 10,  # Proxy timeout in seconds
}

# Rate Limiting
RATE_LIMIT = {
    'requests_per_minute': 30,  # Max requests per minute
    'requests_per_hour': 1000,  # Max requests per hour
    'cool_down_period': 300,  # Cool down period in seconds if rate limited
}

# Data Storage Settings
STORAGE_CONFIG = {
    'data_dir': 'crawled_data',  # Directory to store output files
    'backup_dir': 'backups',  # Directory for backups
    'log_dir': 'logs',  # Directory for log files
    'create_dirs': True,  # Automatically create directories if they don't exist
    'compress_old_files': True,  # Compress files older than 7 days
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': True,  # Log to file
    'console_handler': True,  # Log to console
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,  # Keep 5 backup log files
}

# Content Filtering
CONTENT_FILTERS = {
    'min_title_length': 5,  # Minimum title length to consider valid
    'max_title_length': 200,  # Maximum title length
    'min_content_length': 50,  # Minimum content length
    'exclude_keywords': [
        '广告', '推广', '删除', '测试'
    ],  # Keywords to filter out
    'include_only': [],  # If not empty, only include posts with these keywords
}

# Email Notification (Optional)
EMAIL_CONFIG = {
    'enabled': False,  # Set to True to enable email notifications
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': '',  # Your email username
    'password': '',  # Your email password or app password
    'recipient': '',  # Email to send notifications to
    'send_on_error': True,  # Send email on errors
    'send_summary': True,  # Send daily summary
}

# Environment Variables (Override config if set)
def load_env_config():
    """Load configuration from environment variables"""
    env_config = {}
    
    # Load proxy from environment
    if os.getenv('WECHAT_PROXY'):
        env_config['proxy'] = os.getenv('WECHAT_PROXY')
    
    # Load headless mode from environment
    if os.getenv('WECHAT_HEADLESS'):
        env_config['headless'] = os.getenv('WECHAT_HEADLESS').lower() == 'true'
    
    # Load output directory from environment
    if os.getenv('WECHAT_OUTPUT_DIR'):
        env_config['output_dir'] = os.getenv('WECHAT_OUTPUT_DIR')
    
    return env_config

# Function to get configuration with environment overrides
def get_config():
    """Get final configuration with environment variable overrides"""
    config = CRAWLER_CONFIG.copy()
    env_config = load_env_config()
    config.update(env_config)
    return config

# Create necessary directories
def setup_directories():
    """Create necessary directories for the crawler"""
    if STORAGE_CONFIG['create_dirs']:
        for dir_name in [STORAGE_CONFIG['data_dir'], 
                        STORAGE_CONFIG['backup_dir'], 
                        STORAGE_CONFIG['log_dir']]:
            os.makedirs(dir_name, exist_ok=True)

# Validate configuration
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check rate limits
    if RATE_LIMIT['requests_per_minute'] > 60:
        errors.append("requests_per_minute should not exceed 60 to avoid being blocked")
    
    # Check concurrent requests
    if CRAWLER_CONFIG['max_concurrent_requests'] > 10:
        errors.append("max_concurrent_requests should not exceed 10 to avoid being blocked")
    
    # Check proxy configuration
    if PROXY_CONFIG['enabled'] and not PROXY_CONFIG['proxy_list']:
        errors.append("Proxy is enabled but no proxy servers configured")
    
    if errors:
        print("Configuration warnings:")
        for error in errors:
            print(f"  - {error}")

if __name__ == "__main__":
    # Validate and setup when run directly
    validate_config()
    setup_directories()
    print("Configuration validated and directories created.")